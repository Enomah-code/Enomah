"""OKF Logistique — voice-over script (transcribed from the reference promo).

Each scene is reproduced in the cloned voice. Long scenes are split into short
phrases reassembled with a GAP silence, which keeps XTTS cadence natural.
"""

GAP = 0.28  # seconds of silence between phrases within a scene

SCENES = [
    ["2000 colis par mois,", "pas un seul colis perdu.", "Alors, comment on fait ?"],
    ["Tout commence à Lomé,", "Ghana, Bénin,", "et bien plus loin."],
    ["Là où les autres voient un voyage,", "nous voyons une ligne droite."],
    ["Sécurisé.", "On ne laisse rien au hasard."],
    ["Il est où mon colis ?", "Chez OKF, cette question n'existe pas."],
    ["Vous avez quelque chose à envoyer ?", "On s'en occupe."],
    ["OKF Logistique.", "Votre colis, notre responsabilité."],
]
