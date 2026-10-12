# Règle de commission — Studio OS

Décidée par le fondateur le 30 septembre 2026. Fait foi pour le code (`packages/payments`, `packages/pricing`) et les documents légaux.

## La règle

| Statut du créateur | Condition | Commission |
|---|---|---|
| **Standard** | Par défaut, dès l'inscription | **15 %** de chaque commande |
| **Confirmé** | Total cumulé des ventes depuis l'inscription ≥ **4 000 000 FCFA** | **10 %** de chaque commande, à partir du 1er jour du mois suivant, **définitivement** |

- Le taux s'applique à **toute la commande** (pas de palier par tranche).
- Le statut Confirmé est **acquis** : il ne se perd pas, même si les ventes baissent ensuite.
- Il n'y a ni abonnement ni frais d'inscription.

## Précisions pour l'implémentation

1. **Ce qui compte dans le cumul** : le montant des commandes dont les fonds ont été **libérés** au créateur (validation du client ou validation automatique), **moins les remboursements**. Une commande en séquestre ou en litige ne compte pas encore. Cela empêche de franchir le seuil avec des commandes qui seront annulées.
2. **Montant pris en compte** : le montant payé par le client pour la prestation, hors frais de service éventuels facturés au client.
3. **Devises** : le seuil est défini en francs CFA (XOF).
   - Euro : parité fixe **1 € = 655,957 FCFA**, soit un seuil de **6 097,96 €**.
   - Dollar et autres devises : conversion au cours du jour où les fonds sont libérés, enregistrée avec la commande (le cumul ne varie donc pas après coup avec les cours).
   - Le cumul est stocké en XOF (entier, sans décimale).
4. **Date de passage** : le mois où le cumul franchit le seuil reste à 15 % en entier. Le passage à 10 % s'applique aux commandes **acceptées et payées à partir du 1er du mois suivant**, à 00:00 heure du Bénin (UTC+1).
5. **Commande en cours au moment du passage** : elle garde le taux de la date de son paiement. Le taux est figé dans la commande au paiement.
6. **Remboursement après passage** : il réduit le cumul mais ne retire pas le statut Confirmé.
7. **Affichage** : le créateur voit dans son tableau de bord son cumul, le seuil, la barre de progression et la date de passage prévue. Il est prévenu par e-mail quand il atteint le seuil.
8. **Traçabilité** : chaque changement de statut est journalisé (date, cumul au moment du franchissement, commande qui l'a déclenché).

## Exemples

- Awa s'inscrit en janvier. En mars, une commande libérée porte son cumul à 4 150 000 FCFA. Ses commandes de mars restent à 15 %. À partir du 1er avril, toutes ses commandes sont à 10 %, pour toujours.
- Liam, basé en France, vend en euros. Son cumul atteint 6 200 € (4 066 933 FCFA) le 20 juin : 10 % à partir du 1er juillet.
- Une commande de 500 000 FCFA payée le 30 mars et livrée le 10 avril : taux figé au paiement, donc 15 %.

## Points à confirmer par le juriste et l'expert-comptable
- Mention claire de la règle dans les conditions créateurs.
- Traitement fiscal de la commission (TVA sur la commission au Bénin, facture de commission au créateur).
