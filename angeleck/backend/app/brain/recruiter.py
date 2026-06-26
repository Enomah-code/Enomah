"""
AGENT RECRUTEUR AUTOMATIQUE (Module 3) — la fonctionnalité signature.

Quand le cerveau détecte une compétence absente du registre, le recruteur :

  1. analyse la compétence manquante ;
  2. fait GÉNÉRER par le LLM une fiche d'agent (nom, rôle, compétences, outils,
     prompt système) au format JSON ;
  3. écrit le code Python de l'agent dans app/agents/generated/<key>.py ;
  4. teste l'agent (smoke test : instanciation + petite requête) ;
  5. l'ajoute au registre en mémoire ;
  6. le persiste en base (AgentRecord) pour le rendre disponible définitivement.

Exemple : "Analyse mes campagnes TikTok" → création d'un
"TikTok Growth Specialist Agent".
"""
from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import asdict
from typing import Optional

from app.agents.base import AgentSpec, GenericAgent
from app.agents.registry import registry
from app.config import settings
from app.models.ollama import OllamaClient
from app.tools import TOOL_REGISTRY

logger = logging.getLogger("angeleck.recruiter")

# Gabarit du fichier python produit pour chaque agent généré.
AGENT_FILE_TEMPLATE = '''"""
Agent généré automatiquement par le RECRUTEUR d'Angeleck OS.

NE PAS éditer à la main : ce fichier est produit dynamiquement.
Compétence d'origine : {origin_skill!r}
"""
from app.agents.base import AgentSpec

SPEC = AgentSpec(
    key={key!r},
    name={name!r},
    role={role!r},
    description={description!r},
    skills={skills!r},
    tools={tools!r},
    system_prompt={system_prompt!r},
    model={model!r},
    origin="generated",
)
'''


class AgentRecruiter:
    """Fabrique d'agents à la volée."""

    def __init__(self, client: Optional[OllamaClient] = None) -> None:
        self._client = client or OllamaClient()
        self._dir = settings.generated_agents_dir
        os.makedirs(self._dir, exist_ok=True)

    # ------------------------------------------------------------------ #
    async def recruit(self, missing_skill: str, original_request: str = "") -> Optional[AgentSpec]:
        """
        Crée, teste et enregistre un nouvel agent pour `missing_skill`.

        Retourne la `AgentSpec` créée, ou None en cas d'échec.
        """
        logger.info("Recrutement déclenché pour : %s", missing_skill)

        spec = await self._design_spec(missing_skill, original_request)
        if spec is None:
            logger.error("Conception de l'agent échouée.")
            return None

        # Éviter les collisions de clé.
        spec.key = self._unique_key(spec.key)

        # 3. Écrire le code du nouvel agent.
        module_path = self._write_agent_file(spec, missing_skill)

        # 4. Smoke test.
        ok = await self._smoke_test(spec)
        if not ok:
            logger.warning("Smoke test KO pour %s — agent conservé mais marqué fragile.", spec.key)

        # 5. Enregistrer en mémoire.
        registry.register_spec(spec)

        # 6. Persister en base.
        await self._persist(spec, module_path)

        logger.info("Nouvel agent recruté : %s (%s)", spec.name, spec.key)
        return spec

    # ------------------------------------------------------------------ #
    async def _design_spec(self, missing_skill: str, original_request: str) -> Optional[AgentSpec]:
        """Fait concevoir la fiche de l'agent par le LLM."""
        available_tools = ", ".join(TOOL_REGISTRY.keys())
        prompt = (
            "Tu es le RECRUTEUR d'Angeleck OS. Un utilisateur a besoin d'une "
            "compétence qu'aucun agent existant ne couvre. Conçois un nouvel "
            "agent expert spécialisé.\n\n"
            f"Compétence manquante : {missing_skill}\n"
            f"Demande d'origine : {original_request}\n"
            f"Outils disponibles que l'agent peut utiliser : {available_tools}\n\n"
            "Réponds UNIQUEMENT en JSON valide :\n"
            "{\n"
            '  "key": "identifiant_court_snake_case",\n'
            '  "name": "Nom Lisible de l\'Agent",\n'
            '  "role": "rôle en une phrase",\n'
            '  "description": "ce que fait l\'agent",\n'
            '  "skills": ["compétence1", "compétence2"],\n'
            '  "tools": ["sous-ensemble des outils disponibles"],\n'
            '  "system_prompt": "instructions système détaillées et expertes pour l\'agent"\n'
            "}\n"
            "Le system_prompt doit être professionnel, précis et orienté action."
        )
        try:
            raw = await self._client.chat(
                [{"role": "user", "content": prompt}],
                model=settings.ollama_brain_model,
                temperature=0.4,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("LLM indisponible pour la conception : %s", exc)
            return None

        data = _extract_json(raw)
        if not data or "key" not in data:
            return None

        # On filtre les outils pour ne garder que ceux réellement existants.
        tools = [t for t in data.get("tools", []) if t in TOOL_REGISTRY]
        return AgentSpec(
            key=_slugify(data["key"]),
            name=data.get("name", "Agent Généré"),
            role=data.get("role", ""),
            description=data.get("description", ""),
            skills=data.get("skills", []),
            tools=tools,
            system_prompt=data.get("system_prompt", "Tu es un agent expert d'Angeleck OS."),
            model=settings.ollama_agent_model,
            origin="generated",
        )

    def _unique_key(self, key: str) -> str:
        base = _slugify(key) or "agent"
        candidate = base
        i = 2
        while registry.exists(candidate):
            candidate = f"{base}_{i}"
            i += 1
        return candidate

    def _write_agent_file(self, spec: AgentSpec, origin_skill: str) -> str:
        """Écrit le fichier python de l'agent généré et retourne son chemin."""
        path = os.path.join(self._dir, f"{spec.key}.py")
        content = AGENT_FILE_TEMPLATE.format(origin_skill=origin_skill, **asdict(spec))
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        logger.info("Code de l'agent écrit : %s", path)
        return path

    async def _smoke_test(self, spec: AgentSpec) -> bool:
        """Instancie l'agent et lui envoie une micro-requête de validation."""
        try:
            agent = GenericAgent(spec)
            reply = await agent.run("Présente-toi en une phrase et confirme ta spécialité.")
            return bool(reply and reply.strip())
        except Exception as exc:  # noqa: BLE001
            logger.warning("Smoke test exception : %s", exc)
            return False

    async def _persist(self, spec: AgentSpec, module_path: str) -> None:
        """Enregistre l'agent dans la table `agents`."""
        try:
            from sqlalchemy import select

            from app.memory.database import AgentRecord, SessionLocal

            async with SessionLocal() as session:
                existing = await session.scalar(
                    select(AgentRecord).where(AgentRecord.key == spec.key)
                )
                if existing:
                    return
                record = AgentRecord(
                    key=spec.key,
                    name=spec.name,
                    role=spec.role,
                    description=spec.description,
                    skills=spec.skills,
                    tools=spec.tools,
                    system_prompt=spec.system_prompt,
                    model=spec.model,
                    origin="generated",
                    module_path=module_path,
                )
                session.add(record)
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            # La persistance est un bonus : l'agent reste utilisable en mémoire.
            logger.warning("Persistance DB de l'agent échouée : %s", exc)


# --------------------------------------------------------------------------- #
def _extract_json(text: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_")


# Singleton
recruiter = AgentRecruiter()
