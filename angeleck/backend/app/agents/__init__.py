"""
Agents experts d'Angeleck OS.

Expose les classes d'agents natifs et le registre dynamique.
"""
from .base import AgentSpec, BaseAgent
from .registry import AgentRegistry, registry

__all__ = ["BaseAgent", "AgentSpec", "AgentRegistry", "registry"]
