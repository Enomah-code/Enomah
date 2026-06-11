#!/usr/bin/env python3
"""
Raphaël AI Network — Point d'entrée principal.
Modes: API (FastAPI), CLI interactif, ou module Python.
"""
import asyncio
import sys
from pathlib import Path

# Configure le logging avant tout
from loguru import logger
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
Path("logs").mkdir(exist_ok=True)
logger.add("logs/raphael.log", rotation="10 MB", retention="30 days", level="DEBUG")


def start_api():
    """Démarre le serveur FastAPI."""
    import uvicorn
    from raphael.api.main import create_app
    from raphael.config import get_settings

    settings = get_settings()
    app = create_app()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=settings.api_debug,
    )


async def start_cli():
    """Démarre le mode CLI interactif."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from raphael.core.orchestrator import Raphael

    console = Console()

    console.print(Panel.fit(
        "[bold blue]Raphaël AI Network v1.0[/bold blue]\n"
        "[dim]Réseau d'agents IA interconnectés et auto-évolutifs[/dim]\n"
        "[dim]Tapez 'exit' ou Ctrl+C pour quitter | '/status' pour le statut du réseau[/dim]",
        border_style="blue",
    ))

    raphael = Raphael()
    with console.status("[bold green]Initialisation du réseau Raphaël...[/bold green]"):
        await raphael.initialize()

    console.print("[bold green]Réseau opérationnel! Comment puis-je vous aider?[/bold green]\n")

    session_id = "cli_session"

    while True:
        try:
            user_input = console.input("[bold cyan]Vous:[/bold cyan] ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "quitter", "bye"):
                console.print("[dim]Au revoir! Le réseau Raphaël reste à votre service.[/dim]")
                break
            if user_input == "/status":
                status = await raphael.get_network_status()
                console.print(Panel(
                    f"[bold]Agents actifs:[/bold] {status['active_agents']}/{status['total_agents']}\n"
                    f"[bold]Tâches traitées:[/bold] {status['total_tasks_processed']}\n" +
                    "\n".join(
                        f"  • {a['name']}: {a['tasks']} tâches | succès: {a['success_rate']:.1%}"
                        for a in status['agents']
                    ),
                    title="Statut du Réseau Raphaël",
                    border_style="green",
                ))
                continue

            with console.status("[bold yellow]Raphaël réfléchit...[/bold yellow]"):
                response = await raphael.chat(user_input, session_id=session_id)

            console.print(f"\n[bold purple]Raphaël:[/bold purple]")
            console.print(Markdown(response))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Interruption. Au revoir![/dim]")
            break
        except Exception as e:
            console.print(f"[red]Erreur: {e}[/red]")
            logger.exception(e)


async def run_single_task(task: str):
    """Exécute une tâche unique depuis la ligne de commande."""
    from raphael.core.orchestrator import Raphael
    raphael = Raphael()
    await raphael.initialize()
    response = await raphael.chat(task)
    print(response)


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "api":
        start_api()
    elif sys.argv[1] == "cli":
        asyncio.run(start_cli())
    elif sys.argv[1] == "task" and len(sys.argv) > 2:
        task = " ".join(sys.argv[2:])
        asyncio.run(run_single_task(task))
    else:
        print("Usage:")
        print("  python main.py api          # Démarre l'API FastAPI")
        print("  python main.py cli          # Mode CLI interactif")
        print("  python main.py task <text>  # Exécute une tâche unique")
        sys.exit(1)


if __name__ == "__main__":
    main()
