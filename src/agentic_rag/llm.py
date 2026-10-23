"""LLM access behind a small interface.

The default implementation, :class:`MockLLM`, is deterministic and fully
offline. It is *extractive*: it composes an answer only from sentences that
literally appear in the retrieved passages, attaching the source document id
to each sentence. That design choice is deliberate — it makes citations and
the groundedness check real and testable instead of decorative.

A real provider can be plugged in by implementing the same two methods and
selecting it through environment variables (see :func:`get_llm`); no other
part of the system needs to change.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol

from .retrieval import RetrievedPassage
from .text import content_tokens, split_sentences


@dataclass
class GeneratedAnswer:
    """An answer as a list of (sentence, source doc id) claims."""

    claims: list[tuple[str, str]] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(f"{sentence} [{doc_id}]" for sentence, doc_id in self.claims)

    @property
    def citations(self) -> list[str]:
        seen: list[str] = []
        for _, doc_id in self.claims:
            if doc_id not in seen:
                seen.append(doc_id)
        return seen


class LLM(Protocol):
    def generate(self, question: str, passages: list[RetrievedPassage]) -> GeneratedAnswer:
        ...

    def rewrite_query(self, question: str) -> str:
        ...


# Deterministic synonym / expansion map used for query rewriting. Keys are
# colloquial or vague terms a user might type; values are the vocabulary the
# corpus actually uses.
SYNONYMS: dict[str, list[str]] = {
    "cheap": ["cost", "optimisation"],
    "cheaper": ["cost", "optimisation", "discount"],
    "bill": ["cost", "billing"],
    "bills": ["cost", "billing"],
    "smaller": ["reduction", "optimisation"],
    "spending": ["cost"],
    "save": ["discount", "optimisation"],
    "savings": ["discount", "optimisation"],
    "fast": ["latency", "performance"],
    "slow": ["latency", "performance"],
    "duplicate": ["idempotency"],
    "charged": ["payment", "charge"],
    "twice": ["duplicate", "idempotency"],
    "late": ["watermark", "lateness"],
    "delayed": ["watermark", "lateness"],
    "review": ["pull", "request"],
    "stock": ["inventory"],
    "warehouse": ["inventory", "storage"],
    "fault": ["otdr", "fibre"],
    "broken": ["fault", "break"],
    "less": ["cost", "discount"],
    "pay": ["cost", "billing"],
    "money": ["cost"],
    "computers": ["compute"],
    "slice": ["slicing", "virtual", "network"],
    "index": ["indexing", "btree"],
}


class MockLLM:
    """Deterministic extractive stand-in for a generative model."""

    name = "mock-extractive"

    def rewrite_query(self, question: str) -> str:
        tokens = question.lower().split()
        expanded: list[str] = []
        for raw in tokens:
            word = raw.strip("?!.,;:")
            expanded.extend(SYNONYMS.get(word, []))
        if not expanded:
            # Fall back to emphasising the rarest-looking content words.
            expanded = content_tokens(question)[:4]
        base = " ".join(content_tokens(question))
        return f"{base} {' '.join(dict.fromkeys(expanded))}".strip()

    def generate(self, question: str, passages: list[RetrievedPassage]) -> GeneratedAnswer:
        """Compose an answer extractively from the strongest passage(s).

        Sentence ranking combines direct question overlap with a topic
        centroid: the most frequent content terms of the passage itself.
        The centroid matters because the sentence that *answers* a question
        often shares few words with it ("adds transactions and schema
        enforcement" answers "what does a lakehouse add?"), while sharing
        many words with the passage's recurring topic terms.
        """
        if not passages:
            return GeneratedAnswer()
        q_tokens = set(content_tokens(question))
        # Concentrate on the strongest evidence: passages scoring within
        # 15% of the top hit. Weaker passages are usually a different topic
        # that happens to share a word, and citing them pollutes the answer.
        eligible = [p for p in passages if p.score >= 0.85 * passages[0].score]
        scored: list[tuple[float, int, int, str, str]] = []
        for rank, passage in enumerate(eligible):
            sentences = split_sentences(passage.text)
            freq: dict[str, int] = {}
            for sentence in sentences:
                for tok in set(content_tokens(sentence)):
                    freq[tok] = freq.get(tok, 0) + 1
            topic = {t for t, _ in sorted(freq.items(), key=lambda kv: -kv[1])[:14]}
            for position, sentence in enumerate(sentences):
                s_tokens = set(content_tokens(sentence))
                if not s_tokens:
                    continue
                q_overlap = len(q_tokens & s_tokens)
                topic_overlap = len(topic & s_tokens)
                if q_overlap == 0 and topic_overlap < 3:
                    continue
                score = 3.0 * q_overlap + 1.0 * topic_overlap - 0.25 * rank
                scored.append((score, rank, position, sentence, passage.doc_id))
        scored.sort(key=lambda c: (-c[0], c[1], c[2]))
        top = scored[:5]
        # Present the chosen sentences in document order for readability.
        top.sort(key=lambda c: (c[1], c[2]))
        return GeneratedAnswer(claims=[(s, doc) for _, _, _, s, doc in top])


class EnvLLM(MockLLM):
    """Placeholder adapter for a real provider configured via environment.

    Only selected when ``AGENTIC_RAG_LLM=env`` is set. The repository ships no
    provider SDK dependency, so this adapter refuses to run rather than
    silently pretending to call a model; implement ``generate`` against your
    provider of choice to enable it.
    """

    name = "env-configured"

    def generate(self, question: str, passages: list[RetrievedPassage]) -> GeneratedAnswer:
        raise RuntimeError(
            "AGENTIC_RAG_LLM=env selected but no provider implementation is "
            "bundled. Implement EnvLLM.generate against your provider, or "
            "unset the variable to use the offline MockLLM."
        )


def get_llm() -> LLM:
    if os.environ.get("AGENTIC_RAG_LLM", "mock").lower() == "env":
        return EnvLLM()
    return MockLLM()
