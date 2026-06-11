from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/evolution", tags=["Évolution"])


def get_raphael():
    from raphael.api.main import get_raphael_instance
    return get_raphael_instance()


@router.post("/run-cycle")
async def run_evolution_cycle(background_tasks: BackgroundTasks):
    """Déclenche manuellement un cycle d'évolution du réseau."""
    from raphael.evolution import EvolutionEngine
    raphael = get_raphael()

    async def _run():
        engine = EvolutionEngine(
            registry=raphael._registry,
            factory=raphael._factory,
            long_memory=raphael._long_memory,
        )
        return await engine.run_cycle()

    background_tasks.add_task(_run)
    return {"status": "Cycle d'évolution démarré en arrière-plan"}


@router.get("/status")
async def evolution_status():
    """Retourne le statut d'évolution du réseau."""
    raphael = get_raphael()
    stats = await raphael.get_network_status()
    return {
        "network_status": stats,
        "evolution": "active",
    }
