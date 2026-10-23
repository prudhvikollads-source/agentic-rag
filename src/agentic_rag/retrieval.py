"""BM25 retrieval implemented in pure Python — no embeddings, no network.

BM25 is a good fit for this corpus: the documents are short, factual, and
keyword-dense, and the index must be built at import time in milliseconds so
the whole system (CLI, tests, eval) runs fully offline.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .corpus import Document
from .text import content_tokens


@dataclass(frozen=True)
class RetrievedPassage:
    doc_id: str
    title: str
    text: str
    score: float


class BM25Index:
    """Classic Okapi BM25 over whole documents."""

    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = documents
        self._tokens: dict[str, list[str]] = {}
        self._tf: dict[str, dict[str, int]] = {}
        self._df: dict[str, int] = {}
        total_len = 0
        for doc in documents:
            toks = content_tokens(doc.text)
            self._tokens[doc.doc_id] = toks
            total_len += len(toks)
            freq: dict[str, int] = {}
            for tok in toks:
                freq[tok] = freq.get(tok, 0) + 1
            self._tf[doc.doc_id] = freq
            for tok in freq:
                self._df[tok] = self._df.get(tok, 0) + 1
        self._avgdl = total_len / max(len(documents), 1)
        self._n = len(documents)

    def idf(self, term: str) -> float:
        df = self._df.get(term, 0)
        return math.log(1 + (self._n - df + 0.5) / (df + 0.5))

    _idf = idf

    def score(self, query: str, doc_id: str) -> float:
        terms = set(content_tokens(query))
        freq = self._tf[doc_id]
        dl = len(self._tokens[doc_id])
        denom_norm = self.k1 * (1 - self.b + self.b * dl / self._avgdl)
        total = 0.0
        for term in terms:
            f = freq.get(term, 0)
            if f:
                total += self._idf(term) * (f * (self.k1 + 1)) / (f + denom_norm)
        return total

    def search(self, query: str, top_k: int = 3) -> list[RetrievedPassage]:
        scored = [
            RetrievedPassage(
                doc_id=doc.doc_id,
                title=doc.title,
                text=doc.body,
                score=self.score(query, doc.doc_id),
            )
            for doc in self.documents
        ]
        scored.sort(key=lambda p: (-p.score, p.doc_id))
        return [p for p in scored[:top_k] if p.score > 0]
