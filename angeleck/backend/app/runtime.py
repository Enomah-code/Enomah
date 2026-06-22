"""
Noyau d'exécution d'Angeleck OS.

Assemble et conserve les composants partagés (mémoires, registre d'agents,
recruteur, superviseur) instanciés une seule fois au démarrage de l'API.
"""
from loguru import logger

from app.agents import AgentRegistry
from app.brain import Supervisor
from app.database import init_db
from app.factory import AgentRecruiter
from app.memory import LongTermMemory, ShortTermMemory


class AngeleckCore:
    def __init__(self) -> None:
        self.short_memory = ShortTermMemory()
        self.long_memory = LongTermMemory()
        self.registry: AgentRegistry | None = None
        self.recruiter: AgentRecruiter | None = None
        self.supervisor: Supervisor | None = None
        self._ready = False

    async def startup(self) -> None:
        """Initialise tous les sous-systèmes (idempotent)."""
        if self._ready:
            return
        logger.info("Démarrage du noyau Angeleck OS...")
        await init_db()
        await self.short_memory.connect()
        self.long_memory.connect()

        self.registry = AgentRegistry(self.short_memory, self.long_memory)
        await self.registry.load()

        self.recruiter = AgentRecruiter(self.registry)
        self.supervisor = Supervisor(
            self.registry, self.recruiter, self.short_memory
        )
        self._ready = True
        logger.info("Noyau Angeleck OS opérationnel.")

    @property
    def ready(self) -> bool:
        return self._ready


# Instance unique partagée par l'application FastAPI.
core = AngeleckCore()
