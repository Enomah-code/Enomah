# Raphaël — Réseau d'Agents IA Interconnectés & Auto-Évolutifs

**Raphaël** est un réseau d'agents IA de niveau Dieu, orchestré par un agent central qui comprend, délègue, coordonne et synthétise — comme un médecin généraliste qui réfère ses patients aux meilleurs spécialistes.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    RAPHAËL (Cerveau Central)          │
│         claude-opus-4-8 + adaptive thinking           │
│  Comprend → Planifie → Délègue → Synthétise → Évolue │
└──────────────────────┬──────────────────────────────┘
                       │ Orchestration
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │ Sophie  │   │ Victor  │   │  Elena  │  ...10 agents
   │Research │   │Writing  │   │Marketing│
   └─────────┘   └─────────┘   └─────────┘
```

## Agents Spécialisés

| Agent | Domaine | Super-pouvoir |
|-------|---------|---------------|
| **Sophie** | Recherche Web | Trouve N'IMPORTE quelle information avec précision chirurgicale |
| **Victor** | Rédaction & Copywriting | Copywriting qui convertit, scripts cinématographiques |
| **Elena** | Marketing & Ads | Campagnes Meta/Google/TikTok avec ROAS > 5x |
| **Marcus** | Stratégie Business | Business models qui scalent de 0 à 100M€ |
| **Aurora** | Images & Vidéos | Production Hollywood quality (8K, cinématique) |
| **Felix** | Trading & Finance | Analyse technique/fondamentale + gestion risque |
| **Diana** | E-commerce | Boutiques Shopify/WooCommerce optimisées |
| **Noah** | Sécurité & Risques | Protection des actifs, conformité, audit |
| **Luna** | Réseaux Sociaux | Croissance organique explosive, viral content |
| **Axel** | Data Analysis | Insights actionnables, forecasting, BI |

## Installation Rapide

```bash
# Cloner et installer
git clone <repo>
cd raphael
pip install -r requirements.txt

# Configurer les clés API
cp .env.example .env
# Éditez .env et ajoutez au minimum: ANTHROPIC_API_KEY=sk-ant-...

# Lancer en mode CLI interactif
python main.py cli

# Ou lancer l'API REST
python main.py api
# Accédez à http://localhost:8000/docs
```

## Utilisation

### Mode CLI
```
Vous: Crée une stratégie complète pour lancer ma boutique de vêtements en ligne

Raphaël: [Analyse → Délègue à Marcus + Diana + Elena + Luna → Synthétise]
→ Plan stratégique complet + setup boutique + stratégie marketing + social media
```

### API REST
```bash
# Chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyse le marché crypto et donne-moi un setup de trade BTC"}'

# Statut du réseau
curl http://localhost:8000/api/v1/agents

# Créer un nouvel agent
curl -X POST http://localhost:8000/api/v1/agents/spawn \
  -H "Content-Type: application/json" \
  -d '{"domain": "juridique", "skills": ["droit des affaires", "RGPD", "contrats"]}'

# Déclencher un cycle d'évolution
curl -X POST http://localhost:8000/api/v1/evolution/run-cycle
```

### Module Python
```python
import asyncio
from raphael.core.orchestrator import Raphael

async def main():
    raphael = Raphael()
    await raphael.initialize()
    
    response = await raphael.chat(
        "Lance une campagne publicitaire pour mon produit SaaS B2B"
    )
    print(response)

asyncio.run(main())
```

## Auto-Évolution

Le réseau évolue de façon autonome:
- **Évaluation** toutes les 6h: score de performance par agent
- **Optimisation** automatique des prompts des agents sous-performants
- **Création** de nouveaux agents si une compétence manque (détection automatique)
- **Mémoire** à long terme: chaque agent apprend de ses expériences passées

## Clés API Requises

**Minimum requis:**
- `ANTHROPIC_API_KEY` — Pour Claude (orchestration + agents)

**Pour les fonctionnalités avancées:**
- Images: `STABILITY_AI_API_KEY` ou `OPENAI_API_KEY`
- Vidéos: `RUNWAYML_API_KEY`
- Recherche: `SERPER_API_KEY` ou `BRAVE_SEARCH_API_KEY`
- Trading: `BINANCE_API_KEY` / `ALPACA_API_KEY`
- Ads: `META_ACCESS_TOKEN`, `GOOGLE_ADS_DEVELOPER_TOKEN`

Voir `.env.example` pour la liste complète.

## Structure du Projet

```
raphael/
├── core/
│   ├── orchestrator.py     # Raphaël — cerveau central
│   ├── registry.py         # Registre des agents
│   ├── router.py           # Routing des tâches
│   └── factory.py          # Création automatique d'agents
├── agents/
│   ├── base.py             # Classe de base avec boucle agentic
│   ├── sophie.py           # Recherche
│   ├── victor.py           # Rédaction
│   └── ...                 # 10 agents spécialisés
├── tools/
│   ├── web_search.py       # Serper/Brave/DuckDuckGo
│   ├── image_generation.py # Stability/DALL-E/Replicate
│   ├── video_generation.py # RunwayML/Pika/HeyGen
│   ├── ad_platforms.py     # Meta/Google Ads
│   └── data_tools.py       # CCXT/Pandas/Matplotlib
├── memory/
│   ├── short_term.py       # Contexte conversationnel
│   └── long_term.py        # ChromaDB vectoriel
├── evolution/
│   ├── evaluator.py        # Évaluation des performances
│   ├── optimizer.py        # Optimisation des prompts
│   └── creator.py          # Moteur d'évolution
└── api/
    ├── main.py             # FastAPI app
    └── routes/             # Endpoints REST
```
