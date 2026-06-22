"""
Interface d'administration Angeleck OS (Streamlit).

Permet de :
  - voir les agents actifs et ceux créés automatiquement ;
  - consulter l'historique des missions ;
  - suivre la consommation de ressources (missions, taux de succès, Ollama).

Lancement :
    streamlit run admin/dashboard.py

L'admin s'authentifie avec un compte administrateur de l'API.
"""
import os

import requests
import streamlit as st

API_BASE = os.getenv("ANGELECK_API_URL", "http://localhost:8000/api/v1")

st.set_page_config(page_title="Angeleck OS — Admin", page_icon="🛰️", layout="wide")
st.title("🛰️ Angeleck OS — Console d'administration")


def login(email: str, password: str) -> str | None:
    try:
        resp = requests.post(
            f"{API_BASE}/auth/login",
            data={"username": email, "password": password},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()["access_token"]
        st.error(f"Connexion refusée: {resp.json().get('detail')}")
    except Exception as e:
        st.error(f"API injoignable: {e}")
    return None


# --- Authentification ---
if "token" not in st.session_state:
    st.session_state.token = None

if not st.session_state.token:
    with st.form("login"):
        st.subheader("Connexion administrateur")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.form_submit_button("Se connecter"):
            token = login(email, password)
            if token:
                st.session_state.token = token
                st.rerun()
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}


def api_get(path: str):
    resp = requests.get(f"{API_BASE}{path}", headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


# --- Tableau de bord ---
try:
    stats = api_get("/admin/stats")
except Exception as e:
    st.error(f"Impossible de charger les stats (compte admin requis ?): {e}")
    if st.button("Se déconnecter"):
        st.session_state.token = None
        st.rerun()
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Utilisateurs", stats["users"])
col2.metric("Missions traitées", stats["missions_total"])
col3.metric("Taux de succès", f"{stats['success_rate'] * 100:.0f}%")
col4.metric("Agents", f"{stats['agents_total']} ({stats['agents_generated']} générés)")

ollama = stats["ollama"]
if ollama.get("available"):
    st.success(f"Ollama opérationnel — modèles: {', '.join(ollama.get('models', []))}")
else:
    st.warning("Ollama indisponible — démarrez le service Ollama.")

st.divider()
st.subheader("🤖 Agents")
st.dataframe(stats["agents"], use_container_width=True)

st.subheader("📜 Historique des missions")
try:
    missions = api_get("/admin/missions?limit=100")
    st.dataframe(missions, use_container_width=True)
except Exception as e:
    st.info(f"Aucune mission ou erreur: {e}")

if st.sidebar.button("Se déconnecter"):
    st.session_state.token = None
    st.rerun()
st.sidebar.caption("Angeleck OS Admin Console")
