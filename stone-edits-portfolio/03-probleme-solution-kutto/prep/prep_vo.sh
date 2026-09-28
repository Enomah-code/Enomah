#!/usr/bin/env bash
# Voice-over: master the single take, then cut it into lines placed on the picture beats.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p assets/vo
ffmpeg -nostdin -y -v error -i prep/vo_take.mp3 -af "highpass=f=85,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,loudnorm=I=-14:TP=-1.5:LRA=7" -ar 48000 -ac 1 /tmp/vo_master.wav
# id  src_in  src_out
while read -r id a b; do
  d=$(python3 -c "print(round($b-$a,3))")
  ffmpeg -nostdin -y -v error -ss "$a" -t "$d" -i /tmp/vo_master.wav -af "afade=t=in:d=0.012,afade=t=out:st=$(python3 -c "print(round($d-0.05,3))"):d=0.05" assets/vo/$id.wav
done <<'LINES'
v01 0.00 1.64
v02 2.05 4.30
v03 4.60 5.26
v04 5.50 7.88
v05 8.18 8.93
v06 9.07 10.56
v07 10.83 12.53
v08 12.90 14.64
v09 14.96 16.14
v10 16.43 17.72
v11 17.94 19.25
v12 19.55 21.85
v13 22.29 24.35
LINES
# synthesised hits
ffmpeg -nostdin -y -v error -f lavfi -i "aevalsrc='0.9*sin(2*PI*(38*t+ (110-38)*0.25*(1-exp(-t/0.25))))*exp(-t/0.45)':s=48000:d=1.4" -af "lowpass=f=180,volume=1.6,alimiter=limit=0.9" assets/fx/subdrop.wav
ffmpeg -nostdin -y -v error -f lavfi -i "anoisesrc=c=pink:a=0.8:d=0.5:r=48000" -af "highpass=f=1200,lowpass=f=9000,afade=t=in:d=0.28:curve=exp,afade=t=out:st=0.3:d=0.2" assets/fx/swish.wav
