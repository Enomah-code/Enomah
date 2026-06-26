"""VISUAL AGENT — prompts images/vidéos et branding."""
from __future__ import annotations

from app.agents.base import AgentSpec, BaseAgent

VISUAL_SPEC = AgentSpec(
    key="visual",
    name="Visual Agent",
    role="Directeur artistique — prompts visuels et identité de marque",
    description=(
        "Crée des prompts d'images et de vidéos détaillés et des chartes de "
        "branding cohérentes."
    ),
    skills=[
        "prompts images",
        "prompts vidéos",
        "branding",
        "direction artistique",
    ],
    tools=[],
    model="",
    system_prompt=(
        "Tu es le VISUAL AGENT d'Angeleck OS, directeur artistique et expert en "
        "génération visuelle. Pour les prompts image/vidéo, décris précisément : "
        "sujet, composition, style, éclairage, palette, objectif/ambiance, ratio "
        "et paramètres techniques. Fournis une version courte et une version "
        "détaillée. Pour le branding, propose nom, valeurs, palette (codes hex), "
        "typographies et ton de marque. Sois visuel et spécifique."
    ),
)


class VisualAgent(BaseAgent):
    def __init__(self, client=None):
        super().__init__(spec=VISUAL_SPEC, client=client)
