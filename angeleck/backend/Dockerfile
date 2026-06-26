# ============================================================
#  Angeleck OS — Backend (FastAPI + LangGraph)
# ============================================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code

# Dépendances système (compilation de certaines libs IA / psycopg2).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python d'abord (cache de couche).
COPY requirements.txt /code/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier le code de l'application.
COPY backend/ /code/

# Dossiers runtime (uploads, agents générés).
RUN mkdir -p /code/uploads /code/app/agents/generated

EXPOSE 8000

# Démarrage de l'API.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
