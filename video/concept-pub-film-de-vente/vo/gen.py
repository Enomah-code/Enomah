"""Voix off : synthèse phrase par phrase, silence rogné, minutage mot à mot, assemblage."""
import asyncio, ssl, os, json, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
import edge_tts, edge_tts.communicate as C
from lines import LINES
C._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
VOICE = os.environ.get("VOICE", "fr-FR-RemyMultilingualNeural"); RATE = "-5%"
PROXY = os.environ.get("HTTPS_PROXY")
async def synth(i, text):
    c = edge_tts.Communicate(text, VOICE, rate=RATE, proxy=PROXY, boundary="WordBoundary")
    ws = []
    with open(f"{D}/l{i:02d}.mp3", "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary": ws.append([ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]])
    return ws
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]).decode())
async def main():
    t = 0.0; meta = []
    for i, (lid, pause, text, tts) in enumerate(LINES):
        ws = await synth(i, tts or text)
        w = f"{D}/l{i:02d}.wav"
        subprocess.run(["ffmpeg","-loglevel","error","-y","-i",f"{D}/l{i:02d}.mp3","-af","silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse","-ar","48000","-ac","1",w], check=True)
        d = dur(w); t += pause; o = ws[0][0]
        meta.append({"id": lid, "start": round(t, 3), "end": round(t + d, 3), "text": text,
                     "words": [[round(t + x[0] - o, 3), round(x[1], 3), x[2]] for x in ws]})
        t += d
    total = t + 2.4
    json.dump(meta, open(f"{D}/timing.json", "w"), ensure_ascii=False, indent=1)
    ins, fl = [], []
    for i, m in enumerate(meta):
        ins += ["-i", f"{D}/l{i:02d}.wav"]; ms = int(m["start"] * 1000); fl.append(f"[{i}]adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(meta))) + f"amix=inputs={len(meta)}:normalize=0,apad=whole_dur={total},loudnorm=I=-16:TP=-1.5:LRA=11[out]"
    subprocess.run(["ffmpeg","-loglevel","error","-y",*ins,"-filter_complex",";".join(fl)+";"+mix,"-map","[out]","-ar","48000","-ac","1",f"{D}/../assets/voice.wav"], check=True)
    print("TOTAL", round(total, 2))
    for m in meta: print(f'{m["start"]:7.2f} {m["end"]:7.2f}  {m["id"]}')
asyncio.run(main())
