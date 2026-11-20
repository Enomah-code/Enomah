# IABB · Pistes de branding pour la refonte du tunnel

Statut : **proposition, à valider par Enock**. Rien n'est en ligne. Aucun Pixel, aucun script de suivi, aucun lien de paiement réel dans les maquettes.

Fichiers :
- `piste-a.html`, `piste-b.html`, `piste-c.html` : 3 maquettes (accueil, une question du quiz, carte de l'offre), à ouvrir dans un navigateur.
- `comparatif.html` : les 3 pistes côte à côte.
- `captures/` : `piste-x-390.png` (téléphone, page entière), `piste-x-390-premier-ecran.png` (ce qu'on voit sans défiler), `piste-x-1440.png` (ordinateur), `comparatif-1440.png`.
- `assets/` : `enock.webp` (portrait détouré, 28 Ko), `logo-emk.webp` (logo existant sur fond transparent, inchangé), `certificat.webp`.

---

## 1. Le projet en 6 lignes

1. **Marque** : EMK Blue Diamond (Cotonou), formation « IA Business Building », certification « IA Business Builder ». Logo inchangé : « EMK » sans-serif encre + « Blue Diamond » serif italique violet `#47218F`.
2. **Offre** : 8 modules, 5 bonus (valeur annoncée 47 000 F), certification, mises à jour à vie. **4 999 F CFA au lieu de 35 000 F**, paiement unique, garantie 7 jours.
3. **Client** : Afrique de l'Ouest francophone, sur Android en 3G/4G, débutant en IA, salarié, freelance ou entrepreneur. Douleur : « je bosse tout le temps et je n'avance pas », peur d'être largué par ceux qui utilisent l'IA.
4. **Promesse** : créer soi-même son agent WhatsApp, son site pro et son application, sans coder, et le prouver par une certification.
5. **Preuves disponibles** : portrait réel d'Enock, modèle de certificat, programme détaillé, garantie, widget d'avis Chariow et notifications de ventes réelles (API) dans le tunnel actuel. Aucun témoignage inventé dans les maquettes.
6. **Action attendue** : commencer le bilan (quiz), puis acheter sur Chariow (Mobile Money ou carte).

---

## 2. Recherche

### Tendances 2026 retenues (et ce qu'on en fait)
- Pages épurées, centrées sur l'utilisateur, avec de vraies captures du produit plutôt que des illustrations ([Zoho, 2026](https://www.zoho.com/landingpage/landing-page-design-trends.html)). Nous : la bulle WhatsApp, la liste des modules, le certificat réel.
- Le contraste remplace la couleur criarde, boutons très contrastés sans casser l'harmonie (Zoho). Nous : un seul accent pour l'action par piste.
- Fonds clairs « non blanchis », légèrement teintés, plutôt que le blanc pur ([Line25, 2026](https://line25.com/articles/web-design-trends-2026/)). Nous : lavande `#F5F7FE`, blanc violacé `#FAF8FD`, blanc bleuté `#FBFBFF`. On évite volontairement le crème chaud, devenu un réflexe « site IA ».
- Typographie expressive et grande, tailles fluides avec `clamp()` (Line25, [GetResponse](https://www.getresponse.com/blog/landing-page-design-trends)). Nous : titres très grands sur téléphone, une police de titre qui porte la personnalité.
- Vitesse et stabilité (Core Web Vitals) comme condition de confiance ([Moburst](https://www.moburst.com/blog/landing-page-design-trends-2026/)). Nous : 108 à 214 Ko par maquette, polices limitées à 2 familles.
- Pour une formation, l'achat dépend de la confiance dans le formateur : il faut le montrer tôt ([Swipe Pages](https://swipepages.com/create/course-landing-page)). Nous : Enock visible dès le premier écran dans les 3 pistes.

### Planche de références (sites réellement visités le 9 octobre 2026)

| Site | Ce qu'on emprunte | Ce qu'on évite |
|---|---|---|
| [DeepLearning.AI](https://www.deeplearning.ai) | Indigo profond + jaune or + photo réelle du formateur, et un mot en italique serif (« *anywhere* ») dans un titre sans-serif. Preuve que indigo/or fait « IA sérieuse ». | Leur héros entièrement sombre (Enock veut du clair), les motifs de circuits. |
| [Brilliant](https://brilliant.org) | Fond clair légèrement teinté, titre serif chaleureux, l'interactif montré dans une carte à droite. | Deux boutons équivalents dans le héros (dilue l'action). |
| [Maven](https://maven.com/wes-kao/build-a-cbc) | Formateur présenté avec photo, nom et rôle, avant toute promesse. Serif fine sur blanc pour le sérieux. | Densité de catalogue, logos de grandes entreprises qu'on n'a pas. |
| [Alegria Academy](https://alegria.group/academy) (concurrent FR) | Portrait détouré + petites cartes de preuve chiffrée autour. Promesse simple « l'IA et le NoCode ». | Rouge et violet saturés, majuscules criardes, trop de bandeaux. |
| [Headway](https://makeheadway.com) | Tunnel quiz : « un plan construit autour de toi », une question par écran, barre de progression. Fond très légèrement teinté. | Style générique d'application, aucune personnalité de marque. |
| [Duolingo](https://www.duolingo.com) | Boutons épais et tactiles, état « appuyé » visible, ton rassurant. | Mascotte et illustrations 3D, univers enfantin. |
| [Chariow](https://chariow.com) | Le décor où l'acheteur finira : rester cohérent et sobre pour que le passage au paiement ne surprenne pas. | Le centrage systématique titre + sous-titre. |
| [Kolonell](https://kolonell.com/fr) (concurrent africain) | Rien sur le visuel. Sur le fond : paiement Wave/Orange Money mis en avant, assistance WhatsApp. | Fond noir + vert néon « matrix », le cliché tech que l'on refuse. |

### 3 concurrents directs
1. **Kolonell Academy (Sénégal)** : « Découvrir l'IA », 5 h, **25 000 FCFA** ; parcours complet 87 h à 350 000 FCFA. Promesse : « une compétence utilisable dans la semaine ». Faiblesses : formateur peu présenté, chiffres non étayés, pas de remboursement visible, rien sur la reconnaissance du certificat ([source](https://kolonell.com/fr/blog/apprendre-ia-debutant-thies-formation-2026)). Notre avantage : 5 fois moins cher, garantie 7 jours, livrables concrets.
2. **Alegria Academy (France)** : formations IA et NoCode certifiantes (RNCP), exemple à 2 400 €, 14 700 apprenants revendiqués. Faiblesses pour notre public : prix hors de portée, financement pensé pour la France, rien sur Mobile Money.
3. **Le « je paie quelqu'un »** : freelances qui vendent un agent WhatsApp IA de 25 000 à 150 000 FCFA par agent sur ComeUp ([exemple](https://comeup.com/fr/service/539386/creer-un-agent-ia-whatsapp-personnalise)), et formations gratuites ponctuelles (Force-N, EEIA) aux dates limitées. Argument pour nous : pour moins que le prix d'un agent, on apprend à en faire autant qu'on veut.

Ce que la recherche n'a pas trouvé : un vendeur francophone africain de formation IA à petit prix avec une page soignée. La place est libre, c'est un argument pour une identité très propre.

---

## 3. Les 3 pistes

Règles communes aux 3 :
- Fond clair partout ; le bleu nuit n'apparaît qu'en cartes ou bandeaux ponctuels.
- Logo existant, posé en haut à gauche sur fond clair (version transparente fournie).
- Mêmes textes, repris du tunnel actuel, tutoiement, aucun tiret cadratin, espaces insécables avant `: ? ! ;`, apostrophe typographique.
- Icônes : un seul jeu, traits fins type Lucide (licence libre), en SVG intégré. Aucun emoji comme icône (le tunnel actuel en utilise beaucoup, à abandonner).
- Photo : uniquement le vrai portrait d'Enock, détouré (le fond vert d'origine jurait avec toutes les palettes).
- Boutons : 56 px de haut minimum, cible tactile de 44 px minimum, état survol et appui, contour de focus visible clavier.
- Mouvement : très sobre, respect de « réduire les animations ».

### Piste A · « Écran clair » (fidèle à la vidéo)

**Concept** : les écrans clairs de ta pub, en vrai. Un mot s'allume en bleu électrique, le fil d'or avance comme la barre de progression de la vidéo, et l'indigo n'apparaît qu'en cartes (la bulle WhatsApp, le bandeau de l'offre).

| Rôle | Hex | Contraste vérifié |
|---|---|---|
| Fond lavande | `#F5F7FE` | |
| Cartes | `#FFFFFF` | |
| Texte (indigo nuit) | `#0C1446` | 16,3 : 1 sur fond (AA) |
| Texte secondaire | `#4A5178` | 7,2 : 1 sur fond (AA) |
| Bleu électrique (mots-clés, sélection, liens) | `#3A47D5` | 6,5 : 1 sur fond, 6,9 : 1 blanc sur bleu (AA) |
| Indigo carte (bandeaux) | `#121A57` | 16,0 : 1 texte blanc ; or dessus 8,5 : 1 (AA) |
| Or (boutons, fil, soulignés) | `#E8B53A` | texte indigo sur or 9,2 : 1 (AA) |
| Or foncé (petits textes « Offert ») | `#8A6410` | 5,4 : 1 sur blanc (AA) |
| Nuances | `#E4E8FC` bordures, `#EEF1FD` fonds d'icônes | décoratives |

- **Polices** : Plus Jakarta Sans 500/700/800 (très proche de la police de la pub) + IBM Plex Mono 500 pour les repères (« 01 · Ton bilan », prix convertis). Sans + mono, 4 graisses.
- **Boutons** : pilule or, texte indigo gras, flèche qui glisse au survol, ombre dorée douce.
- **Cartes** : blanches, coins 22 à 28 px, bordure lavande, ombre bleutée très diffuse. Réponses du quiz en lignes avec pastille d'icône ; sélection = contour bleu électrique + coche.
- **Images** : portrait détouré dans une carte indigo avec halo (comme les fonds de la vidéo), bulle WhatsApp et pastille « 24h/24 » reprises de la pub.
- **Ton** : direct, énergique, « le problème ce n'est pas toi ».
- **Signature** : le fil d'or.

### Piste B · « Diamant taillé » (accordée au violet du logo)

**Concept** : le « Blue Diamond » du logo devient le système visuel. Chaque carte et chaque bouton a deux coins taillés comme une facette, l'or sert de sertissage, l'italique violet porte l'émotion du titre.

| Rôle | Hex | Contraste vérifié |
|---|---|---|
| Fond blanc violacé | `#FAF8FD` | |
| Cartes | `#FFFFFF` | |
| Texte (aubergine nuit) | `#1A1430` | 16,8 : 1 (AA) |
| Texte secondaire | `#554C6E` | 7,5 : 1 (AA) |
| Violet logo (titres en italique, bouton) | `#47218F` | 10,6 : 1 sur fond ; blanc sur violet 11,2 : 1 (AA) |
| Violet pâle (sélection, garantie) | `#EFE9FB` | violet dessus 9,4 : 1 (AA) |
| Or (sertissage, losanges) | `#E3B65A` | décoratif ; texte aubergine sur or 9,4 : 1 |
| Or foncé (petits textes) | `#7A5512` | 6,7 : 1 sur blanc (AA) |
| Aubergine (bandeau ponctuel si besoin) | `#2A1650` | blanc 15,8 : 1 ; or 8,4 : 1 |

- **Polices** : Lora 600 et 600 italique (de la même famille d'esprit que « Blue Diamond » du logo) + Figtree 400/700 pour le texte. Serif + sans, 4 graisses.
- **Boutons** : rectangle violet à coins taillés, texte blanc, petit diamant or à droite.
- **Cartes** : coins taillés, liseré or dégradé (sertissage), ombre violette douce. Progression du quiz en 13 petits losanges (violet fait, or en cours).
- **Images** : portrait sur panneau violet très pâle, diamant au trait or derrière (repris de la couverture).
- **Ton** : plus posé, « prestige », proche du certificat.
- **Signature** : la facette taillée.

### Piste C · « Plan de construction » (la plus audacieuse, toujours claire)

**Concept** : « Building » au pied de la lettre. Papier quadrillé de plan d'architecte, annotations « fig. 01 », surligneur or sur les mots qui comptent, un bon de commande pour l'offre et un tampon « Garantie 7 jours ». Le bleu-violet électrique fait le pont entre le bleu de la pub et le violet du logo.

| Rôle | Hex | Contraste vérifié |
|---|---|---|
| Fond blanc bleuté | `#FBFBFF` + trame `#ECEEFA` (28 px) | |
| Cartes | `#FFFFFF`, contour encre 2 px | |
| Encre | `#11132E` | 17,6 : 1 (AA) |
| Texte secondaire | `#4B4F6E` | 7,7 : 1 (AA) |
| Bleu-violet électrique (bouton, sélection) | `#4C3AE3` | 6,7 : 1 sur fond ; blanc dessus 7,0 : 1 (AA) |
| Surligneur or | `#F7CC4F` | encre dessus 11,9 : 1 (AA) |
| Or foncé (« offert ») | `#80600A` | 5,8 : 1 sur blanc (AA) |
| Nuit (en-tête du bon de commande) | `#14174A` | blanc 16,8 : 1 ; or 11,0 : 1 |
| Lavande (fond photo, ombres) | `#EDEBFF` | décoratif |

- **Polices** : Bricolage Grotesque (titres en largeur étroite 78, graisses 400 à 800, une seule police variable) + JetBrains Mono 500 pour les notes. Sans + mono.
- **Boutons** : rectangle bleu-violet, contour encre, ombre portée nette décalée ; il « s'enfonce » à l'appui. Très tactile sur téléphone.
- **Cartes** : contour encre 2 px, coins 16 à 20 px, ombre lavande décalée. Quiz façon cahier des charges : lettres A à E, cases à cocher, la réponse choisie est surlignée.
- **Images** : portrait dans une « fiche » légendée (fig. 01), à côté de la liste « Ce que tu vas construire » reliée aux vrais modules (agent WhatsApp module 3, site module 4, application module 6).
- **Ton** : atelier, concret, « on construit ensemble ».
- **Signature** : le surligneur + le bon de commande.

---

## 4. Recommandation

**Piste A comme base.** La personne arrive depuis ta pub vidéo : si elle retrouve les mêmes couleurs, la même police et le même fil d'or, elle sait qu'elle est au bon endroit (continuité pub vers page, c'est ce qui réduit les abandons en première seconde). C'est aussi la piste que tu aimes déjà.

On lui ajoute deux idées de la piste C qui font vendre :
1. le **bon de commande** pour l'offre (la valeur se lit ligne par ligne, puis le prix tombe) ;
2. la liste **« Ce que tu vas construire », module par module**, dans l'accueil.

La piste B reste la bonne direction pour harmoniser plus tard le certificat et les supports « prestige ».

---

## 5. Liste anti « site IA » (vérifiée sur les 3 maquettes)
- [x] Pas de dégradé violet-bleu générique, pas de texte en dégradé, pas de néon.
- [x] Héros asymétrique avec une vraie photo, un seul bouton principal.
- [x] Pas de grille de 3 cartes identiques avec emoji.
- [x] Aucun emoji comme icône, un seul jeu d'icônes SVG.
- [x] Pas d'illustration 3D ni de photo de stock.
- [x] Aucun lorem ipsum, textes repris du tunnel réel.
- [x] Guillemets français, espaces insécables, apostrophe typographique, pas de césure dans les titres et boutons.
- [x] Aucun débordement horizontal à 390 px (vérifié par script sur les 3 pistes).
- [x] Contrastes AA vérifiés par calcul (tableaux ci-dessus).
- [x] Poids mesuré : A 108 Ko, B 135 Ko, C 214 Ko (polices comprises).

---

## 6. À valider ou fournir par Enock
1. **Le choix de piste** (ou le mélange recommandé A + 2 idées de C).
2. **Incohérence dans le tunnel actuel** : le programme annonce « 49 leçons vidéo », le certificat HTML et la couverture « 57 leçons ». Les maquettes disent seulement « 8 modules » en attendant le bon chiffre.
3. **Le certificat** (`certificat.png`) écrit « Certificat **AI** Business Building », pas « IA », et ses couleurs (orange, crème, ruban rouge) ne vont avec aucune des 3 pistes. À refaire dans la piste choisie.
4. **Ton titre exact** sous ta photo : « Ton formateur · Cotonou » est une proposition.
5. **Le nombre de questions du quiz** : 13 étapes comptées dans le tunnel actuel (prénom et email compris). Les maquettes l'affichent ; à ajuster si le futur quiz change.
6. **La police de ta vidéo** : la piste A suppose Plus Jakarta Sans (très ressemblante). Si ton outil de montage indique une autre police, on l'alignera.
7. **Les preuves sociales** : le widget d'avis Chariow et les notifications de vente réelles seront à réintégrer à la construction ; garde-les seulement s'ils affichent de vrais clients.
8. **En production** : polices auto-hébergées et réduites aux caractères français (plus rapide en 3G que Google Fonts).
