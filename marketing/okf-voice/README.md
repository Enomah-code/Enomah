# OKF — Voice Clone

Clone the voice-over from the OKF Logistique promo and make it say **any text**,
using zero-shot voice cloning (Coqui **XTTS-v2**).

## What's here

| File | Role |
|------|------|
| `prepare_ref.py` | Build a clean speaker reference (decode → isolate voice with Demucs → keep only voiced speech → high-pass + noise reduction). |
| `clone.py` | Synthesise the full promo voice-over, or any `--text`, in the cloned voice. |
| `script.py` | The OKF voice-over script (transcribed from the reference). |
| `ta_shim.py` | Routes `torchaudio` I/O through `soundfile` (skips the CUDA-only torchcodec backend). |
| `assets/speaker_ref.wav` | Ready-made 24 kHz speaker reference (~32 s of isolated, polished voice). |
| `build/` | Generated audio (git-ignored). |

## Install

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

CPU is enough (XTTS runs in ~real-time-ish per phrase). See `requirements.txt`
for the two fresh-container gotchas (Debian `setuptools`, and `docopt`).

## Use

```bash
# Reproduce the whole promo voice-over -> build/okf_voiceover.wav (+ scene_*.wav)
python3 clone.py

# Make the cloned voice say anything
python3 clone.py --text "Bonjour, votre colis OKF est arrivé à Lomé."
```

To rebuild the reference from a different source clip:

```bash
python3 prepare_ref.py --src /path/to/promo.mp4         # isolate + clean, writes assets/speaker_ref.wav
python3 prepare_ref.py --src promo.mp4 --no-isolate     # source is already clean speech
python3 prepare_ref.py --src promo.mp4 --mode window    # one loudest block instead of all voiced bits
python3 prepare_ref.py --src promo.mp4 --no-clean       # skip the high-pass + denoise polish
```

## Script (transcribed)

> 2000 colis par mois, pas un seul colis perdu. Alors, comment on fait ?
> Tout commence à Lomé, Ghana, Bénin, et bien plus loin.
> Là où les autres voient un voyage, nous voyons une ligne droite.
> Sécurisé. On ne laisse rien au hasard.
> Il est où mon colis ? Chez OKF, cette question n'existe pas.
> Vous avez quelque chose à envoyer ? On s'en occupe.
> OKF Logistique. Votre colis, notre responsabilité.

## Note

This clones a voice from a reference recording. Use it only with permission of
the original speaker / brand owner.
