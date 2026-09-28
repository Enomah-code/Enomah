import asyncio, ssl, os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edge_tts, edge_tts.communicate as C
from lines import LINES
C._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
meta = json.load(open("timing.json"))
async def main():
    for i, (lid, pause, text) in enumerate(LINES):
        c = edge_tts.Communicate(text, "fr-FR-RemyMultilingualNeural", rate="-6%", proxy=os.environ.get("HTTPS_PROXY"), boundary="WordBoundary")
        ws = []
        async for ch in c.stream():
            if ch["type"] == "WordBoundary": ws.append([ch["offset"]/1e7, ch["duration"]/1e7, ch["text"]])
        o = ws[0][0]
        meta[i]["words"] = [[round(meta[i]["start"] + w[0] - o, 3), round(w[1], 3), w[2]] for w in ws]
    json.dump(meta, open("timing.json", "w"), ensure_ascii=False, indent=1)
asyncio.run(main())
