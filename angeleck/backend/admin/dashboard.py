"""
INTERFACE ADMIN ANGELECK OS (Module 8) — tableau de contrôle Streamlit.

Permet de visualiser :
  * l'état système (Ollama, mémoire vectorielle, DB) ;
  * les agents actifs (natifs) et les agents créés automatiquement ;
  * l'historique des tâches (TaskLog) ;
  * un panneau pour recruter manuellement un agent.

Le dashboard interroge l'API Angeleck (POST/GET /api/...). Il a besoin d'un
token admin : connectez-vous via la barre latérale.

Lancement :
    streamlit run admin/dashboard.py
"""
from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.environ.get("ANGELECK_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Angeleck OS — Command Center", page_icon="🛡️", layout="wide")


# --------------------------------------------------------------------------- #
def api_get(path: str, token: str):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{API_URL}{path}", headers=headers, timeout=30)


def api_post(path: str, token: str, json=None, data=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.post(f"{API_URL}{path}", headers=headers, json=json, data=data, timeout=120)


def login(email: str, password: str) -> str | None:
    """Récupère un token via le password flow OAuth2."""
    resp = requests.post(
        f"{API_URL}/api/auth/login",
        data={"username": email, "password": password},
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json()["access_token"]
    st.sidebar.error(f"Connexion échouée : {resp.status_code}")
    return None


# --------------------------------------------------------------------------- #
#  Barre latérale — authentification
# --------------------------------------------------------------------------- #
st.sidebar.title("🛡️ Angeleck OS")
st.sidebar.caption("Command Center — EMK Blue Diamond")

if "token" not in st.session_state:
    st.session_state.token = None

with st.sidebar.form("auth"):
    email = st.text_input("Email", value="admin@angeleck.os")
    password = st.text_input("Mot de passe", type="password")
    if st.form_submit_button("Se connecter"):
        st.session_state.token = login(email, password)

token = st.session_state.token
if not token:
    st.info("Connectez-vous dans la barre latérale pour accéder au tableau de bord.")
    st.stop()

st.sidebar.success("Connecté ✓")

# --------------------------------------------------------------------------- #
#  En-tête — état système
# --------------------------------------------------------------------------- #
st.title("Tableau de contrôle Angeleck OS")

status_resp = api_get("/api/system/status", token)
status = status_resp.json() if status_resp.ok else {}

c1, c2, c3, c4 = st.columns(4)
ollama = status.get("ollama", {})
c1.metric("Ollama", "🟢 En ligne" if ollama.get("online") else "🔴 Hors ligne")
c2.metric("Modèles installés", len(ollama.get("models", [])))
c3.metric("Agents actifs", status.get("agents", {}).get("count", 0))
c4.metric(
    "Mémoire longue",
    "🟢 Active" if status.get("vector_memory", {}).get("enabled") else "⚪ Inactive",
)

st.divider()

# --------------------------------------------------------------------------- #
#  Agents
# --------------------------------------------------------------------------- #
st.subheader("🤖 Agents")
agents_resp = api_get("/api/agents", token)
agents = agents_resp.json().get("agents", []) if agents_resp.ok else []

native = [a for a in agents if a.get("origin") == "native"]
generated = [a for a in agents if a.get("origin") == "generated"]

col_n, col_g = st.columns(2)
with col_n:
    st.markdown(f"**Agents natifs ({len(native)})**")
    for a in native:
        with st.expander(f"{a['name']} — `{a['key']}`"):
            st.write(a["role"])
            st.caption("Compétences : " + ", ".join(a.get("skills", [])))
            st.caption("Outils : " + (", ".join(a.get("tools", [])) or "aucun"))

with col_g:
    st.markdown(f"**Agents créés automatiquement ({len(generated)})**")
    if not generated:
        st.caption("Aucun agent généré pour l'instant.")
    for a in generated:
        with st.expander(f"⚡ {a['name']} — `{a['key']}`"):
            st.write(a["role"])
            st.caption("Compétences : " + ", ".join(a.get("skills", [])))
            st.caption("Outils : " + (", ".join(a.get("tools", [])) or "aucun"))

st.divider()

# --------------------------------------------------------------------------- #
#  Recrutement manuel
# --------------------------------------------------------------------------- #
st.subheader("➕ Recruter un nouvel agent")
with st.form("recruit"):
    skill = st.text_input("Compétence / spécialité", placeholder="ex: Analyse de campagnes TikTok")
    context = st.text_area("Contexte (optionnel)")
    if st.form_submit_button("Créer l'agent") and skill:
        with st.spinner("Le cerveau recrute un agent…"):
            r = api_post("/api/create-agent", token, json={"skill": skill, "context": context})
        if r.ok:
            st.success(f"Agent créé : {r.json()['agent']['name']}")
            st.rerun()
        else:
            st.error(f"Échec : {r.status_code} — {r.text}")

st.divider()

# --------------------------------------------------------------------------- #
#  Tester le cerveau
# --------------------------------------------------------------------------- #
st.subheader("💬 Tester le cerveau central")
with st.form("chat"):
    msg = st.text_area("Demande", placeholder="Crée une publicité Facebook pour mon produit")
    if st.form_submit_button("Envoyer") and msg:
        with st.spinner("Traitement par le cerveau…"):
            r = api_post("/api/chat", token, json={"message": msg})
        if r.ok:
            data = r.json()
            st.markdown(data["answer"])
            st.caption("Agents utilisés : " + (", ".join(data["agents_used"]) or "—"))
            if data.get("recruited"):
                st.info(f"Nouvel agent recruté : {data['recruited']}")
        else:
            st.error(f"Échec : {r.status_code} — {r.text}")
