"""Generate a still with the Gemini image model.

usage: GEMINI_API_KEY=... python3 gen_image.py OUT.png "prompt" [--ar 1:1] [--size 2K] [--ref img.png ...] [--model gemini-3-pro-image]
The key is read from the environment only; it is never written to disk by this script.
"""
import argparse, base64, json, mimetypes, os, sys, urllib.request

p = argparse.ArgumentParser()
p.add_argument("out")
p.add_argument("prompt")
p.add_argument("--ar", default="1:1")
p.add_argument("--size", default="2K")
p.add_argument("--ref", nargs="*", default=[])
p.add_argument("--model", default="gemini-3-pro-image")
a = p.parse_args()

key = os.environ.get("GEMINI_API_KEY")
if not key:
    sys.exit("GEMINI_API_KEY is not set")

parts = []
for r in a.ref:
    mt = mimetypes.guess_type(r)[0] or "image/png"
    parts.append({"inlineData": {"mimeType": mt, "data": base64.b64encode(open(r, "rb").read()).decode()}})
parts.append({"text": a.prompt})
body = {
    "contents": [{"role": "user", "parts": parts}],
    "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": a.ar, "imageSize": a.size}},
}
req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent",
    data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
try:
    res = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}: {e.read().decode()[:800]}")
for cand in res.get("candidates", []):
    for part in cand.get("content", {}).get("parts", []):
        if "inlineData" in part:
            open(a.out, "wb").write(base64.b64decode(part["inlineData"]["data"]))
            print(a.out)
            sys.exit(0)
sys.exit("no image returned: " + json.dumps(res)[:800])
