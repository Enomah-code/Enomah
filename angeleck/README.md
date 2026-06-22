# Angeleck OS — Écosystème IA Multi-Agents Autonome

**Angeleck OS** est une plateforme SaaS auto-hébergeable : une équipe virtuelle
d'agents IA capable de comprendre une demande, choisir le bon expert, exécuter
la tâche, mémoriser, apprendre et **créer de nouveaux agents** quand une
compétence manque — le tout avec des **modèles IA locaux (Ollama)**, sans
aucune dépendance à une API payante.

```
FRONTEND EXISTANT
       │
       ▼
API BACKEND (FastAPI)
       │
       ▼
CERVEAU CENTRAL — Superviseur (LangGraph)
       │
       ▼
HUB DES AGENTS (LangChain + Ollama)
       │
       ▼
MÉMOIRE (Redis court terme · ChromaDB long terme) + PostgreSQL
```

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Python + FastAPI |
| Orchestration | LangGraph |
| Agents | LangChain |
| Modèles IA | Ollama (Llama 3, Mistral, Qwen, Phi) |
| Base de données | PostgreSQL |
| Mémoire vectorielle | ChromaDB |
| Cache / court terme | Redis |
| Admin | Streamlit |
| Déploiement | Docker + Docker Compose |

## Modules

1. **Cerveau central (`app/brain`)** — comprend l'intention, détecte les
   compétences, route vers les agents, synthétise (graphe LangGraph).
2. **Hub des agents (`app/agents`)** — 5 agents initiaux :
   - **Plume** — Copywriting (pages de vente, emails, scripts, descriptions)
   - **Stratège** — Marketing & business (tunnels, acquisition, marché)
   - **Forge** — Code & automatisation (scripts, debug, outils)
   - **Vision** — Création visuelle (prompts image/vidéo, branding)
   - **Oracle** — Data analyst (CSV/Excel, stats, rapports)
3. **Recruteur automatique (`app/factory`)** — génère, teste et enregistre un
   nouvel agent quand aucune compétence existante ne couvre la demande.
4. **Mémoire (`app/memory`)** — court terme (Redis) + long terme vectorielle
   (ChromaDB) + données persistantes (PostgreSQL).
5. **API (`app/api`)** — `/chat`, `/agents`, `/memory`, `/create-agent`,
   `/upload`, `/auth/*`, `/admin/*`.
6. **Sécurité (`app/security`)** — auth JWT, hachage bcrypt, validation des
   entrées (Pydantic), limitation de débit, logs.
7. **Admin (`admin/dashboard.py`)** — console Streamlit (agents, missions,
   ressources).

## Démarrage rapide (Docker)

```bash
cd angeleck
cp .env.example .env          # changez SECRET_KEY !
docker compose up -d          # postgres + redis + ollama + backend + admin

# Télécharger les modèles dans Ollama (une seule fois)
docker compose exec ollama ollama pull llama3
docker compose exec ollama ollama pull mistral
docker compose exec ollama ollama pull qwen2.5-coder
docker compose exec ollama ollama pull nomic-embed-text
# (ou : ./scripts/pull_models.sh depuis l'hôte)
```

- API : http://localhost:8000  (docs : http://localhost:8000/docs)
- Admin : http://localhost:8501

## Démarrage en local (sans Docker)

```bash
cd angeleck/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload          # API
streamlit run admin/dashboard.py       # Admin (autre terminal)
```

> PostgreSQL, Redis et Ollama doivent tourner. Le système dégrade
> proprement (fallback mémoire locale) si Redis/Chroma sont absents.

## Parcours utilisateur de bout en bout

```bash
# 1. Créer un compte (le premier compte devient admin)
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"me@mail.com","password":"motdepasse123"}'

# 2. Envoyer une demande (récupérez access_token de l'étape 1)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"message":"Crée-moi une stratégie TikTok pour vendre mon produit"}'
# → le cerveau mobilise Stratège + Plume et synthétise.

# 3. Compétence manquante → création automatique d'agent
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"message":"Analyse mes pubs Facebook et prédis les meilleures audiences"}'
# → recrutement d'un "Facebook Ads Specialist" puis exécution.
```

## Connecter votre frontend existant

Incluez `frontend/angeleck-client.js` :

```html
<script src="angeleck-client.js"></script>
<script>
  const api = new AngeleckClient("http://localhost:8000/api/v1");
  await api.login("me@mail.com", "motdepasse123");
  const res = await api.chat("Lance une campagne pour mon SaaS B2B");
  console.log(res.response, res.missions, res.created_agents);
</script>
```

## Tests

```bash
cd angeleck/backend && pytest -q   # tests sans services externes
```

## Structure du projet

```
angeleck/
├── backend/
│   ├── app/
│   │   ├── main.py            # API FastAPI (CORS, rate limit, routes)
│   │   ├── config.py          # Paramètres (.env)
│   │   ├── runtime.py         # Noyau (assemble tout)
│   │   ├── api/routes/        # auth, chat, agents, memory, upload, admin
│   │   ├── brain/             # Cerveau central (LangGraph + intent)
│   │   ├── agents/            # BaseAgent, registre, définitions, générés/
│   │   ├── factory/           # Recruteur automatique d'agents
│   │   ├── memory/            # Court terme (Redis) + long terme (ChromaDB)
│   │   ├── database/          # SQLAlchemy (session + modèles)
│   │   ├── tools/             # Outils (web, code, data)
│   │   ├── llm/               # Client Ollama (LangChain)
│   │   ├── security/          # JWT + bcrypt
│   │   └── models/            # Schémas Pydantic
│   ├── admin/dashboard.py     # Console Streamlit
│   ├── tests/                 # Tests unitaires
│   └── requirements.txt
├── docker/backend.Dockerfile
├── frontend/angeleck-client.js
├── scripts/pull_models.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

## Production

- Changez `SECRET_KEY`, mettez `ENVIRONMENT=production`.
- Placez l'API derrière un reverse proxy (HTTPS).
- Allouez un GPU à Ollama (voir `docker-compose.yml`).
- Sauvegardez les volumes `pgdata`, `ollama`, `appdata`.
