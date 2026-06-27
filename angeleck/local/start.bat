@echo off
REM ============================================================
REM   Angeleck OS - Lanceur local Windows (double-clic)
REM   Cree un environnement Python, installe les dependances
REM   minimales, puis demarre le serveur et ouvre le navigateur.
REM ============================================================
setlocal
cd /d "%~dp0"

echo.
echo ============================================================
echo    ANGELECK OS - Demarrage local
echo    Powered by EMK Blue Diamond
echo ============================================================
echo.

REM --- Verifier Python ---
python --version >nul 2>&1
if errorlevel 1 (
  echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
  echo Installez Python 3.10+ depuis https://www.python.org/downloads/
  echo IMPORTANT : cochez "Add Python to PATH" pendant l'installation.
  pause
  exit /b 1
)

REM --- Creer l'environnement virtuel si absent ---
if not exist ".venv" (
  echo [1/3] Creation de l'environnement Python...
  python -m venv .venv
)

REM --- Installer les dependances ---
echo [2/3] Installation des dependances (1re fois : ~1 min)...
call ".venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
call ".venv\Scripts\python.exe" -m pip install --quiet -r requirements-local.txt

REM --- Lancer le serveur + ouvrir le navigateur ---
echo [3/3] Demarrage du serveur...
echo.
echo    Ouvre automatiquement : http://localhost:8000
echo    (Pour arreter : ferme cette fenetre ou appuie Ctrl+C)
echo.
start "" http://localhost:8000
call ".venv\Scripts\python.exe" server.py

pause
