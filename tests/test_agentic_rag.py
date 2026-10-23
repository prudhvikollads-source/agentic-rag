"""Offline test suite for the corrective RAG system."""
from __future__ import annotations

import pytest

from agentic_rag.corpus import load_corpus
from agentic_rag.grading import check_groundedness, grade_retrieval
from agentic_rag.graph import build_default_rag
from agentic_rag.llm import MockLLM
from agentic_rag.retrieval import BM25Index


@pytest.fixture(scope="module")
def index() -> BM25Index:
    return BM25Index(load_corpus())


@pytest.fixture(scope="module")
def rag():
    return build_default_rag()


def test_corpus_has_expected_size(index):
    assert len(index.documents) >= 10


def test_retrieval_finds_right_doc_for_known_questions(index):
    cases = {
        "How long are cached query results retained in a cloud data warehouse?": "01-cloud-data-warehouse",
        "How do streaming pipelines handle late-arriving events?": "03-streaming-pipelines",
        "Why are idempotency keys used in checkout payments?": "06-ecommerce-checkout",
        "What does an OTDR measure in a fibre network?": "05-fiber-broadband-operations",
        "How does cursor pagination differ from offset pagination?": "11-api-design",
    }
    for question, expected_doc in cases.items():
        top = index.search(question, top_k=1)
        assert top, f"no results for {question!r}"
        assert top[0].doc_id == expected_doc, f"{question!r} -> {top[0].doc_id}"


def test_grader_triggers_rewrite_on_weak_query(index):
    weak_query = "How do I pay less money for computers?"
    passages = index.search(weak_query, top_k=3)
    grade = grade_retrieval(weak_query, passages, idf=index.idf)
    assert not grade.relevant, f"weak query unexpectedly graded relevant: {grade}"

    rewritten = MockLLM().rewrite_query(weak_query)
    assert rewritten != weak_query
    new_passages = index.search(rewritten, top_k=3)
    assert new_passages, "rewritten query retrieved nothing"
    assert new_passages[0].doc_id == "10-cloud-cost-optimization"
    new_grade = grade_retrieval(rewritten, new_passages, idf=index.idf)
    assert new_grade.relevant, f"rewritten query still weak: {new_grade}"


def test_groundedness_flags_fabricated_claim(index):
    passages = index.search("cached query results retained warehouse", top_k=2)
    fabricated = [
        (
            "Cached query results are retained for 90 days and are encrypted "
            "with quantum resistant hardware modules.",
            "01-cloud-data-warehouse",
        )
    ]
    report = check_groundedness(fabricated, passages)
    assert not report.grounded
    assert fabricated[0][0] in report.unsupported_claims


def test_groundedness_accepts_extractive_claim(index):
    passages = index.search("cached query results retained warehouse", top_k=2)
    supported = [
        (
            "Cached query results are retained for 24 hours, provided the "
            "underlying data has not changed.",
            "01-cloud-data-warehouse",
        )
    ]
    report = check_groundedness(supported, passages)
    assert report.grounded, report


def test_unanswerable_question_produces_abstention(rag):
    result = rag.run("What is the internal salary band for a senior platform engineer at the company?")
    assert result.abstained
    assert "Insufficient evidence" in result.answer_text
    assert result.citations == []


def test_end_to_end_answer_with_citations(rag):
    result = rag.run("What is a canary deployment?")
    assert not result.abstained
    assert result.grounded
    assert "08-cicd-practices" in result.citations
    assert "subset" in result.answer_text.lower()


def test_end_to_end_rewrite_path_answers_cost_question(rag):
    result = rag.run("How do I pay less money for computers?")
    assert not result.abstained
    assert result.rewrites >= 1
    assert "10-cloud-cost-optimization" in result.citations
