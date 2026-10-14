"""Suivi des mains (MediaPipe Tasks) sur un intervalle d'un rush → JSON [t, mains[{cx,cy,tip_x,tip_y,open}]]
Coordonnées normalisées (0-1) dans l'image verticale 1440x2560. Usage: hands.py rush.mp4 t0 t1 out.json"""
import sys, json, subprocess, numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
W, H = 720, 1280
opt = vision.HandLandmarkerOptions(base_options=BaseOptions(model_asset_path="" + __import__("os").environ.get("MP_MODELS", "models") + "/hand_landmarker.task"),
                                   running_mode=vision.RunningMode.VIDEO, num_hands=2, min_hand_detection_confidence=0.3, min_tracking_confidence=0.3)
lm = vision.HandLandmarker.create_from_options(opt)
fps = 30
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", src, "-vf", f"fps={fps},scale={W}:{H}",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
res = []
for i, f in enumerate(frames):
    r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)), int(i * 1000 / fps))
    hs = []
    for h, hd in zip(r.hand_landmarks, r.handedness):
        p = np.array([[q.x, q.y] for q in h])
        palm = p[[0, 5, 9, 13, 17]].mean(0)
        tips = p[[4, 8, 12, 16, 20]]
        spread = float(np.linalg.norm(tips - palm, axis=1).mean() / (np.linalg.norm(p[9] - p[0]) + 1e-6))
        hs.append({"side": hd[0].category_name, "cx": round(float(palm[0]), 4), "cy": round(float(palm[1]), 4),
                   "ix": round(float(p[8][0]), 4), "iy": round(float(p[8][1]), 4), "open": round(spread, 3)})
    res.append({"t": round(t0 + i / fps, 3), "hands": hs})
json.dump(res, open(out, "w"))
print(len(res), "images,", sum(1 for r in res if r["hands"]), "avec mains")
