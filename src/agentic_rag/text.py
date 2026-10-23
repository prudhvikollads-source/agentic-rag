"""Small text utilities shared by retrieval, grading and groundedness checks."""
from __future__ import annotations

import re

STOPWORDS = frozenset(
    """
    a an the is are was were be been being what how why when where which who
    does do did can could should would will shall may might in on at of for
    to from by with and or but if then than it its this that these those as
    into about between through during before after above below under over
    """.split()
)

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _stem(word: str) -> str:
    """Very light suffix stemmer so 'adds'/'add', 'retained'/'retain' match.

    Deliberately crude: it is applied identically at index and query time,
    so consistency matters more than linguistic perfection.
    """
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    if len(word) > 3 and word.endswith("es"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def content_tokens(text: str) -> list[str]:
    """Tokens with stopwords removed — the unit every score in this repo uses."""
    return [_stem(t) for t in tokenize(text) if t not in STOPWORDS]


def split_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in _SENTENCE_RE.split(text.replace("\n", " "))]
    return [p for p in parts if len(p) > 15]
