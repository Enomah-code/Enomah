"""
Shared voice-over script + timing for the Money Boost promo.

Both the offline Piper path (soundtrack.py) and the exact voice-clone path
(voice_clone.py, XTTS-v2) import SCENES/LEAD/TAIL/GAP from here, so the spoken
content and the dramatic cadence stay identical whichever backend is used.

Diction is copied from the reference promo: short, punchy, declarative lines
delivered slowly with a real silence between each (the reference sits at ~54%
speech with ~0.8s pauses). Each phrase is synthesised on its own and the scene
is re-assembled with a GAP silence, reproducing that posed, premium delivery.
"""

# ---------------- scenes : (min_dur, [phrases]) ----------------
SCENES = [
    (3.2, ["Ton téléphone.", "Tu l'as en main toute la journée."]),
    (3.6, ["Et s'il pouvait te rapporter…", "bien plus que ton salaire ?"]),
    (5.4, ["En Afrique, des milliers l'ont déjà compris.",
           "Cinquante mille. Cent mille. Cinq cent mille francs par mois.",
           "Avec un simple téléphone."]),
    (5.2, ["Sans capital.", "Sans diplôme.", "Sans expérience.", "Juste la bonne méthode."]),
    (5.2, ["Voici le Pack Money Boost.", "Ton accélérateur de revenus."]),
    (8.8, ["Quinze services digitaux, prêts à vendre.",
           "Cinquante scripts WhatsApp.", "Cent idées de produits.",
           "Et le plan complet.", "De zéro… à un million de francs."]),
    (6.6, ["Et ça marche déjà.",
           "Voici les premiers revenus de ceux qui sont passés à l'action."]),
    (10.5, ["Aujourd'hui, c'est moins cinquante-trois pour cent.",
            "Quatre mille quatre cent cinquante francs.", "Au lieu de neuf mille cinq cents.",
            "L'offre est limitée.", "Télécharge ton pack maintenant.",
            "Le lien est juste en dessous."]),
]
LEAD = 0.45   # voice starts this long after the scene begins
TAIL = 0.75   # silence kept after the voice before the next scene
GAP  = 0.42   # dramatic silence inserted between phrases within a scene
