# 🛡️ Angeleck OS — Backend

> Système d'intelligence artificielle **autonome et auto-évolutif** : un cerveau
> central qui comprend, route, exécute et **recrute lui-même de nouveaux agents**,
> avec une **mémoire persistante**.
>
> **Powered by EMK Blue Diamond** — moteur backend du frontend *EMK Blue Diamond Studio*.

---

## ✨ Ce que fait Angeleck OS

L'utilisateur écrit une demande en langage naturel (« Crée une publicité Facebook
pour mon produit », « Analyse mes campagnes TikTok », « Écris un script vidéo »…).
Le **cerveau central** :

1. comprend l'objectif,
2. identifie la compétence nécessaire,
3. **sélectionne le meilleur agent** (ou plusieurs),
4. **en crée un nouveau** si la compétence n'existe pas encore,
5. exécute la mission et synthétise la réponse,
6. **mémorise** le résultat pour s'améliorer.

---

## 🏗️ Architecture

```
   FRONTEND EXISTANT  (EMK Blue Diamond Studio)
            │  HTTPS / JSON
            ▼
   ┌───────────────────────────┐
   │      API ANGELECK         │   FastAPI  (app/api/routes.py)
   └───────────┬───────────────┘
               ▼
   ┌───────────────────────────┐
   │     CERVEAU CENTRAL       │   LangGraph (app/brain/supervisor.py)
   │  analyze → recruit →      │
   │  execute → synthesize →   │
   │  remember                 │
   └───────────┬───────────────┘
               ▼
   ┌───────────────────────────┐
   │    REGISTRE DES AGENTS    │   (app/agents/registry.py)
   └───────────┬───────────────┘
               ▼
   ┌───────────────────────────┐
   │      AGENTS EXPERTS       │   Writer · Marketing · Code · Visual · Data
   │   (+ agents générés)      │   (app/agents/…)
   └───────────┬───────────────┘
               ▼
   ┌───────────────────────────┐
   │     MÉMOIRE LONG TERME    │   ChromaDB (app/memory/vector_memory.py)
   │     + PostgreSQL          │   (app/memory/database.py)
   └───────────────────────────┘
```

### Stack technique

| Couche            | Technologie                                  |
|-------------------|----------------------------------------------|
| Backend API       | **Python FastAPI**                           |
| Orchestration IA  | **LangGraph**                                |
| Agents            | **LangChain**                                |
| Modèles IA        | **Ollama local** (Llama, Mistral, Qwen, Phi) |
| Base principale   | **PostgreSQL** (SQLAlchemy async)            |
| Mémoire IA        | **ChromaDB**                                 |
| Interface admin   | **Streamlit**                                |
| Déploiement       | **Docker / docker-compose**                  |

---

## 📁 Structure du projet

```
angeleck/
├── docker-compose.yml          # Orchestration complète (5 services)
├── requirements.txt
├── .env.example
├── frontend-connection-example.js   # Client JS pour le frontend (Module 7)
└── backend/
    ├── Dockerfile
    ├── Dockerfile.admin
    ├── admin/
    │   └── dashboard.py        # Module 8 — tableau de contrôle Streamlit
    ├── scripts/
    │   └── seed_admin.py       # Création du compte admin initial
    └── app/
        ├── main.py             # Point d'entrée FastAPI
        ├── config.py           # Configuration (env)
        ├── api/
        │   └── routes.py       # Module 5 — endpoints frontend
        ├── auth/
        │   └── security.py     # Module 6 — JWT, users, sessions
        ├── brain/
        │   ├── supervisor.py   # Module 1 — cerveau central (LangGraph)
        │   ├── router.py       # Aiguillage vers les agents
        │   └── recruiter.py    # Module 3 — création auto d'agents
        ├── agents/
        │   ├── base.py         # Classe de base + AgentSpec
        │   ├── registry.py     # Registre des agents
        │   ├── writer.py       # Module 2 — Copywriter
        │   ├── marketing.py    # Module 2 — Marketing
        │   ├── code.py         # Module 2 — Code
        │   ├── visual.py       # Module 2 — Visual
        │   ├── data.py         # Module 2 — Data
        │   └── generated/      # Agents créés dynamiquement
        ├── memory/
        │   ├── database.py     # Module 4 — PostgreSQL (court terme)
        │   └── vector_memory.py# Module 4 — ChromaDB (long terme)
        ├── models/
        │   └── ollama.py       # Accès aux modèles locaux
        └── tools/
            ├── file_reader.py
            ├── web_tools.py
            └── analysis_tools.py
```

---

## 🚀 Lancer le système localement

### Option A — Tout en Docker (recommandé)

Prérequis : **Docker** + **Docker Compose**.

```bash
cd angeleck
cp .env.example .env            # adaptez si besoin

# 1. Démarrer tous les services (postgres, chroma, ollama, backend, admin)
docker compose up --build -d

# 2. Télécharger au moins un modèle dans Ollama
docker compose exec ollama ollama pull llama3.1
docker compose exec ollama ollama pull mistral

# 3. Créer le compte administrateur
docker compose exec backend python -m scripts.seed_admin
```

Services disponibles :
- **API** : http://localhost:8000  · documentation interactive : http://localhost:8000/docs
- **Admin (Streamlit)** : http://localhost:8501
- **Ollama** : http://localhost:11434
- **PostgreSQL** : localhost:5432 · **ChromaDB** : localhost:8001

### Option B — En local sans Docker (dev)

Prérequis : Python 3.11+, PostgreSQL, [Ollama](https://ollama.com), (ChromaDB optionnel).

```bash
cd angeleck/backend
python -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt

# Variables d'environnement (pointez sur vos services locaux)
export POSTGRES_HOST=localhost CHROMA_HOST=localhost CHROMA_PORT=8001
export OLLAMA_BASE_URL=http://localhost:11434

# Ollama
ollama pull llama3.1 && ollama pull mistral

# Lancer l'API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Dans un autre terminal : l'admin
streamlit run admin/dashboard.py
```

> 💡 **Résilience** : si ChromaDB ou langgraph/langchain ne sont pas disponibles,
> le système bascule automatiquement sur un mode dégradé fonctionnel
> (mémoire longue désactivée, orchestrateur linéaire). Seul **Ollava** est
> indispensable pour que les agents génèrent des réponses.

---

## 🔌 Connecter le frontend (Module 7)

Le backend expose une **couche API propre** ; **le frontend n'a pas besoin
d'être modifié dans son design**. Il suffit d'appeler ces endpoints :

| Méthode | Endpoint               | Rôle                                  |
|---------|------------------------|---------------------------------------|
| POST    | `/api/auth/register`   | Créer un compte                       |
| POST    | `/api/auth/login`      | Obtenir un token JWT                  |
| POST    | `/api/chat`            | Envoyer une demande au cerveau        |
| GET     | `/api/agents`          | Lister les agents                     |
| POST    | `/api/create-agent`    | Créer un agent dynamiquement          |
| POST    | `/api/upload`          | Analyser un fichier                   |
| GET     | `/api/history`         | Historique des conversations          |
| GET     | `/api/system/status`   | État système                          |

**Étapes :**

1. Configurez l'URL de l'API dans votre frontend (voir `frontend-connection-example.js`).
2. Réglez `CORS_ORIGINS` dans `.env` sur l'URL exacte de votre frontend en prod
   (ex. `CORS_ORIGINS=https://studio.emk-blue-diamond.com`).
3. Le client JS fourni (`frontend-connection-example.js`) contient des fonctions
   prêtes à copier : `login()`, `chat()`, `listAgents()`, `createAgent()`,
   `uploadFile()`, `getHistory()`.

Exemple :

```js
await login("admin@angeleck.os", "changeme123");
const reply = await chat("Crée une publicité Facebook pour mon produit");
console.log(reply.answer, reply.agents_used); // → ["writer", "marketing"]
```

---

## 🧠 Les modules

| Module | Description                              | Fichiers clés                         |
|--------|------------------------------------------|---------------------------------------|
| **1**  | Cerveau central (superviseur LangGraph)  | `brain/supervisor.py`, `brain/router.py` |
| **2**  | 5 agents natifs                          | `agents/{writer,marketing,code,visual,data}.py` |
| **3**  | Recruteur automatique d'agents           | `brain/recruiter.py`                  |
| **4**  | Mémoire courte + longue                  | `memory/database.py`, `memory/vector_memory.py` |
| **5**  | API frontend                             | `api/routes.py`                       |
| **6**  | Authentification & logs                  | `auth/security.py`, table `task_logs` |
| **7**  | Connexion frontend (CORS + client)       | `main.py`, `frontend-connection-example.js` |
| **8**  | Interface admin                          | `admin/dashboard.py`                  |

### Comment fonctionne le recrutement automatique (Module 3)

```
Demande : "Analyse mes campagnes TikTok"
   │
   ▼  le routeur ne trouve aucun agent adapté
   ▼  needs_new_agent = true
   ▼
RECRUTEUR :
   1. analyse la compétence manquante
   2. le LLM conçoit la fiche (nom, rôle, compétences, outils, prompt système)
   3. écrit app/agents/generated/tiktok_growth_specialist.py
   4. smoke-test de l'agent
   5. ajout au registre (mémoire)
   6. persistance en base → disponible définitivement
   ▼
Nouvel agent : "TikTok Growth Specialist Agent" ✅
```

---

## 🌐 Déployer sur un serveur

### VPS / serveur dédié (Docker)

```bash
# Sur le serveur (Ubuntu) — installer Docker
curl -fsSL https://get.docker.com | sh

# Récupérer le projet
git clone <votre-repo> && cd angeleck

# Configurer la production
cp .env.example .env
#   - SECRET_KEY=<openssl rand -hex 32>
#   - CORS_ORIGINS=https://votre-frontend.com
#   - mots de passe Postgres robustes

docker compose up --build -d
docker compose exec ollama ollama pull llama3.1
docker compose exec backend python -m scripts.seed_admin
```

Recommandations production :
- Placez un **reverse proxy** (Nginx / Caddy / Traefik) devant le backend avec
  **HTTPS** (Let's Encrypt).
- Exposez uniquement le port 443 ; gardez Postgres/Chroma/Ollama sur le réseau interne.
- Pour de meilleures performances LLM, utilisez un serveur **avec GPU** et
  décommentez la section `deploy.resources` du service `ollama`.
- Mettez en place des **sauvegardes** des volumes `pgdata` et `chromadata`.
- Changez impérativement `SECRET_KEY` et les mots de passe par défaut.

### Exemple de bloc Nginx

```nginx
server {
    server_name api.votre-domaine.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## ✅ Vérification rapide

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/system/status
```

Puis ouvrez la doc interactive **http://localhost:8000/docs** pour tester chaque
endpoint, ou l'**admin http://localhost:8501**.

---

## 📜 Licence

Projet propriétaire — **EMK Blue Diamond**. Tous droits réservés.
