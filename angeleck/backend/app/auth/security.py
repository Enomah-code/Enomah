"""
Sécurité & authentification (Module 6).

Fournit :
  * hachage de mot de passe (bcrypt via passlib) ;
  * émission/validation de JWT (python-jose) ;
  * dépendances FastAPI `get_current_user` pour protéger les endpoints ;
  * helpers de création/authentification d'utilisateur.

Les sessions sont stateless (JWT Bearer). Les logs d'accès sont écrits via la
table TaskLog par la couche API.
"""
from __future__ import annotations

import datetime as dt
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.memory.database import User, get_session

logger = logging.getLogger("angeleck.auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# --- Hachage --------------------------------------------------------------- #
try:
    from passlib.context import CryptContext

    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(password: str) -> str:
        return _pwd_context.hash(password)

    def verify_password(plain: str, hashed: str) -> bool:
        return _pwd_context.verify(plain, hashed)

except ImportError:  # pragma: no cover - fallback si passlib absent
    import hashlib

    logger.warning("passlib absent — hachage SHA256 de secours (NON recommandé en prod).")

    def get_password_hash(password: str) -> str:
        return "sha256$" + hashlib.sha256(password.encode()).hexdigest()

    def verify_password(plain: str, hashed: str) -> bool:
        return get_password_hash(plain) == hashed


# --- JWT ------------------------------------------------------------------- #
def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    """Émet un JWT signé pour `subject` (user id)."""
    from jose import jwt

    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> Optional[dict]:
    from jose import JWTError, jwt

    try:
        return jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None


# --- Helpers utilisateur --------------------------------------------------- #
async def create_user(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: str = "",
    is_admin: bool = False,
) -> User:
    """Crée un utilisateur (lève si l'email existe déjà)."""
    existing = await session.scalar(select(User).where(User.email == email))
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré.")
    user = User(
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        is_admin=is_admin,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Vérifie les identifiants et renvoie l'utilisateur si valides."""
    user = await session.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# --- Dépendance FastAPI ---------------------------------------------------- #
async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Récupère l'utilisateur courant à partir du JWT Bearer."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou token manquant.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exc
    payload = _decode_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exc
    user = await session.scalar(select(User).where(User.id == payload["sub"]))
    if not user or not user.is_active:
        raise credentials_exc
    return user
