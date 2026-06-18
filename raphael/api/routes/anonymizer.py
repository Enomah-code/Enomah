"""Routes d'anonymisation d'images et de vidéos.

Image : Claude détecte les IPI et renvoie les zones à flouter (en %) ; le flouage
est appliqué côté client (canvas).

Vidéo : traitement en tâche de fond — visages floutés en local (OpenCV) sur chaque
image + Claude sur des images échantillonnées pour le texte. Voir
`raphael.tools.video_anonymizer`.

La clé API Anthropic reste côté serveur : le navigateur n'y a jamais accès.
"""
import shutil
import tempfile
import uuid
from pathlib import Path

import anthropic
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from loguru import logger

from raphael.config import get_settings
from raphael.tools.pii_detection import DETECTION_PROMPT, detect_pii

router = APIRouter(prefix="/anonymize", tags=["Anonymiseur"])

# Dossier temporaire pour les vidéos en cours / terminées.
_VIDEO_DIR = Path(tempfile.gettempdir()) / "raphael_anonymizer"
_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


# ─── IMAGE ────────────────────────────────────────────────────────────────────
class DetectRequest(BaseModel):
    """Image encodée en base64 (sans le préfixe data:...;base64,)."""

    image_base64: str
    media_type: str = "image/jpeg"


class PiiRegion(BaseModel):
    type: str
    description: str = ""
    x: float
    y: float
    width: float
    height: float


class DetectResponse(BaseModel):
    regions: list[PiiRegion] = []
    count: int = 0


@router.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest) -> DetectResponse:
    """Détecte les IPI d'une image et renvoie les zones à flouter (en %)."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY non configurée côté serveur.")

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        raw_regions = await detect_pii(
            client, request.image_base64, request.media_type, settings.specialist_model, DETECTION_PROMPT
        )
    except anthropic.APIError as exc:
        logger.error("Erreur API Anthropic lors de la détection IPI: {}", exc)
        raise HTTPException(status_code=502, detail=f"Erreur API Anthropic: {exc}") from exc

    regions = [PiiRegion(**r) for r in raw_regions]
    return DetectResponse(regions=regions, count=len(regions))


# ─── VIDÉO ────────────────────────────────────────────────────────────────────
class VideoJobCreated(BaseModel):
    job_id: str


class VideoJobStatus(BaseModel):
    job_id: str
    status: str            # queued | processing | done | error
    progress: int = 0
    message: str = ""
    stats: dict | None = None


def _import_video_engine():
    """Import paresseux : opencv/imageio-ffmpeg ne sont chargés que si la vidéo est utilisée."""
    try:
        from raphael.tools import video_anonymizer
        return video_anonymizer
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Dépendances vidéo manquantes (opencv-python, imageio-ffmpeg). "
                "Installez-les : pip install -r requirements.txt"
            ),
        ) from exc


@router.post("/video", response_model=VideoJobCreated)
async def anonymize_video(file: UploadFile = File(...)) -> VideoJobCreated:
    """Lance l'anonymisation d'une vidéo (visages + texte) en tâche de fond."""
    engine = _import_video_engine()

    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(status_code=400, detail="Le fichier fourni n'est pas une vidéo.")

    job_id = uuid.uuid4().hex
    suffix = Path(file.filename or "video.mp4").suffix or ".mp4"
    input_path = _VIDEO_DIR / f"{job_id}_in{suffix}"
    output_path = _VIDEO_DIR / f"{job_id}_anonymise.mp4"

    # Écrit le fichier uploadé sur disque en streaming (gros fichiers).
    try:
        with input_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)
    finally:
        await file.close()

    engine.JOBS[job_id] = {"status": "queued", "progress": 0, "message": "En file d'attente…"}
    engine.schedule_job(job_id, str(input_path), str(output_path))
    logger.info("Job vidéo {} créé ({})", job_id, file.filename)
    return VideoJobCreated(job_id=job_id)


@router.get("/video/{job_id}", response_model=VideoJobStatus)
async def video_status(job_id: str) -> VideoJobStatus:
    """Renvoie l'état d'avancement d'un job vidéo."""
    engine = _import_video_engine()
    job = engine.JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job introuvable.")
    return VideoJobStatus(
        job_id=job_id,
        status=job.get("status", "unknown"),
        progress=job.get("progress", 0),
        message=job.get("message", ""),
        stats=job.get("stats"),
    )


@router.get("/video/{job_id}/download")
async def video_download(job_id: str):
    """Télécharge la vidéo anonymisée une fois le traitement terminé."""
    engine = _import_video_engine()
    job = engine.JOBS.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job introuvable.")
    if job.get("status") != "done":
        raise HTTPException(status_code=409, detail="Le traitement n'est pas terminé.")
    output_path = job.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(status_code=404, detail="Fichier de sortie introuvable.")
    return FileResponse(output_path, media_type="video/mp4", filename=f"video_anonymisee_{job_id}.mp4")
