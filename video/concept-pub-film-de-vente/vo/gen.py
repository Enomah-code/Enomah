import asyncio, ssl, os, json, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
import edge_tts, edge_tts.communicate as C
from lines import LINES
C._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
VOICE = os.environ.get("VOICE", "fr-FR-RemyMultilingualNeural")
D = os.path.dirname(os.path.abspath(__file__))
async def one(i, text):
    out = f"{D}/l{i:02d}.mp3"
    c = edge_tts.Communicate(text, VOICE, rate="-6%", proxy=os.environ.get("HTTPS_PROXY"))
    await c.save(out)
    return out
async def main():
    t = 0.0; meta = []
    for i, (lid, pause, text) in enumerate(LINES):
        f = await one(i, text)
        # trim leading/trailing silence for tight timing
        w = f"{D}/l{i:02d}.wav"
        subprocess.run(["ffmpeg","-loglevel","error","-y","-i",f,"-af","silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse","-ar","48000","-ac","1",w],check=True)
        d = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",w]).decode())
        t += pause
        meta.append({"id": lid, "start": round(t, 3), "end": round(t + d, 3), "text": text})
        t += d
    json.dump(meta, open(f"{D}/timing.json","w"), ensure_ascii=False, indent=1)
    total = t + 2.2
    # assemble
    inputs=[]; flt=[]
    for i,m in enumerate(meta):
        inputs += ["-i", f"{D}/l{i:02d}.wav"]
        ms=int(m["start"]*1000); flt.append(f"[{i}]adelay={ms}|{ms}[a{i}]")
    mix="".join(f"[a{i}]" for i in range(len(meta)))+f"amix=inputs={len(meta)}:normalize=0,apad=whole_dur={total}[out]"
    subprocess.run(["ffmpeg","-loglevel","error","-y",*inputs,"-filter_complex",";".join(flt)+";"+mix,"-map","[out]","-ar","48000","-ac","1",f"{D}/voice.wav"],check=True)
    print("total", round(total,2))
    for m in meta: print(f'{m["start"]:7.2f} {m["end"]:7.2f}  {m["id"]}')
asyncio.run(main())
