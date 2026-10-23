"""Retrieval grading and groundedness (hallucination) checking.

Both checks are lexical and deterministic, which is what makes them testable
offline:

* The **retrieval grader** asks whether the retrieved passages actually cover
  the question's content terms and whether the best BM25 score clears a
  floor. A weak grade routes the graph into the query-rewrite loop.
* The **groundedness checker** verifies, claim by claim, that the content
  tokens of each generated sentence are supported by the retrieved passages.
  A claim whose numbers or terms appear nowhere in the evidence is flagged.
"""
from __future__ import annotations

from dataclasses import dataclass

from .retrieval import RetrievedPassage
from .text import content_tokens

# Tuned against the bundled corpus: correct top hits score well above this,
# while off-topic questions score near zero.
MIN_TOP_SCORE = 2.0
MIN_TERM_COVERAGE = 0.34
GROUNDING_SUPPORT_RATIO = 0.6


@dataclass
class RetrievalGrade:
    relevant: bool
    top_score: float
    term_coverage: float
    reason: str


@dataclass
class GroundednessReport:
    grounded: bool
    unsupported_claims: list[str]
    support_ratios: list[float]


# Terms with an idf at or above this value occur in at most ~2 of the 12
# corpus documents. They are the *distinctive* terms of a question — the
# specific fact being asked about — so a retrieval that misses most of them
# is weak even when generic topical terms match well. This is what stops a
# question about an unrecorded statistic (its distinctive terms appear
# nowhere) from being graded relevant just because it mentions "checkout".
RARE_IDF_FLOOR = 1.6
MIN_RARE_COVERAGE = 0.5


def grade_retrieval(
    question: str,
    passages: list[RetrievedPassage],
    idf=None,
) -> RetrievalGrade:
    if not passages:
        return RetrievalGrade(False, 0.0, 0.0, "no passages retrieved")
    q_terms = set(content_tokens(question))
    if not q_terms:
        return RetrievalGrade(False, passages[0].score, 0.0, "question has no content terms")
    covered: set[str] = set()
    for passage in passages:
        covered |= q_terms & set(content_tokens(passage.text))
    coverage = len(covered) / len(q_terms)
    top = passages[0].score
    relevant = top >= MIN_TOP_SCORE and coverage >= MIN_TERM_COVERAGE
    reason = (
        f"top_score={top:.2f} (floor {MIN_TOP_SCORE}), "
        f"term_coverage={coverage:.2f} (floor {MIN_TERM_COVERAGE})"
    )
    if idf is not None:
        rare = {t for t in q_terms if idf(t) >= RARE_IDF_FLOOR}
        if rare:
            rare_coverage = len(rare & covered) / len(rare)
            reason += f", rare_term_coverage={rare_coverage:.2f} (floor {MIN_RARE_COVERAGE})"
            relevant = relevant and rare_coverage >= MIN_RARE_COVERAGE
    return RetrievalGrade(relevant, top, coverage, reason)


def _numbers(text: str) -> set[str]:
    return {t for t in content_tokens(text) if any(ch.isdigit() for ch in t)}


def check_groundedness(answer_claims: list[tuple[str, str]], passages: list[RetrievedPassage]) -> GroundednessReport:
    evidence_text = " ".join(p.text for p in passages)
    evidence_tokens = set(content_tokens(evidence_text))
    evidence_numbers = _numbers(evidence_text)
    unsupported: list[str] = []
    ratios: list[float] = []
    for sentence, _doc_id in answer_claims:
        tokens = set(content_tokens(sentence))
        if not tokens:
            ratios.append(1.0)
            continue
        supported = tokens & evidence_tokens
        ratio = len(supported) / len(tokens)
        ratios.append(ratio)
        numbers_ok = _numbers(sentence) <= evidence_numbers
        if ratio < GROUNDING_SUPPORT_RATIO or not numbers_ok:
            unsupported.append(sentence)
    return GroundednessReport(
        grounded=not unsupported,
        unsupported_claims=unsupported,
        support_ratios=ratios,
    )
