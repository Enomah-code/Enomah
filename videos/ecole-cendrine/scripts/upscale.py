"""Agrandissement x4 des photos (Real-ESRGAN x4plus via spandrel), traitement par tuiles avec recouvrement.
Les photos fournies font 1080 px de large (784 px pour les .webp) : sans cela, un cadrage 9:16 serait flou.
Usage : python3 scripts/upscale.py modèle.pth entrée... (écrit assets/up/<nom>.png)
"""
import os
import sys

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
torch.set_num_threads(os.cpu_count())


def run(model, img, tile=256, pad=16):
    x = torch.from_numpy(np.asarray(img).astype(np.float32) / 255).permute(2, 0, 1)[None]
    _, _, h, w = x.shape
    out = torch.zeros(1, 3, h * 4, w * 4)
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            ya, yb, xa, xb = max(0, y0 - pad), min(h, y0 + tile + pad), max(0, x0 - pad), min(w, x0 + tile + pad)
            with torch.no_grad():
                o = model(x[:, :, ya:yb, xa:xb])
            cy, cx = (y0 - ya) * 4, (x0 - xa) * 4
            th, tw = (min(h, y0 + tile) - y0) * 4, (min(w, x0 + tile) - x0) * 4
            out[:, :, y0 * 4:y0 * 4 + th, x0 * 4:x0 * 4 + tw] = o[:, :, cy:cy + th, cx:cx + tw]
    return Image.fromarray((out[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255 + 0.5).astype(np.uint8))


def main():
    model = ModelLoader().load_from_file(sys.argv[1]).model.eval()
    os.makedirs(os.path.join(ROOT, "assets/up"), exist_ok=True)
    for p in sys.argv[2:]:
        name = os.path.splitext(os.path.basename(p))[0]
        dst = os.path.join(ROOT, f"assets/up/{name}.png")
        if os.path.exists(dst):
            continue
        im = run(model, Image.open(p).convert("RGB"))
        im.save(dst)
        print(name, im.size, flush=True)


if __name__ == "__main__":
    main()
