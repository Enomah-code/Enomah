# Déployer Angeleck sur Vercel (URL publique)

Le frontend est une app **Next.js 14** prête pour Vercel. La route serveur
`app/api/chat/route.ts` appelle l'API Claude — la clé est lue côté serveur
via la variable d'environnement `ANTHROPIC_API_KEY` (jamais exposée au navigateur).

## Prérequis
- Un compte Vercel (gratuit) : https://vercel.com
- Ta clé API Claude : https://console.anthropic.com

## Étapes (depuis le dossier `frontend/`)

```bash
cd frontend

# 1. Installer la CLI Vercel
npm install -g vercel

# 2. Se connecter
vercel login

# 3. Lier le projet (Vercel détecte Next.js automatiquement)
#    Quand il demande "In which directory is your code located?" -> ./
vercel link

# 4. Ajouter la clé API comme variable d'environnement chiffrée (Production)
vercel env add ANTHROPIC_API_KEY production
#    -> colle ta clé sk-ant-... quand demandé

# 5. Déployer en production -> renvoie une URL publique https://
vercel --prod
```

À la fin, Vercel affiche une URL du type `https://angeleck-xxx.vercel.app`.

## Important
- **Root Directory** : si tu déploies depuis la racine du dépôt (et non depuis
  `frontend/`), règle le *Root Directory* du projet sur `frontend` dans
  Settings → General sur le dashboard Vercel.
- La clé `ANTHROPIC_API_KEY` doit être définie dans Vercel (étape 4), pas dans
  le code. Le fichier `.env.local` local n'est pas déployé.
- Sans clé configurée, le site fonctionne quand même en **mode démo**
  (réponses simulées de Raphaël).

## Mode démo vs live
| Mode | Condition | Comportement du chat |
|------|-----------|----------------------|
| **Live** | `ANTHROPIC_API_KEY` définie | Vraies réponses Claude (`claude-opus-4-8`) en streaming |
| **Démo** | pas de clé | Réponses simulées, app 100% navigable |
