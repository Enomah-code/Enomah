"""Moteur d'anonymisation vidéo (hybride).

Stratégie :
- **Visages** : détection locale (OpenCV Haar cascades) sur CHAQUE image — rapide,
  gratuit, pas d'appel API.
- **Texte / IPI graphiques** (noms, numéros, adresses…) : Claude est interrogé sur
  des images **échantillonnées** (1 toutes les `SAMPLE_INTERVAL_SEC` secondes), et
  les zones détectées sont propagées aux images de l'intervalle.

Le traitement tourne en tâche de fond. L'audio d'origine est réintégré et la vidéo
est ré-encodée en H.264 (compatible navigateur) via le ffmpeg embarqué par
`imageio-ffmpeg` — aucune installation manuelle de ffmpeg n'est nécessaire.
"""
import asyncio
import base64
import subprocess
import time
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import anthropic
import imageio_ffmpeg
from loguru import logger

from raphael.config import get_settings
from raphael.tools.pii_detection import detect_pii, TEXT_DETECTION_PROMPT

# ─── PARAMÈTRES ──────────────────────────────────────────────────────────────
MAX_DURATION_SEC = 10 * 60 + 30          # ~10 min (petite marge)
SAMPLE_INTERVAL_SEC = 2.0                # 1 image envoyée à Claude toutes les 2 s
CLAUDE_CONCURRENCY = 5                   # appels Claude simultanés max
DETECT_MAX_DIM = 720                     # downscale pour la détection de visages
BLUR_MARGIN = 0.12                       # marge ajoutée autour des visages détectés

# ─── ÉTAT DES JOBS (en mémoire — process uvicorn unique) ─────────────────────
JOBS: dict[str, dict[str, Any]] = {}

# Références fortes aux tâches de fond, pour éviter qu'asyncio ne les ramasse.
_BG_TASKS: set = set()


def schedule_job(job_id: str, input_path: str, output_path: str) -> None:
    """Planifie le traitement en tâche de fond en conservant une référence à la tâche."""
    task = asyncio.create_task(run_video_job(job_id, input_path, output_path))
    _BG_TASKS.add(task)
    task.add_done_callback(_BG_TASKS.discard)

# ─── CASCADES OPENCV (embarquées avec opencv-python) ─────────────────────────
_FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_PROFILE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")


def _set(job_id: str, **kwargs: Any) -> None:
    job = JOBS.get(job_id)
    if job is not None:
        job.update(kwargs)


# ─── FLOUTAGE ────────────────────────────────────────────────────────────────
def _pixelate(frame: np.ndarray, x: int, y: int, w: int, h: int) -> None:
    """Pixelise une région du frame (in place)."""
    fh, fw = frame.shape[:2]
    x, y = max(0, x), max(0, y)
    w, h = min(w, fw - x), min(h, fh - y)
    if w <= 0 or h <= 0:
        return
    roi = frame[y : y + h, x : x + w]
    block = max(8, min(w, h) // 5)
    small = cv2.resize(roi, (max(1, w // block), max(1, h // block)), interpolation=cv2.INTER_LINEAR)
    frame[y : y + h, x : x + w] = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)


def _detect_faces(frame: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Détecte les visages (frontaux + profils gauche/droite) avec une marge."""
    fh, fw = frame.shape[:2]
    scale = min(1.0, DETECT_MAX_DIM / max(fh, fw))
    small = cv2.resize(frame, None, fx=scale, fy=scale) if scale < 1.0 else frame
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    found: list[tuple[int, int, int, int]] = []
    for cascade, src in (
        (_FACE_CASCADE, gray),
        (_PROFILE_CASCADE, gray),
        (_PROFILE_CASCADE, cv2.flip(gray, 1)),  # profils orientés dans l'autre sens
    ):
        flipped = src is not gray
        rects = cascade.detectMultiScale(src, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))
        for (x, y, w, h) in rects:
            if flipped:
                x = src.shape[1] - x - w
            found.append((x, y, w, h))

    # Remise à l'échelle + marge.
    boxes: list[tuple[int, int, int, int]] = []
    inv = 1.0 / scale
    for (x, y, w, h) in found:
        x, y, w, h = x * inv, y * inv, w * inv, h * inv
        mx, my = w * BLUR_MARGIN, h * BLUR_MARGIN
        boxes.append((int(x - mx), int(y - my), int(w + 2 * mx), int(h + 2 * my)))
    return boxes


def _pct_to_box(region: dict, fw: int, fh: int) -> tuple[int, int, int, int]:
    """Convertit une zone Claude (pourcentages) en pixels."""
    x = int(region["x"] / 100 * fw)
    y = int(region["y"] / 100 * fh)
    w = int(region["width"] / 100 * fw)
    h = int(region["height"] / 100 * fh)
    return x, y, w, h


# ─── PHASES (bloquantes — exécutées dans un thread) ──────────────────────────
def _probe(input_path: str) -> dict[str, Any]:
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("Vidéo illisible ou format non supporté.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    if total <= 0:
        # Certains conteneurs ne renseignent pas le compte : on le considère inconnu.
        total = 0
    duration = total / fps if total else 0
    return {"fps": fps, "total": total, "width": w, "height": h, "duration": duration}


def _extract_samples(input_path: str, fps: float, total: int) -> list[tuple[int, bytes]]:
    """Extrait les images échantillonnées (JPEG) à envoyer à Claude."""
    step = max(1, int(round(fps * SAMPLE_INTERVAL_SEC)))
    cap = cv2.VideoCapture(input_path)
    samples: list[tuple[int, bytes]] = []
    idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % step == 0:
            ok2, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok2:
                samples.append((idx, buf.tobytes()))
        idx += 1
    cap.release()
    return samples


def _process_full(
    job_id: str,
    input_path: str,
    silent_path: str,
    fps: float,
    total: int,
    detections: list[tuple[int, int, list[dict]]],
) -> dict[str, int]:
    """Passe complète : floute visages (chaque image) + zones Claude (par intervalle)."""
    cap = cv2.VideoCapture(input_path)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(silent_path, fourcc, fps, (w, h))

    face_count = 0
    text_zone_frames = 0
    idx = 0
    last_pct = -1
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        for (x, y, fw_, fh_) in _detect_faces(frame):
            _pixelate(frame, x, y, fw_, fh_)
            face_count += 1

        for (start, end, regions) in detections:
            if start <= idx < end:
                for region in regions:
                    bx, by, bw, bh = _pct_to_box(region, w, h)
                    _pixelate(frame, bx, by, bw, bh)
                    text_zone_frames += 1

        writer.write(frame)
        idx += 1

        if total:
            pct = int(idx / total * 100)
            if pct != last_pct:
                last_pct = pct
                # 45 % → 90 % réservés à cette phase.
                _set(job_id, progress=45 + int(pct * 0.45),
                     message=f"Floutage image {idx}/{total}…")

    cap.release()
    writer.release()
    return {"frames": idx, "faces": face_count, "text_zone_frames": text_zone_frames}


def _mux_audio(silent_path: str, input_path: str, output_path: str) -> None:
    """Ré-encode en H.264 (yuv420p) et réintègre l'audio d'origine si présent."""
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-i", silent_path,
        "-i", input_path,
        "-map", "0:v:0",
        "-map", "1:a:0?",          # audio optionnel (le `?` évite l'échec si muet)
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg a échoué: {}", result.stderr[-1000:])
        raise RuntimeError("Échec de l'encodage final (ffmpeg).")


# ─── DÉTECTION CLAUDE (asynchrone, concurrente) ──────────────────────────────
async def _detect_samples(
    job_id: str,
    samples: list[tuple[int, bytes]],
    fps: float,
    settings,
) -> list[tuple[int, int, list[dict]]]:
    """Interroge Claude sur chaque image échantillonnée, en parallèle (borné)."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    step = max(1, int(round(fps * SAMPLE_INTERVAL_SEC)))
    sem = asyncio.Semaphore(CLAUDE_CONCURRENCY)
    done = 0
    total = len(samples) or 1

    async def one(frame_idx: int, jpg: bytes) -> tuple[int, int, list[dict]]:
        nonlocal done
        async with sem:
            try:
                b64 = base64.b64encode(jpg).decode("ascii")
                regions = await detect_pii(
                    client, b64, "image/jpeg", settings.specialist_model, TEXT_DETECTION_PROMPT
                )
            except Exception as exc:  # un échec ponctuel ne doit pas tout casser
                logger.warning("Détection Claude échouée (frame {}): {}", frame_idx, exc)
                regions = []
            done += 1
            _set(job_id, progress=15 + int(done / total * 30),
                 message=f"Analyse IPI {done}/{total} images échantillonnées…")
            return (frame_idx, frame_idx + step, regions)

    return await asyncio.gather(*(one(i, j) for i, j in samples))


# ─── ORCHESTRATEUR ────────────────────────────────────────────────────────────
async def run_video_job(job_id: str, input_path: str, output_path: str) -> None:
    """Pipeline complet d'anonymisation vidéo (mis à jour dans JOBS[job_id])."""
    settings = get_settings()
    silent_path = output_path + ".silent.mp4"
    started = time.time()
    try:
        _set(job_id, status="processing", progress=2, message="Analyse de la vidéo…")
        meta = await asyncio.to_thread(_probe, input_path)

        if meta["duration"] and meta["duration"] > MAX_DURATION_SEC:
            mins = meta["duration"] / 60
            raise ValueError(f"Vidéo trop longue ({mins:.1f} min). Maximum : 10 min.")

        _set(job_id, progress=8, message="Extraction des images à analyser…", meta=meta)
        samples = await asyncio.to_thread(_extract_samples, input_path, meta["fps"], meta["total"])

        detections: list[tuple[int, int, list[dict]]] = []
        if settings.anthropic_api_key and samples:
            detections = await _detect_samples(job_id, samples, meta["fps"], settings)
        else:
            _set(job_id, message="Clé API absente : floutage des visages uniquement.")

        text_zones = sum(len(r) for _, _, r in detections)
        _set(job_id, progress=45, message="Floutage des visages et zones détectées…")
        stats = await asyncio.to_thread(
            _process_full, job_id, input_path, silent_path, meta["fps"], meta["total"], detections
        )

        _set(job_id, progress=92, message="Réintégration de l'audio et encodage final…")
        await asyncio.to_thread(_mux_audio, silent_path, input_path, output_path)

        Path(silent_path).unlink(missing_ok=True)
        _set(
            job_id,
            status="done",
            progress=100,
            message="Terminé.",
            output_path=output_path,
            stats={
                "frames": stats["frames"],
                "faces_blurred": stats["faces"],
                "text_pii_zones": text_zones,
                "duration_sec": round(meta["duration"], 1),
                "elapsed_sec": round(time.time() - started, 1),
            },
        )
        logger.info("Job vidéo {} terminé en {:.1f}s", job_id, time.time() - started)
    except Exception as exc:
        logger.exception("Job vidéo {} échoué", job_id)
        Path(silent_path).unlink(missing_ok=True)
        _set(job_id, status="error", message=str(exc))
