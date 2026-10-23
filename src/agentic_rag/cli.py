"""Command-line entry point.

Usage::

    python -m agentic_rag "What is a canary deployment?"
    python -m agentic_rag --eval
    python -m agentic_rag --trace "How do streaming pipelines handle late data?"
"""
from __future__ import annotations

import argparse
import sys

from .evaluation import format_report, run_evaluation
from .graph import build_default_rag


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentic_rag",
        description="Corrective / self-RAG over the bundled corpus (fully offline).",
    )
    parser.add_argument("question", nargs="?", help="the question to answer")
    parser.add_argument("--eval", action="store_true", help="run the evaluation harness")
    parser.add_argument("--trace", action="store_true", help="print the graph execution trace")
    args = parser.parse_args(argv)

    if args.eval:
        print(format_report(run_evaluation()))
        return 0
    if not args.question:
        parser.print_help()
        return 2

    result = build_default_rag().run(args.question)
    print(f"Q: {result.question}")
    print(f"A: {result.answer_text}")
    if result.abstained:
        print("Citations: (none — abstained)")
    else:
        print(f"Citations: {', '.join('[' + c + ']' for c in result.citations)}")
    print(
        f" grounded={result.grounded} rewrites={result.rewrites} "
        f"generations={result.generations} abstained={result.abstained}"
    )
    if args.trace:
        print("Trace:")
        for step in result.trace:
            print(f"  - {step}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
