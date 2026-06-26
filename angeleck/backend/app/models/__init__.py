"""Couche modèles IA — abstraction des LLM (Ollama local)."""
from .ollama import OllamaClient, get_llm, list_available_models

__all__ = ["OllamaClient", "get_llm", "list_available_models"]
