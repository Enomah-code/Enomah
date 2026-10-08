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

La page s'ouvre sur les phrases que la personne entend depuis des années (« Le vent va t'emporter. », « Mange un peu, toi. », « Tu as quel âge, 14 ans ? »), posées en grand italique, puis barrées lentement par **la vague dorée du logo Livensya**. La même vague revient à la fin pour **souligner** la phrase que la personne a écrite elle-même dans le test (« ce que je veux vivre dans 60 jours »). Le trait qui barrait devient le trait qui souligne : c'est tout le tunnel.

Le choc émotionnel passe par les mots et le rythme, jamais par des couleurs agressives : pas de rouge, pas de compte à rebours, pas de contraste dur. Le test renvoie à la personne ses propres réponses, en une page, puis lui montre ce que coûtent 60 jours de plus sans rien changer. Le visiteur doit se sentir compris et en sécurité.

**Ambiance (consigne d'Enock)** : la douceur de ses visuels. Lumière naturelle chaude, crème, lin, bois clair, plantes, ombres de feuillage en filigrane (découpées dans ses bannières), coins arrondis, ombres portées très douces, beaucoup d'air, animations lentes (0,7 à 1,2 s) et fluides.

## 3. Palette : la charte Livensya (contraste vérifié, WCAG 2.2)

Relevée sur le logo et les visuels fournis par Enock (`images/marque/`). Le vert citron `#a5f600` de Chariow était un réglage par défaut : il n'est **pas** utilisé.

| Nom | Hex | Rôle | Contraste |
|---|---|---|---|
| Crème | `#F6F0E6` | fond principal | Encre dessus 13,1:1 |
| Lin | `#FFFCF6` | sections alternées, cartes | Encre dessus 14,5:1 |
| Encre (lettrage du logo) | `#1C2B21` | texte courant | 13 à 14,5:1 |
| Forêt (vague des bannières) | `#16402A` | titres, boutons, section finale | Crème sur Forêt 10,3:1 |
| Feuille (feuilles du logo) | `#216427` | liens, icônes, mots en italique | 6,4:1 sur Crème |
| Or doux | `#B8913A` | **décor uniquement** : vague, filets, cercles | (2,6:1, jamais pour du texte) |
| Or texte | `#7A5C1C` | étiquettes et chiffres dorés sur crème | 5,5:1 |
| Or clair | `#D9B65E` | bouton et vague sur fond Forêt | Forêt sur Or clair 6:1 |
| Sauge | `#5A6B5F` / `#B9C7B7` | texte secondaire clair / sur forêt | 5:1 / 6,6:1 |

Aucun dégradé violet-bleu, aucun texte en dégradé, aucun néon. Les seuls dégradés sont des halos crème presque invisibles (lumière du matin).

## 4. Typographies (2 familles, 4 styles, auto-hébergées, 120 Ko)

- **Newsreader** (serif à taille optique, dans l'esprit du logo et des couvertures) : titres en romain 400/500, et l'**italique** pour les phrases entendues et la phrase de la personne. C'est la voix « parlée » de la page.
- **Hanken Grotesk** (sans sobre et chaleureuse) : texte courant 400 et 700. Remplace Atkinson Hyperlegible, écartée car son zéro barré rendait « 60 jours » bizarre.
- Échelle (mobile → bureau) : 14 / 17,5 (texte) / 21 / 28 / 38 / 52 → 60 px. Interligne 1,6 pour le texte, 1,1 à 1,2 pour les titres.
- Français soigné : `lang="fr"`, césure automatique, guillemets « », espaces fines insécables avant ? ! : ; (passe typographique automatique sur le HTML et dans le JavaScript), aucun tiret cadratin.

## 5. Grille, espacements, formes, images

- Mobile d'abord : marge 20 px, colonne de lecture 34 em max. Bureau : 1 200 px max, compositions asymétriques (7/5, 5/7, 6/6 alternées), jamais tout centré.
- Espacements : 4 / 8 / 12 / 16 / 24 / 32 / 48 / 72 / 112 px. Sections : 72 px mobile, 112 px bureau.
- Coins : boutons en pilule, cartes 18 à 22 px, photos 12 px avec bord blanc (tirage photo).
- Ombres : très diffuses et chaudes (`rgba(60,48,20,.35)`, flou 60 px, décalées vers le bas).
- Photos : uniquement les 2 vraies photos d'Enock (avant à 24 ans, après), légendées. Aucune autre séance prévue.
- Visuels de marque : le mockup des 3 livres (`pack-3-livres-carre`) pour « Ce que tu reçois » et le ticket de l'offre, toujours légendé « visuel d'illustration ». Les ombres de feuillage sont découpées dans les bannières (`fond-feuillage.webp`, `fond-plante.webp`) et posées en filigrane, fondues par un masque.
- Illustrations : maison, sobres, au trait ou à plat (journée de repas, deux assiettes, calendrier de 60 cercles). Icônes : un seul jeu SVG au trait 1,75 px. Aucun emoji.
- Mouvement : un seul moment orchestré (les phrases qui se barrent), puis des apparitions lentes au défilement. `prefers-reduced-motion` respecté.

## 6. Structure du tunnel (une page + merci.html)

| # | Section | Fond | Objectif |
|---|---|---|---|
| 1 | Héros « les mots » + photo d'Enock à 24 ans | Crème, feuillage en filigrane | Choc de reconnaissance (« c'est moi »). Bouton test visible sans défiler, lien direct vers l'offre. |
| 2 | Test de 2 minutes (intro + 8 écrans, barre de progression) | Crème, carte en lin | Engagement progressif : facile d'abord, sensible ensuite avec le « pourquoi », réassurance après les phrases et après le poids. |
| 3 | Ton résultat (généré) | Lin | Le déclic : ses réponses en miroir, IMC indicatif et prudent, alertes santé douces, les deux chemins des 60 prochains jours, sa phrase soulignée. |
| 4 | « Tu manges, pourtant. » | Crème | Recadrer : ce n'est pas la quantité, c'est quand, quoi, et chaque jour. |
| 5 | L'histoire d'Enock | Lin | Preuve vécue : avant/après légendés, récit à la 1re personne (à valider). |
| 6 | La méthode en 3 leviers | Crème | Trois visuels différents : une journée de repas, deux assiettes, 60 cercles. |
| 7 | Ce que tu reçois | Lin | Mockup des 3 documents, 4 parties du livre, format et poids (45 Mo). |
| 8 | Jour 1, jour 30, jour 60 | Crème | Se projeter, sans chiffre promis. Ligne de 60 jours. |
| 9 | Vidéo faceless (masquée tant que `VIDEO_SRC` est vide) | Lin | Motivation, objections, soutien. Affiche + lecture au clic. |
| 10 | (Témoignages : emplacement commenté, vide) | | Seulement de vrais retours. |
| 11 | L'offre + paiement Mobile Money en 5 étapes | Lin | Prix, contenu, bouton, honnêteté (pas de chiffre garanti). |
| 12 | Questions fréquentes | Crème | Lever les objections près du prix (femmes, sirops, kilos, coût, réception, santé, mineurs). |
| 13 | Final « les mots qui comptent » | Forêt, ouvert par la vague | Bouclage : sa phrase soulignée d'or, bouton or clair. |
| 14 | merci.html | Crème et lin | Rassurer, expliquer l'accès, cocher les 4 gestes du jour 1 ce soir. |

Barre d'achat collante sur téléphone, visible seulement entre les sections (masquée sur le héros, le test, le résultat, l'offre et le final).

## 6 bis. Suivi Meta (simple, sans doublon)

Un seul fichier `js/tracking.js`, `PIXEL_ID` vide = rien n'est chargé. Pixel standard uniquement : PageView (toutes pages), ViewContent (offre affichée), Lead (fin du test, une fois par visiteur), InitiateCheckout (clic d'achat, anti double-clic). Chaque événement a un `eventID` unique. Pas de Purchase dans le navigateur : il sera envoyé une seule fois côté serveur (voir LISEZMOI.md).

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
- [x] Pas de couleurs d'alerte : la santé est signalée par un cadre doré doux et une icône, jamais en rouge.
- [x] Pas de grille de 3 cartes identiques : les 3 leviers ont chacun leur visuel (journée, assiette, calendrier).
- [x] Aucun emoji, aucune illustration 3D, aucune photo de stock.
- [x] Aucun texte creux ; chaque phrase reprend les mots du public (« le vent va t'emporter », « mange un peu »).
- [x] Micro-animations sobres, états survol et appui, focus visible, césures, guillemets français, espaces insécables.
- [x] Rien de faux : pas de compteur, pas d'avis inventé, pas de compte à rebours, pas de garantie inventée.

## 9. Relecture par un directeur artistique indépendant (3 tours, contexte neuf)

| Tour | Design | Texte | Confiance | Conversion | Principales corrections faites ensuite |
|---|---|---|---|---|---|
| 1 | 7,5 | 8,5 | 5 | 6 | Photos recadrées sous le bandeau noir, vidéo masquée tant qu'elle n'existe pas, bouton d'achat après l'histoire, héros raccourci, FAQ clés ouvertes, barre d'achat visible sur le résultat |
| 2 | 8 | 8,5 | 5,5 | 6,5 | Enock signe la carte de l'offre (photo + contact), ligne de réassurance après paiement, bouton d'achat direct dans le résultat, bloc forêt au milieu, assiette de riz dessinée, légende du jour raté, carte « test terminé » remplacée |
| 3 | 8 | 8,5 | 6 | 7 | Assiettes recolorées dans la palette. Ce qui bloque sous 8 : absence de témoignages, de garantie, de contact direct (e-mail ou WhatsApp) et de vraies pages du PDF. À fournir par Enock. |
