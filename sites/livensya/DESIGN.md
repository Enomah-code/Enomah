# Livensya · Défi 60 jours · Direction artistique

## 1. Le projet en 6 lignes

- **Marque** : Livensya (santé et bien-être), portée par Enock Mahougnan, Cotonou.
- **Offre** : « Défi 60 jours : du sous-poids à ton poids idéal ». 3 PDF (le Livre en 4 parties, le Programme alimentaire jour par jour, le Carnet de transformation). 3 999 F (prix barré 12 500 F), paiement Chariow (MTN, Moov, Orange, Wave, carte).
- **Client** : jeune adulte d'Afrique de l'Ouest francophone, homme ou femme, en sous-poids. Il entend « le vent va t'emporter », « mange un peu », on le prend pour un ado. Il évite les photos, cache son corps sous des habits larges, a souvent déjà essayé de « forcer » ou les sirops pour grossir.
- **Promesse** : une méthode naturelle, sans sirop ni comprimé, avec les repas d'ici (riz, igname, plantain, arachides, avocat, œufs, poisson), pour prendre du poids sainement, jour après jour. Aucun chiffre garanti.
- **Preuve disponible** : l'histoire vraie d'Enock et 2 photos (à 24 ans, puis après). Zéro vente, zéro avis client à ce jour : aucune preuve sociale affichée, un emplacement commenté est prêt.
- **Action attendue** : faire le test de 2 minutes, puis acheter sur Chariow (constante `LIEN_PAIEMENT`).

## 2. Concept

> **« Les mots qu'on t'a dits, puis les tiens. »**

La page s'ouvre la nuit, sur les phrases que la personne entend depuis des années, posées en grand italique et barrées une à une. Elle se termine au matin, sur la phrase que la personne a écrite elle-même dans le test (« ce que je veux vivre dans 60 jours »), dans le même italique, mais cette fois non barrée. Tout le tunnel est ce passage : de la nuit (le miroir, les remarques) au matin (le jour 1).

Le choc émotionnel ne vient pas d'un faux compte à rebours : il vient du miroir. Le test renvoie à la personne ses propres réponses, en une page, puis lui montre ce que coûtent 60 jours de plus sans rien changer.

## 3. Palette : le branding Chariow d'Enock (contraste vérifié, WCAG 2.2)

Construite sur les couleurs déjà choisies par Enock : le vert citron de sa boutique Chariow (`--brand-color: #a5f600`), le vert de ses titres produit (`rgb(0,138,0)`) et le vert forêt de son logo (relevé dans le fichier : `#1E2E25`).

| Nom | Hex | Rôle | Contraste |
|---|---|---|---|
| Forêt (logo) | `#1E2E25` | fond du héros, du test, du final ; texte sur citron | Lait dessus 12,1:1 |
| Nuit | `#14211A` | fond le plus profond (cartes du test) | Lait dessus 14:1 |
| Citron (Chariow) | `#A5F600` | **aplat** des boutons d'action (texte Forêt), surlignage et phrase de la personne **sur fond sombre** | Forêt sur Citron 10,7:1 ; Nuit sur Citron 12,5:1 |
| Vert Chariow | `#008A00` | grands titres et chiffres sur blanc uniquement (≥ 24 px) | 4,5:1 sur blanc |
| Vert profond | `#006E00` | liens et petits textes verts sur fond clair | 6:1 sur Matin |
| Matin | `#F4F7EE` | fond des sections de vente | Encre dessus 15:1 |
| Encre | `#14231B` | texte principal sur fond clair | 15:1 |
| Lait | `#E9EEE6` | texte sur fond sombre | 12 à 14:1 |
| Sauge | `#4A5A50` / `#A9B8AE` | texte secondaire clair / sombre | 6,8:1 / 6,9:1 |

Règle : **jamais de texte citron sur fond clair** (1,3:1). Le citron ne vit que sur la forêt ou en aplat sous un texte foncé. Pas de dégradé violet-bleu, pas de texte en dégradé, pas de néon : le citron est utilisé à plat, en petites surfaces.

## 4. Typographies (2 familles, 4 styles, auto-hébergées, 120 Ko)

- **Newsreader** (serif à taille optique) : titres en romain 400/500, et l'**italique** pour les phrases entendues et la phrase de la personne. C'est la voix « parlée » de la page.
- **Atkinson Hyperlegible Next** (sans) : texte courant 400 et 700. Dessinée pour la lisibilité, pensée pour les petits écrans Android et les yeux fatigués.
- Échelle (mobile → bureau) : 15 / 17,5 (texte) / 21 / 28 / 38 / 52 → 72 px. Interligne 1,6 pour le texte, 1,05 à 1,15 pour les titres.
- Français soigné : `lang="fr"`, césure automatique, guillemets « », espaces fines insécables avant ? ! : ; (passe typographique automatique), aucun tiret cadratin.

## 5. Grille, espacements, formes

- Mobile d'abord : marge latérale 20 px, colonne de lecture 34 em max.
- Bureau : grille 12 colonnes, 1 200 px max, compositions asymétriques (7/5, 5/7), jamais tout centré.
- Espacements : échelle 4 / 8 / 12 / 16 / 24 / 32 / 48 / 72 / 112 px. Sections : 72 px mobile, 112 px bureau.
- Coins : 6 px pour les boutons et champs, 2 px pour les photos (comme un tirage), cercles seulement pour les points du calendrier.
- Photos : uniquement les 2 vraies photos d'Enock (il n'en a pas d'autres, aucune séance prévue), cadrées 4:5, légendées comme des tirages (date, âge, contexte), légère bordure Lait. Aucune photo de stock, aucune illustration 3D. La couverture Chariow (visuels générés) n'est utilisée que pour l'aperçu de partage (Open Graph).
- Icônes : un seul jeu, traits SVG 1,75 px dessinés à la main pour le projet (flèche, coche, cadenas, téléphone, plus/moins). Aucun emoji.
- Mouvement : un seul moment orchestré (les phrases qui se barrent dans le héros), puis des apparitions sobres au défilement (opacité + 12 px). `prefers-reduced-motion` respecté.

## 6. Structure du tunnel (une page + merci.html)

| # | Section | Fond | Objectif |
|---|---|---|---|
| 1 | Héros « les mots » | Nuit | Choc de reconnaissance : « c'est moi ». Bouton test visible sans défiler, lien direct vers l'offre. |
| 2 | Test de 2 minutes (8 écrans, barre de progression) | Nuit | Engagement progressif (modèle Noom) : facile d'abord, sensible ensuite avec le « pourquoi », réassurance après le poids. |
| 3 | Ton résultat | Nuit → Matin | Le déclic : ses réponses en miroir, IMC indicatif et prudent, coût de 60 jours sans changement, sa phrase gardée. |
| 4 | « Tu manges, pourtant » | Matin | Recadrer le problème : ce n'est pas la quantité, c'est la structure, la densité, la régularité. |
| 5 | L'histoire d'Enock | Matin | Preuve vécue : 2 photos légendées, ses mots à la première personne. |
| 6 | La méthode en 3 leviers | Blanc | Rendre la méthode concrète : une journée de repas, une assiette plus dense, 60 jours cochés. Trois visuels différents, pas trois cartes. |
| 7 | Ce que tu reçois | Matin | Les 3 documents, les 4 parties du livre, format et poids des fichiers (3G). |
| 8 | Jour 1, jour 30, jour 60 | Matin | Projeter la personne dans le défi, sans chiffre promis. Ligne de 60 points. |
| 9 | (Témoignages : emplacement commenté, vide) | | À remplir uniquement avec de vrais retours. |
| 10 | L'offre + paiement en 5 étapes | Blanc | Prix, contenu, bouton, Mobile Money expliqué, honnêteté (pas de garantie de résultat). |
| 11 | Questions fréquentes | Matin | Lever les objections près du prix. |
| 12 | Final « les mots qui comptent » | Nuit | Bouclage du concept : sa phrase à elle, non barrée, et le bouton. |
| 13 | merci.html | Matin | Rassurer, expliquer l'accès, faire démarrer le jour 1 ce soir. |

Barre d'achat collante sur téléphone, visible après le héros, masquée sur l'offre.

## 7. Planche de références (recherche du 08/10/2026)

| Site | Ce qu'on emprunte | Ce qu'on évite |
|---|---|---|
| [Noom](https://www.noom.com), analysé par [RevenueCat (avril 2026)](https://www.revenuecat.com/blog/growth/web-to-app-onboarding-funnel) | Le test qui prépare la décision : 1re question facile, barre de progression, « pourquoi on te demande ça » sur les questions sensibles, réassurance juste après la saisie du poids, résultat sans honte, prix après l'engagement. | Les 113 écrans (on en garde 8), le faux compte à rebours de 15 min, le « prix libre » qui ne change rien. |
| [Bony to Beastly](https://bonytobeastly.com) | Le seul grand site du créneau « maigre qui veut prendre du poids » : histoire du fondateur à la 1re personne, ton chaleureux qui dédramatise la frustration, rappel que les résultats varient. | Les compteurs (13 000 personnes aidées) qu'on n'a pas, la galerie d'avant/après qu'on n'a pas, la navigation d'un site d'articles. |
| [Future](https://www.future.co) | Rendre l'accompagnement concret par un exemple (un vrai message de suivi) : chez nous, une vraie journée de repas et une page du carnet. Le bouton répété après chaque preuve. | Les notes App Store et pourcentages qu'on ne peut pas prouver. |
| [Ritual](https://ritual.com) | Un mot en italique pour donner la voix d'une phrase ; la transparence comme preuve ; les garde-fous santé écrits sans honte. | La grille de 6 produits, le bandeau promo permanent. |
| [Wave](https://www.wave.com/fr/) | La langue d'ici : phrases courtes, usages réels (« sans te déplacer »), le « tu » dans la bouche des gens, la simplicité qui rassure sur l'argent mobile. | Rien à éviter sur le ton ; on n'imite pas leur identité visuelle. |
| [Swipe Pages, pages bien-être 2026](https://swipepages.com/blog/8-best-wellness-supplement-self-care-landing-page-examples-of-2026/) et [Heyflow, tunnels à quiz](https://heyflow.com/blog/10-quiz-funnel-examples/) | Indiquer la durée du test dès le départ, résultat vraiment personnalisé (sinon c'est du temps perdu). | Les preuves « cliniques » des compléments ; les chiffres de conversion non vérifiés des éditeurs. |
| Tendances 2026 ([Zoho](https://www.zoho.com/landingpage/landing-page-design-trends.html), [Involve.me](https://involve.me/blog/landing-page-design-trends), [Moburst](https://www.moburst.com/blog/landing-page-design-trends-2026/)) | Mobile d'abord, page légère, vraies photos plutôt que visuels génériques, contraste fort sur l'action, Core Web Vitals. | La « personnalisation IA » gadget. |

### Concurrents directs

| Concurrent | Promesse et prix | Faiblesses (notre angle) |
|---|---|---|
| Sirops et comprimés « pour grossir » vendus sur WhatsApp, TikTok et au marché (type Apetamin, à base de cyproheptadine) | « Grossir vite », quelques milliers de F | Médicament vendu sans ordonnance ; la [FDA américaine met en garde](https://www.healthday.com/healthpro-news/general-health/apetamin-use-of-this-illegal-weight-gain-product-can-bring-tragic-results-2659941288) (somnolence, foie, cœur). Notre angle : « sans sirop, sans comprimé », dit calmement, sans faire peur. |
| Ebook de recettes africaines « prise de formes » sur [Comeup](https://comeup.com/fr/service/540301/creer-ton-ebook-de-recettes-africaines-healthy-pour-maigrir) | Menu de 14 jours + liste de courses, environ 17,55 $ (10 000 F et plus) | Pensé d'abord pour maigrir, prise de poids en option, pas d'histoire vécue. Notre angle : 60 jours, pensé uniquement pour le sous-poids, par quelqu'un qui l'a vécu, moins cher. |
| Guides PDF « naturels » génériques sur Payhip ou Gumroad ([exemple à 8 €](https://payhip.com/b/y7uJv)) | Plan de 30 jours, environ 5 000 F | Aucun auteur, aucune preuve, aucun avertissement santé, euros et carte uniquement. Notre angle : un visage, une histoire, Mobile Money, prudence santé affichée. |

## 8. Liste anti « site IA » (contrôlée avant livraison)

- [x] Aucun dégradé violet-bleu, aucun texte en dégradé, aucun néon.
- [x] Héros asymétrique et ancré sur une vraie photo, pas de « titre + sous-titre + 2 boutons » centrés.
- [x] Pas de grille de 3 cartes identiques : les 3 leviers ont chacun leur visuel (journée, assiette, calendrier).
- [x] Aucun emoji, aucune illustration 3D, aucune photo de stock.
- [x] Aucun texte creux ; chaque phrase reprend les mots du public (« le vent va t'emporter », « mange un peu »).
- [x] Micro-animations sobres, états survol et appui, focus visible, césures, guillemets français, espaces insécables.
- [x] Rien de faux : pas de compteur, pas d'avis inventé, pas de compte à rebours, pas de garantie inventée.
