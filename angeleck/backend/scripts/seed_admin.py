"""
Crée le compte administrateur initial à partir des variables d'environnement
ADMIN_EMAIL / ADMIN_PASSWORD.

Usage (en local) :
    python -m scripts.seed_admin
Usage (Docker) :
    docker compose exec backend python -m scripts.seed_admin
"""
from __future__ import annotations

import asyncio
import os

from app.auth.security import get_password_hash
from app.memory.database import SessionLocal, User, init_db
from sqlalchemy import select


async def main() -> None:
    email = os.environ.get("ADMIN_EMAIL", "admin@angeleck.os")
    password = os.environ.get("ADMIN_PASSWORD", "changeme123")

    await init_db()
    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing:
            print(f"✓ Admin déjà présent : {email}")
            return
        admin = User(
            email=email,
            full_name="Administrateur Angeleck",
            hashed_password=get_password_hash(password),
            is_admin=True,
        )
        session.add(admin)
        await session.commit()
        print(f"✓ Admin créé : {email} (mot de passe défini via ADMIN_PASSWORD)")


if __name__ == "__main__":
    asyncio.run(main())
