"""The corrective RAG graph.

Implemented as a small explicit state machine whose nodes and transitions
mirror a LangGraph ``StateGraph`` one-to-one (same node names, same
conditional edges), so it can be lifted onto LangGraph mechanically. The
hand-rolled runner is the shipped implementation: it has zero third-party
dependencies, which keeps the repo runnable fully offline (see README
"Design decisions").

Flow::

    retrieve -> grade_retrieval --weak--> rewrite_query -> retrieve (loop)
                               --ok----> generate -> check_groundedness
                                                          |-- grounded -> END
                                                          |-- ungrounded -> regenerate (once)
                                                          |                 -> still bad -> abstain
    (retrieval still weak after max rewrites) ----------------> abstain
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .grading import check_groundedness, grade_retrieval
from .llm import LLM, GeneratedAnswer, get_llm
from .retrieval import BM25Index, RetrievedPassage

MAX_REWRITES = 2
MAX_GENERATIONS = 2
ABSTAIN_TEXT = (
    "Insufficient evidence: the bundled corpus does not contain enough "
    "relevant, verifiable material to answer this question."
)


@dataclass
class RagState:
    question: str
    query: str = ""
    passages: list[RetrievedPassage] = field(default_factory=list)
    grade_reason: str = ""
    rewrites: int = 0
    generations: int = 0
    answer: GeneratedAnswer | None = None
    grounded: bool = False
    unsupported: list[str] = field(default_factory=list)
    abstained: bool = False
    trace: list[str] = field(default_factory=list)


@dataclass
class RagResult:
    question: str
    answer_text: str
    citations: list[str]
    abstained: bool
    rewrites: int
    generations: int
    grounded: bool
    trace: list[str]
    passages: list[RetrievedPassage]


class CorrectiveRAG:
    def __init__(self, index: BM25Index, llm: LLM | None = None, top_k: int = 3):
        self.index = index
        self.llm = llm or get_llm()
        self.top_k = top_k

    # -- nodes ---------------------------------------------------------
    def _node_retrieve(self, state: RagState) -> None:
        state.passages = self.index.search(state.query, top_k=self.top_k)
        state.trace.append(
            f"retrieve(query={state.query!r}) -> "
            f"{[(p.doc_id, round(p.score, 2)) for p in state.passages]}"
        )

    def _node_grade(self, state: RagState) -> bool:
        grade = grade_retrieval(state.query, state.passages, idf=self.index.idf)
        state.grade_reason = grade.reason
        state.trace.append(f"grade_retrieval: relevant={grade.relevant} ({grade.reason})")
        return grade.relevant

    def _node_rewrite(self, state: RagState) -> None:
        state.query = self.llm.rewrite_query(state.question)
        state.rewrites += 1
        state.trace.append(f"rewrite_query #{state.rewrites}: {state.query!r}")

    def _node_generate(self, state: RagState) -> None:
        state.answer = self.llm.generate(state.question, state.passages)
        state.generations += 1
        state.trace.append(f"generate #{state.generations}: {len(state.answer.claims)} claims")

    def _node_check_groundedness(self, state: RagState) -> bool:
        assert state.answer is not None
        report = check_groundedness(state.answer.claims, state.passages)
        state.grounded = report.grounded
        state.unsupported = report.unsupported_claims
        state.trace.append(
            f"check_groundedness: grounded={report.grounded} "
            f"support={[round(r, 2) for r in report.support_ratios]}"
        )
        return report.grounded

    def _node_abstain(self, state: RagState) -> None:
        state.abstained = True
        state.trace.append("abstain: insufficient evidence")

    # -- runner --------------------------------------------------------
    def run(self, question: str) -> RagResult:
        state = RagState(question=question, query=question)
        while True:
            self._node_retrieve(state)
            if self._node_grade(state):
                break
            if state.rewrites >= MAX_REWRITES:
                self._node_abstain(state)
                return self._result(state)
            self._node_rewrite(state)

        while True:
            self._node_generate(state)
            if self._node_check_groundedness(state):
                break
            if state.generations >= MAX_GENERATIONS:
                self._node_abstain(state)
                return self._result(state)
            # Regeneration strategy for the extractive model: drop the
            # weakest passage and regenerate from the remaining evidence,
            # which removes the sentences that failed the check.
            if len(state.passages) > 1:
                state.passages = state.passages[:-1]
                state.trace.append("regenerate: dropped weakest passage")

        return self._result(state)

    def _result(self, state: RagState) -> RagResult:
        if state.abstained or state.answer is None or not state.answer.claims:
            return RagResult(
                question=state.question,
                answer_text=ABSTAIN_TEXT,
                citations=[],
                abstained=True,
                rewrites=state.rewrites,
                generations=state.generations,
                grounded=False,
                trace=state.trace,
                passages=state.passages,
            )
        return RagResult(
            question=state.question,
            answer_text=state.answer.text,
            citations=state.answer.citations,
            abstained=False,
            rewrites=state.rewrites,
            generations=state.generations,
            grounded=state.grounded,
            trace=state.trace,
            passages=state.passages,
        )


def build_default_rag() -> CorrectiveRAG:
    from .corpus import load_corpus

    return CorrectiveRAG(BM25Index(load_corpus()))
