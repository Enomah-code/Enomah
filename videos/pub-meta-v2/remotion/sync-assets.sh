#!/bin/sh
# Copie les assets partagés (même audio, mêmes données que la variante HyperFrames)
set -e
cd "$(dirname "$0")"
cp ../shared/timeline.json ../shared/content.json src/data/
cp ../shared/audio/mix.wav ../shared/img/certificat.png ../shared/img/formation-vignette.png public/
