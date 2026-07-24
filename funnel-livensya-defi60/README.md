# Tunnel de vente — Livensya · Défi 60 Jours

Page de capture + page de vente + tunnel automatisé pour le produit **"Défi 60 Jours : Du sous-poids à votre poids idéal"**, vendu sur la boutique Chariow **Livensya**. Site statique (HTML/CSS/JS), sans dépendance, prêt à déployer.

## Structure

```
funnel-livensya-defi60/
├── index.html      # Page de capture (opt-in email/téléphone + accroche)
├── vente.html       # Page de vente / présentation complète + CTA d'achat
├── assets/
│   ├── style.css
│   └── script.js    # Logique du tunnel (capture, personnalisation, countdown, CTA)
└── README.md
```

## Comment fonctionne le tunnel

1. **`index.html`** — capture le prénom, l'email et le téléphone du visiteur en échange d'un aperçu gratuit.
   À la validation, le lead est enregistré (`localStorage`) et le visiteur est redirigé automatiquement vers `vente.html`.
2. **`vente.html`** — page de vente complète (histoire, contenu du programme, bonus, FAQ, offre) reprenant
   mot pour mot le contenu réel du produit sur Chariow. Elle personnalise l'accueil ("Bravo {prénom}, ...")
   si un lead a été capturé, affiche un compte à rebours jusqu'à minuit (l'offre -68% se renouvelle chaque jour
   sur Chariow), puis redirige tous les boutons d'achat vers l'URL réelle de checkout Chariow :
   `https://ykhzgspm.mychariow.store/prd_4bisyd7x`.
3. **Le paiement, la livraison du produit et l'email de confirmation** restent gérés nativement par Chariow
   (Mobile Money / carte, envoi de l'accès à vie) — inutile de dupliquer cette logique ici.

## Brancher la capture de leads sur un outil externe (optionnel)

Par défaut, les leads sont uniquement stockés dans le navigateur du visiteur. Pour les recevoir automatiquement
(email, CRM, tableur...), ouvre `assets/script.js` et renseigne :

```js
window.FUNNEL_CONFIG.leadWebhookUrl = "https://... "; // ton webhook
```

Ça fonctionne avec n'importe quel service qui accepte un `POST` JSON : un **Pulse** Chariow (webhook sortant),
Zapier, Make, Google Apps Script relié à un Google Sheet, ou Formspree.

## Déploiement

Site 100% statique : dépose le dossier `funnel-livensya-defi60/` tel quel sur Netlify, Vercel, GitHub Pages,
ou tout hébergement statique. Aucune étape de build nécessaire.

Pour tester en local :

```bash
cd funnel-livensya-defi60
python3 -m http.server 8080
# puis ouvre http://localhost:8080
```

## Personnalisation rapide

- **Couleurs / typographie** : `assets/style.css` (variables `:root` en haut du fichier).
- **URL de checkout** : `assets/script.js` → `FUNNEL_CONFIG.checkoutUrl`.
- **Copie / FAQ / prix** : directement dans `index.html` et `vente.html`, synchronisés avec les données
  réelles du produit sur Chariow au moment de la création de ce tunnel (prix 3 999 FCFA au lieu de 12 500 FCFA, -68%).
