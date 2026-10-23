"""The fixed evaluation question set.

``gold_terms`` are terms a correct answer must contain (case-insensitive
containment). ``expected_sources`` are the document ids a well-behaved
system should cite. Questions with ``answerable=False`` have no supporting
document in the corpus by construction — the correct behaviour is to
abstain, and any confident answer counts as a failure.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalQuestion:
    qid: str
    question: str
    gold_terms: tuple[str, ...]
    expected_sources: tuple[str, ...]
    answerable: bool = True


EVAL_QUESTIONS: list[EvalQuestion] = [
    EvalQuestion(
        "q01",
        "How does a cloud data warehouse separate storage and compute?",
        ("separate", "storage", "compute"),
        ("01-cloud-data-warehouse",),
    ),
    EvalQuestion(
        "q02",
        "How long are cached query results retained in a cloud data warehouse?",
        ("24 hours",),
        ("01-cloud-data-warehouse",),
    ),
    EvalQuestion(
        "q03",
        "What does a data lakehouse add on top of a data lake?",
        ("transactions", "schema enforcement"),
        ("02-data-lakehouse",),
    ),
    EvalQuestion(
        "q04",
        "How do streaming pipelines handle late-arriving events?",
        ("watermark",),
        ("03-streaming-pipelines",),
    ),
    EvalQuestion(
        "q05",
        "What is network slicing used for in 5G?",
        ("virtual network", "slice"),
        ("04-telecom-5g-network",),
    ),
    EvalQuestion(
        "q06",
        "What does an OTDR measure in a fibre network?",
        ("distance", "fault"),
        ("05-fiber-broadband-operations",),
    ),
    EvalQuestion(
        "q07",
        "Why are idempotency keys used in checkout payment requests?",
        ("duplicate",),
        ("06-ecommerce-checkout",),
    ),
    EvalQuestion(
        "q08",
        "What is safety stock in inventory management?",
        ("buffer", "uncertainty"),
        ("07-ecommerce-inventory",),
    ),
    EvalQuestion(
        "q09",
        "What is a canary deployment?",
        ("subset", "traffic"),
        ("08-cicd-practices",),
    ),
    EvalQuestion(
        "q10",
        "How large should a pull request be for an effective code review?",
        ("400 lines",),
        ("09-code-review",),
    ),
    EvalQuestion(
        "q11",
        "How does reserved capacity pricing differ from on-demand pricing in cloud cost optimisation?",
        ("commit", "discount"),
        ("10-cloud-cost-optimization",),
    ),
    # --- unanswerable: correct behaviour is to abstain -----------------
    EvalQuestion(
        "q12",
        "What is the internal salary band for a senior platform engineer at the company?",
        (),
        (),
        answerable=False,
    ),
    EvalQuestion(
        "q13",
        "How do quantum computers use Shor's algorithm to factor large prime numbers?",
        (),
        (),
        answerable=False,
    ),
    EvalQuestion(
        "q14",
        "What was the exact checkout conversion rate of the online store in March 2019?",
        (),
        (),
        answerable=False,
    ),
]
