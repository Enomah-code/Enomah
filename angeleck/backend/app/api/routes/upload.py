"""
Route d'upload de fichiers (POST /upload) pour analyse par les agents.
"""
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_current_user
from app.config import get_settings
from app.database.models import User
from app.tools.data_tools import UPLOAD_DIR

router = APIRouter(tags=["upload"])
settings = get_settings()

ALLOWED_EXT = {".csv", ".xlsx", ".xls", ".txt", ".json", ".pdf"}


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Reçoit un fichier, le valide et le stocke pour analyse ultérieure."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=f"Extension non autorisée. Acceptées: {sorted(ALLOWED_EXT)}",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = f"{user.id}_{uuid.uuid4().hex}{ext}"
    dest = os.path.join(UPLOAD_DIR, safe_name)

    size = 0
    max_bytes = settings.max_upload_mb * 1024 * 1024
    with open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_bytes:
                out.close()
                os.remove(dest)
                raise HTTPException(
                    status_code=413,
                    detail=f"Fichier trop volumineux (max {settings.max_upload_mb} Mo).",
                )
            out.write(chunk)

    return {
        "file_path": dest,
        "filename": file.filename,
        "size_bytes": size,
        "hint": "Transmettez file_path dans /chat pour que l'agent Oracle l'analyse.",
    }
