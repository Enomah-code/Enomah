# Charte de l'équipe d'agents — Studio OS

Document de référence commun à **tous** les agents. Chaque agent le lit avant toute tâche, avec `docs/saas-createurs/PLAN.md` (la section « Révision 2 » et la section « Décisions prises » priment sur le reste).

## 1. Décisions fixées (ne pas remettre en cause sans accord du fondateur)

| Sujet | Décision |
|---|---|
| Modèle économique | **Plan B — commission** : accès gratuit et ouvert à tous ; 15 % par commande ; 10 % à vie dès le mois qui suit 4 000 000 FCFA de ventes cumulées (`docs/saas-createurs/COMMISSION.md`). Pas d'abonnement. |
| Paiements | Tous les paiements clients passent par la plateforme, avec **séquestre** (fonds bloqués jusqu'à validation ou auto-validation à J+7), commission, reversements. Fonds détenus par un partenaire agréé, jamais sur un compte personnel. |
| Société | **Basée au Bénin** (zone UEMOA, franc CFA XOF, régulation BCEAO). Stripe n'est pas disponible pour une société béninoise : candidats FedaPay, KkiaPay, CinetPay (Mobile Money + cartes), à confirmer sur le séquestre et les reversements. Structure juridique de l'encaissement pour compte de tiers à valider par un avocat. |
| Portée | **Internationale** : créateurs et clients de tout pays ; FR + EN au lancement ; multi-devises ; fuseaux horaires. |
| Compte client | **Un compte unique par client** pour tous les créateurs, avec chat, nouvelles commandes, paiements. |
| Relances | E-mail : automatique par défaut, personnalisable ou désactivable par le créateur. **WhatsApp : jamais envoyé par la plateforme**, uniquement via l'intégration connectée par le créateur à son propre compte. |
| Livraison protégée | Avant paiement total : filigrane nominatif dynamique, aucun téléchargement / partage, basse résolution, vidéo DRM, images en vidéo DRM. Après : tout se débloque. Ne jamais promettre un blocage à 100 % de l'enregistrement d'écran. |
| Pile | Next.js (App Router) + TypeScript, Tailwind + tokens du design system Concept Pub, Supabase (PostgreSQL, Auth, RLS, Realtime), Cloudflare R2, vidéo DRM (Mux ou équivalent), Inngest/Trigger.dev, Resend, Vercel. |
| Design | Design system Concept Pub (ivoire `#FBF8F1`, noir `#0B0A09`, or `#B5934E` ; Cormorant Garamond, Manrope, IBM Plex Mono ; easing `cubic-bezier(0.16,1,0.3,1)`). Pas d'emoji dans le produit. |

## 2. Organisation et surveillance

```
Fondateur (décide, valide chaque fin de phase)
   └── Session principale Claude Code = orchestrateur
         ├── studio-chef-de-projet : découpe, planifie, attribue, fait le rapport
         └── 19 agents spécialistes (un poste chacun)
               └── contrôles obligatoires avant fusion :
                   studio-relecteur-code + studio-qa (+ studio-securite pour paiements, auth, données, fichiers)
```

- Un sous-agent ne peut pas lancer d'autres sous-agents : c'est **la session principale** qui délègue, sur la base du plan produit par `studio-chef-de-projet`.
- **Une tâche = un agent = une branche** (`studio/<poste>/<sujet-court>`), dans son périmètre de fichiers (section 3). Toucher au périmètre d'un autre agent = demander via le rapport de passation, pas modifier.
- **Aucune fusion** sans : tests verts, revue du relecteur, validation QA ; + sécurité pour paiements, authentification, isolation des données, fichiers.
- Tout ce qui engage juridiquement ou financièrement (CGU, contrats, fiscalité, flux d'argent) est **validé par un humain** : avocat, expert-comptable, développeur senior pour le code des paiements.

## 3. Périmètres de fichiers (monorepo)

| Agent | Possède |
|---|---|
| studio-architecte | `docs/architecture/`, `packages/db/` (schéma, migrations, RLS) en co-validation avec le back-end |
| studio-designer-ui-ux | `design/`, `packages/ui/tokens/` |
| studio-front-end | `apps/web/app/(sites)/`, `apps/web/app/(dashboard)/`, `apps/web/app/(account)/`, `apps/web/app/(marketing)/`, `packages/ui/`, `packages/sections/` |
| studio-back-end | `apps/web/app/api/` (hors paiements), `packages/core/`, `packages/pricing/`, `packages/db/` |
| studio-paiements | `packages/payments/`, `apps/web/app/api/payments/`, `apps/web/app/api/webhooks/payments/`, facturation |
| studio-marketplace | `packages/marketplace/`, `apps/web/app/(marketplace)/` (écrans en lien avec le front-end) |
| studio-temps-reel | `packages/chat/`, `packages/notifications/` |
| studio-medias-protection | `packages/media/`, pipeline vidéo/image, filigranes, DRM |
| studio-mobile | `apps/mobile/` |
| studio-devops | `.github/`, `infra/`, configuration d'hébergement, surveillance |
| studio-qa | `tests/`, `**/*.test.ts`, `e2e/` |
| studio-securite | `docs/securite/`, correctifs de sécurité sur tout le code (après revue) |
| studio-juriste | `docs/legal/` |
| studio-finance | `docs/finance/` |
| studio-marketing-seo | `docs/marketing/`, contenus SEO |
| studio-redacteur | `packages/i18n/` (textes FR/EN), `packages/emails/` (textes), `docs/aide/` |
| studio-support | `docs/support/` (procédures, centre d'aide, litiges) |
| studio-chef-de-produit | `docs/produit/` (spécifications, user stories) |
| studio-chef-de-projet | `docs/saas-createurs/suivi/` |
| studio-relecteur-code | aucun (lecture seule, rapports dans `docs/saas-createurs/suivi/revues/`) |

## 4. Suivi du temps et du travail

- Chaque agent **ouvre et clôt** sa tâche dans `docs/saas-createurs/suivi/JOURNAL.md` (une ligne par tâche, heure UTC obtenue par `date -u +%Y-%m-%dT%H:%MZ`).
- Un journal automatique est aussi tenu par un hook (`.claude/logs/agents.jsonl`) : heure de début et de fin de chaque agent, indépendamment de ce qu'il déclare. Synthèse du temps par agent : `python3 docs/saas-createurs/suivi/temps.py` (option `--jour AAAA-MM-JJ`).
- `studio-chef-de-projet` compile le **rapport quotidien** dans `docs/saas-createurs/suivi/rapports/AAAA-MM-JJ.md` : tâches terminées, en cours, bloquées, temps par agent, risques, décisions attendues du fondateur.

## 5. Format de rapport de passation (fin de chaque tâche)

```
## Rapport — <agent> — <tâche>
Statut : terminé | partiel | bloqué
Branche : studio/<poste>/<sujet>
Fait : …
Fichiers modifiés : …
Tests : commande lancée + résultat
Reste à faire / dépendances : …
Demandes aux autres agents : @studio-xxx : …
Décisions à valider par le fondateur : …
```

## 6. Règles communes

1. Lire `PLAN.md` et cette charte avant de commencer. Ne pas inventer de décision produit : la demander.
2. Rester dans son périmètre ; petites modifications ciblées ; pas de refonte non demandée.
3. Écrire des tests pour tout code métier (prix, commissions, séquestre, isolation des données : 100 % des cas couverts).
4. Montants en entiers dans la plus petite unité ; jamais de flottants pour l'argent.
5. Jamais de secret dans le code ni dans les journaux.
6. Textes visibles par l'utilisateur en FR et EN via `packages/i18n`, jamais en dur.
7. Dire clairement ce qui n'est pas vérifié ; ne jamais annoncer « terminé » si les tests ne passent pas.
8. Consulter les skills listés dans sa fiche quand ils s'appliquent.
