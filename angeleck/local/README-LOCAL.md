# 🛡️ Angeleck OS — Version locale simple

Une version d'Angeleck OS qui se lance **sans Docker, sans PostgreSQL, sans
ChromaDB**. Juste **Python**. Idéale pour tester rapidement sur ton PC.

Elle inclut :
- le **cerveau central** (routage automatique vers le bon agent) ;
- les **5 agents** (Copywriter, Marketing, Code, Visual, Data) ;
- le **recruteur automatique** (crée un nouvel agent si besoin) ;
- la **mémoire** (fichier SQLite local `angeleck.db`) ;
- une **interface de chat intégrée** (page web) ;
- l'**API** compatible avec ton frontend EMK Blue Diamond Studio.

Elle fonctionne avec trois moteurs au choix : **Claude API** (recommandé, le plus
puissant), **Ollama** (local gratuit), ou **mode démonstration** (sans rien).

Priorité automatique : si `ANTHROPIC_API_KEY` est définie → Claude ; sinon si
Ollama tourne → Ollama ; sinon → démonstration.

---

## ✅ Prérequis : seulement Python

1. Va sur https://www.python.org/downloads/ et installe **Python 3.10 ou plus**.
2. ⚠️ Pendant l'installation, **coche la case « Add Python to PATH »**.

(Tu as déjà Python 3.11 d'après nos échanges — donc c'est bon.)

---

## 🚀 Lancer (le plus simple)

### Sur Windows
**Double-clique sur le fichier `start.bat`.**

Il va, tout seul :
1. créer un mini environnement Python,
2. installer les 4 dépendances,
3. démarrer le serveur,
4. **ouvrir ton navigateur sur http://localhost:8000**.

La première fois prend ~1 minute (installation). Les fois suivantes : instantané.

> Si Windows affiche un avertissement « Windows a protégé votre PC » :
> clique **« Informations complémentaires » → « Exécuter quand même »**.

### Sur macOS / Linux
```bash
cd angeleck/local
chmod +x start.sh
./start.sh
```

### À la main (si les scripts ne marchent pas)
```bash
cd angeleck/local
python -m venv .venv
# Windows :
.venv\Scripts\python -m pip install -r requirements-local.txt
.venv\Scripts\python server.py
# macOS/Linux :
./.venv/bin/python -m pip install -r requirements-local.txt
./.venv/bin/python server.py
```
Puis ouvre **http://localhost:8000**.

---

## 🧠 Activer la vraie IA

Sans moteur configuré, l'app marche déjà mais répond en **mode démonstration**
(elle montre quel agent est choisi, sans générer de vrai contenu). Deux options
pour de vraies réponses :

### Option 1 — Claude API (recommandé, qualité maximale)

C'est l'option la plus puissante. Il te suffit de définir ta clé API **avant** de
lancer.

**Windows (PowerShell)** — dans le dossier `angeleck\local` :
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."   # ta clé Anthropic
.\start.bat
```

**macOS / Linux :**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
./start.sh
```

Le statut en haut de la page affichera **« Moteur : Claude API (claude-opus-4-8) 🟢 »**.

> Le modèle par défaut est `claude-opus-4-8` (le plus capable). Pour en changer :
> `set CLAUDE_MODEL=claude-sonnet-4-6` (Windows) avant de lancer.
> La dépendance `anthropic` s'installe automatiquement via `start.bat`.

### Option 2 — Ollama (local, gratuit)

Pour de vraies réponses IA **100 % gratuites et locales** :

1. Installe **Ollama** : https://ollama.com (bouton Download).
2. Ouvre un terminal et télécharge un modèle :
   ```bash
   ollama pull llama3.1
   ```
   (modèles plus légers si ton PC est modeste : `ollama pull phi3` ou `ollama pull qwen2`)
3. Recharge la page http://localhost:8000 → le statut passe en **« IA réelle »** 🟢.

> Tu peux changer le modèle utilisé via une variable d'environnement avant de lancer :
> `set OLLAMA_AGENT_MODEL=phi3` (Windows) puis relance `start.bat`.

---

## 🖥️ Utilisation

- Ouvre **http://localhost:8000**.
- Écris ta demande (ex. *« Crée une publicité Facebook pour mon produit »*).
- Le cerveau choisit le bon agent et répond.
- Demande quelque chose hors des 5 agents (ex. *« Analyse mes campagnes TikTok »*)
  → un **nouvel agent est créé automatiquement** et apparaît dans la liste de gauche.

---

## 🔌 Connecter ton frontend EMK Blue Diamond Studio

L'API tourne sur `http://localhost:8000` avec les mêmes endpoints que la version
complète :

| Méthode | Endpoint            | Rôle                       |
|---------|---------------------|----------------------------|
| POST    | `/api/chat`         | Envoyer une demande        |
| GET     | `/api/agents`       | Lister les agents          |
| POST    | `/api/create-agent` | Créer un agent             |
| POST    | `/api/upload`       | Analyser un fichier        |
| GET     | `/api/history`      | Historique                 |
| GET     | `/api/system/status`| État système               |

Dans ton frontend, appelle simplement `http://localhost:8000/api/chat`.
Le fichier `../frontend-connection-example.js` (dossier parent) contient des
exemples prêts à copier. (Cette version locale n'a pas d'authentification, pour
rester simple : enlève juste l'en-tête `Authorization` des exemples.)

---

## 🆚 Différences avec la version complète (`../backend`)

| | Version locale (ici) | Version complète (`backend/`) |
|---|---|---|
| Installation | Python seul | Docker (5 services) |
| Base de données | SQLite (fichier) | PostgreSQL |
| Mémoire longue | SQLite | ChromaDB (vectorielle) |
| Orchestration | logique intégrée | LangGraph |
| Authentification | non (simple) | oui (JWT) |
| Idéal pour | **tester vite** | **production / serveur** |

Quand tu seras à l'aise, tu pourras passer à la version complète pour le
déploiement sur un serveur.

---

## ❓ Problèmes courants

- **« Python n'est pas reconnu »** → réinstalle Python en cochant « Add to PATH ».
- **Le navigateur ne s'ouvre pas** → ouvre-le manuellement sur http://localhost:8000.
- **Port 8000 déjà utilisé** → ferme l'autre programme, ou change le port dans
  `server.py` (dernière ligne, `port=8000`).
- **Réponses en « mode démonstration »** → installe Ollama (voir plus haut).

---

Powered by **EMK Blue Diamond**.
