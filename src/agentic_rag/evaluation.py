"""Offline evaluation harness.

Metrics, per question and in aggregate:

* **answer containment** — fraction of gold terms present in the answer.
* **citation precision** — of the documents the system cited, the fraction
  that are expected sources for that question.
* **abstention accuracy** — for unanswerable questions, whether the system
  abstained; for answerable ones, whether it (correctly) did not.
"""
from __future__ import annotations

from dataclasses import dataclass

from .graph import CorrectiveRAG, build_default_rag
from .questions import EVAL_QUESTIONS, EvalQuestion


@dataclass
class QuestionResult:
    question: EvalQuestion
    answer_text: str
    citations: list[str]
    abstained: bool
    containment: float | None  # None for unanswerable questions
    citation_precision: float | None
    abstention_correct: bool


def evaluate_question(rag: CorrectiveRAG, eq: EvalQuestion) -> QuestionResult:
    result = rag.run(eq.question)
    if eq.answerable:
        lowered = result.answer_text.lower()
        hits = sum(1 for term in eq.gold_terms if term.lower() in lowered)
        containment = hits / len(eq.gold_terms) if eq.gold_terms else 0.0
        if result.citations:
            good = sum(1 for c in result.citations if c in eq.expected_sources)
            precision: float | None = good / len(result.citations)
        else:
            precision = 0.0
    else:
        containment = None
        precision = None
    return QuestionResult(
        question=eq,
        answer_text=result.answer_text,
        citations=result.citations,
        abstained=result.abstained,
        containment=containment,
        citation_precision=precision,
        abstention_correct=(result.abstained == (not eq.answerable)),
    )


def run_evaluation(rag: CorrectiveRAG | None = None) -> list[QuestionResult]:
    rag = rag or build_default_rag()
    return [evaluate_question(rag, eq) for eq in EVAL_QUESTIONS]


def format_report(results: list[QuestionResult]) -> str:
    lines = ["=" * 78, "Agentic RAG — evaluation report", "=" * 78]
    for r in results:
        eq = r.question
        if eq.answerable:
            status = (
                "PASS"
                if (r.containment or 0) >= 0.5 and (r.citation_precision or 0) >= 0.5 and not r.abstained
                else "FAIL"
            )
            lines.append(
                f"[{status}] {eq.qid} containment={r.containment:.2f} "
                f"citation_precision={r.citation_precision:.2f} "
                f"abstained={r.abstained} :: {eq.question}"
            )
            lines.append(f"       cited: {', '.join(r.citations) or '(none)'}")
        else:
            status = "PASS" if r.abstention_correct else "FAIL"
            lines.append(
                f"[{status}] {eq.qid} unanswerable -> abstained={r.abstained} "
                f"(expected abstention) :: {eq.question}"
            )
    answerable = [r for r in results if r.question.answerable]
    unanswerable = [r for r in results if not r.question.answerable]
    mean_containment = sum(r.containment or 0 for r in answerable) / len(answerable)
    mean_precision = sum(r.citation_precision or 0 for r in answerable) / len(answerable)
    abstention_acc = sum(1 for r in results if r.abstention_correct) / len(results)
    unans_acc = (
        sum(1 for r in unanswerable if r.abstention_correct) / len(unanswerable)
        if unanswerable
        else 0.0
    )
    lines += [
        "-" * 78,
        f"Questions: {len(results)} ({len(answerable)} answerable, {len(unanswerable)} unanswerable)",
        f"Mean answer containment (answerable):      {mean_containment:.3f}",
        f"Mean citation precision (answerable):      {mean_precision:.3f}",
        f"Abstention accuracy (all questions):       {abstention_acc:.3f}",
        f"Abstention accuracy (unanswerable only):   {unans_acc:.3f}",
        "=" * 78,
    ]
    return "\n".join(lines)
