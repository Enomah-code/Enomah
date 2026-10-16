"""Nettoyage de la voix off (enregistrement WhatsApp trop bas, avec écho de pièce).
1. WPE (déréverbération par prédiction linéaire, nara_wpe) : retire une partie de la queue d'écho de la pièce.
2. DeepFilterNet3 (réseau de rehaussement de la parole, venv séparé car il exige torchaudio) :
   souffle + écho résiduel entre les mots.
3. chaîne ffmpeg : passe-haut, coupe de la boue 250-400 Hz, présence 3-5 kHz, de-esser,
   compresseur doux PUIS expandeur (sinon le compresseur remonte l'écho), -16 LUFS.
Variables : DF_PY (python du venv DeepFilterNet), DF_MODEL (dossier du modèle DF3).
Usage : python3 scripts/voice.py entrée.aac sortie.wav
"""
import subprocess
import sys

import os
import tempfile

import numpy as np
import soundfile as sf
from nara_wpe.utils import istft, stft
from nara_wpe.wpe import wpe

SR = 48000


def load(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def dereverb(x):
    size, shift = 1024, 256
    Y = stft(x[None], size=size, shift=shift).transpose(2, 0, 1)        # (F, D, T)
    Z = np.concatenate([wpe(Y[f:f + 24], taps=40, delay=2, iterations=5, statistics_mode="full")
                        for f in range(0, Y.shape[0], 24)])                 # par bandes : mémoire bornée
    return istft(Z.transpose(1, 2, 0), size=size, shift=shift)[0][: len(x)]


def deepfilter(x):
    d = tempfile.mkdtemp()
    sf.write(f"{d}/in.wav", x / (np.abs(x).max() + 1e-9) * 0.7, SR)
    subprocess.run([os.environ["DF_PY"], "-m", "df.enhance", "-m", os.environ["DF_MODEL"], f"{d}/in.wav", "-o", d],
                   check=True, capture_output=True)
    y, _ = sf.read(f"{d}/in_DF3.wav")
    return y


def main():
    src, dst = sys.argv[1], sys.argv[2]
    x = load(src)
    x = x / (np.abs(x).max() + 1e-9) * 0.5
    y = deepfilter(dereverb(x))
    tmp = dst + ".tmp.wav"
    sf.write(tmp, y / (np.abs(y).max() + 1e-9) * 0.7, SR)
    chain = ",".join([
        "highpass=f=85:poles=2",
        "equalizer=f=320:t=q:w=1.0:g=-4",          # boue / résonance de pièce
        "equalizer=f=180:t=q:w=1.2:g=1.5",          # corps de la voix
        "equalizer=f=3800:t=q:w=1.2:g=3.5",         # présence / intelligibilité
        "equalizer=f=9500:t=q:w=1.0:g=1.5",         # air
        "deesser=i=0.35",
        "acompressor=threshold=0.12:ratio=2.5:attack=10:release=180:makeup=1.5",
        "agate=threshold=0.03:ratio=2:attack=4:release=140:range=0.3",     # expandeur doux
        "loudnorm=I=-16:TP=-1.5:LRA=8",
        "aresample=48000",
    ])
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-af", chain, "-ar", str(SR), dst], check=True)
    subprocess.run(["rm", "-f", tmp])
    print("voix ok →", dst)


if __name__ == "__main__":
    main()
