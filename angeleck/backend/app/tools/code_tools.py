"""
Outil d'exécution de code Python pour l'agent Code.

L'exécution se fait dans un sous-processus isolé avec un timeout strict,
afin de limiter les risques (pas d'accès au process principal).
Pour une production exposée, déployer ce service dans un conteneur dédié
sans accès réseau ni système de fichiers sensible.
"""
import subprocess
import sys
import tempfile

from langchain_core.tools import tool


@tool
def run_python(code: str, timeout_seconds: int = 15) -> str:
    """Exécute un script Python et renvoie sa sortie standard / erreurs.

    Args:
        code: le code Python à exécuter.
        timeout_seconds: délai maximum d'exécution (défaut 15s).
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=True
        ) as f:
            f.write(code)
            f.flush()
            proc = subprocess.run(
                [sys.executable, f.name],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        parts = []
        if out:
            parts.append(f"[stdout]\n{out}")
        if err:
            parts.append(f"[stderr]\n{err}")
        return "\n".join(parts) or "(aucune sortie)"
    except subprocess.TimeoutExpired:
        return f"Erreur: délai d'exécution dépassé ({timeout_seconds}s)."
    except Exception as e:
        return f"Erreur d'exécution: {e}"
