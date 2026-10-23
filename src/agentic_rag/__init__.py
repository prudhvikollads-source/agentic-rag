"""Agentic RAG: a corrective / self-RAG question-answering system."""

from .graph import CorrectiveRAG, RagResult, build_default_rag

__all__ = ["CorrectiveRAG", "RagResult", "build_default_rag"]
__version__ = "0.1.0"
