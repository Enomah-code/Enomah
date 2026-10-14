"""Suivi du visage (MediaPipe FaceLandmarker) : centre des yeux, bouche, hauteur du visage, par image (30 i/s).
Coordonnées normalisées dans l'image verticale. Usage: face.py rush.mp4 t0 t1 out.json"""
import sys, json, subprocess, numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, t0, t1, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
W, H, fps = 720, 1280, 30
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="" + __import__("os").environ.get("MP_MODELS", "models") + "/face_landmarker.task"),
    running_mode=vision.RunningMode.VIDEO, num_faces=1))
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", src, "-vf", f"fps={fps},scale={W}:{H}",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
res = []
for i, f in enumerate(fr):
    r = lm.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)), int(i * 1000 / fps))
    if r.face_landmarks:
        p = np.array([[q.x, q.y] for q in r.face_landmarks[0]])
        eyes = p[[33, 133, 362, 263]].mean(0); mouth = p[[13, 14, 61, 291]].mean(0)
        fh = float(p[152][1] - p[10][1])
        res.append({"t": round(i / fps, 3), "ex": round(float(eyes[0]), 4), "ey": round(float(eyes[1]), 4),
                    "mx": round(float(mouth[0]), 4), "my": round(float(mouth[1]), 4), "fh": round(fh, 4)})
    else:
        res.append({"t": round(i / fps, 3)})
json.dump(res, open(out, "w"))
print(len(res), "images,", sum(1 for r in res if "ex" in r), "avec visage")
