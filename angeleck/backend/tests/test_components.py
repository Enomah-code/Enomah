"""
Tests unitaires des composants ne nécessitant aucun service externe
(ni Ollama, ni PostgreSQL, ni Redis).

Lancement : cd backend && pytest -q
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_config_loads():
    from app.config import get_settings

    s = get_settings()
    assert s.app_name == "Angeleck OS"
    assert s.api_prefix == "/api/v1"


def test_password_hashing_roundtrip():
    from app.security import hash_password, verify_password

    h = hash_password("supersecret123")
    assert h != "supersecret123"
    assert verify_password("supersecret123", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    from app.security import create_access_token, decode_token

    token = create_access_token("user-123", {"email": "a@b.c"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["email"] == "a@b.c"
    assert decode_token("garbage.token.value") is None


def test_initial_agents_defined():
    from app.agents.definitions import INITIAL_AGENTS

    keys = {a.key for a in INITIAL_AGENTS}
    assert {"copywriting", "marketing", "code", "visual", "data_analyst"} <= keys
    for agent in INITIAL_AGENTS:
        assert agent.name and agent.role and agent.system_prompt


def test_tool_registry_resolves():
    from app.tools import TOOL_REGISTRY, resolve_tools

    assert "web_search" in TOOL_REGISTRY
    tools = resolve_tools(["web_search", "run_python", "inconnu"])
    assert len(tools) == 2


def test_factory_json_extraction():
    from app.factory.recruiter import _extract_json

    raw = '```json\n{"key": "fb_ads", "name": "Facebook Ads Specialist"}\n```'
    data = _extract_json(raw)
    assert data["key"] == "fb_ads"
    assert _extract_json("pas de json ici") is None


def test_intent_json_extraction():
    from app.brain.intent import _extract_json

    raw = 'Voici: {"intent": "vendre", "agents": ["marketing"], "missing_skill": false}'
    data = _extract_json(raw)
    assert data["intent"] == "vendre"
    assert data["agents"] == ["marketing"]


def test_schemas_validation():
    import pytest
    from pydantic import ValidationError

    from app.models import UserCreate

    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="x")  # mdp trop court + email KO

    ok = UserCreate(email="a@b.com", password="longenough123")
    assert ok.email == "a@b.com"
