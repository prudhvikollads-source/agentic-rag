"""Corpus loading: documents are Markdown files under ``data/corpus/``.

Each file becomes one :class:`Document` whose id is the filename stem, so a
citation like ``[03-streaming-pipelines]`` can always be traced to a file on
disk that a reader can open.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str

    @property
    def body(self) -> str:
        """Document text without the leading Markdown title line."""
        lines = self.text.splitlines()
        if lines and lines[0].startswith("#"):
            lines = lines[1:]
        return "\n".join(lines).strip()


def default_corpus_dir() -> Path:
    # <repo>/data/corpus relative to this file: src/agentic_rag/corpus.py
    return Path(__file__).resolve().parents[2] / "data" / "corpus"


def load_corpus(corpus_dir: str | Path | None = None) -> list[Document]:
    directory = Path(corpus_dir) if corpus_dir else default_corpus_dir()
    docs: list[Document] = []
    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        first_line = text.splitlines()[0] if text.splitlines() else path.stem
        docs.append(
            Document(
                doc_id=path.stem,
                title=first_line.lstrip("# ").strip(),
                text=text,
            )
        )
    if not docs:
        raise FileNotFoundError(f"no .md documents found in {directory}")
    return docs
