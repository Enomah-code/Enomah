"""
============================================================
 Angeleck OS — VERSION LOCALE SIMPLE (un seul fichier)
============================================================

Objectif : pouvoir lancer Angeleck OS sur un PC SANS difficulté.

  * AUCUN Docker, AUCUN PostgreSQL, AUCUN ChromaDB à installer.
  * Persistance dans un simple fichier SQLite (intégré à Python).
  * Interface de chat intégrée (page web servie sur http://localhost:8000).
  * Fonctionne AVEC Ollama (vraie IA) OU SANS (mode démonstration).

Dépendances minimales : fastapi, uvicorn, httpx, python-multipart.

Lancement :
    python server.py
puis ouvrez http://localhost:8000

Powered by EMK Blue Diamond.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# --------------------------------------------------------------------------- #
#  Configuration (modifiable via variables d'environnement, sinon défauts)
# --------------------------------------------------------------------------- #
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
BRAIN_MODEL = os.environ.get("OLLAMA_BRAIN_MODEL", "llama3.1")
AGENT_MODEL = os.environ.get("OLLAMA_AGENT_MODEL", "llama3.1")
DB_PATH = os.environ.get("ANGELECK_DB", os.path.join(os.path.dirname(__file__), "angeleck.db"))
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
#  Base de données SQLite (zéro installation)
# --------------------------------------------------------------------------- #
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(db()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                agents TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS agents (
                key TEXT PRIMARY KEY,
                name TEXT,
                role TEXT,
                skills TEXT,
                system_prompt TEXT,
                origin TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS logs (
                id TEXT PRIMARY KEY,
                event TEXT,
                detail TEXT,
                created_at TEXT
            );
            """
        )
        conn.commit()


def log_event(event: str, detail: Dict[str, Any]) -> None:
    with closing(db()) as conn:
        conn.execute(
            "INSERT INTO logs (id, event, detail, created_at) VALUES (?,?,?,?)",
            (str(uuid.uuid4()), event, json.dumps(detail, ensure_ascii=False), now_iso()),
        )
        conn.commit()


# --------------------------------------------------------------------------- #
#  Agents natifs (5 experts) — Module 2
# --------------------------------------------------------------------------- #
NATIVE_AGENTS: Dict[str, Dict[str, Any]] = {
    "writer": {
        "key": "writer",
        "name": "Copywriter Agent",
        "role": "Copywriting, publicités, emails, storytelling",
        "skills": ["pages de vente", "scripts publicitaires", "emails", "storytelling"],
        "origin": "native",
        "system_prompt": (
            "Tu es le COPYWRITER AGENT d'Angeleck OS, rédacteur publicitaire de "
            "classe mondiale (frameworks AIDA, PAS, BAB). Écris des textes clairs, "
            "persuasifs et orientés conversion. Structure : accroche, corps, appel "
            "à l'action."
        ),
    },
    "marketing": {
        "key": "marketing",
        "name": "Marketing Agent",
        "role": "Stratégie, tunnel de vente, acquisition, positionnement",
        "skills": ["stratégie business", "tunnel de vente", "acquisition client", "positionnement"],
        "origin": "native",
        "system_prompt": (
            "Tu es le MARKETING AGENT d'Angeleck OS, stratège senior. Raisonne en "
            "funnel (TOFU/MOFU/BOFU), ICP, proposition de valeur et canaux "
            "d'acquisition. Livre des plans structurés, actionnables et chiffrés."
        ),
    },
    "code": {
        "key": "code",
        "name": "Code Agent",
        "role": "Scripts, automatisation, correction de bugs",
        "skills": ["écriture de scripts", "automatisation", "correction de bugs"],
        "origin": "native",
        "system_prompt": (
            "Tu es le CODE AGENT d'Angeleck OS, ingénieur logiciel expert. Produis "
            "du code correct, commenté, avec dépendances et commande d'exécution. "
            "Pour un bug : explique la cause puis donne le correctif complet."
        ),
    },
    "visual": {
        "key": "visual",
        "name": "Visual Agent",
        "role": "Prompts images/vidéos et branding",
        "skills": ["prompts images", "prompts vidéos", "branding"],
        "origin": "native",
        "system_prompt": (
            "Tu es le VISUAL AGENT d'Angeleck OS, directeur artistique. Pour les "
            "prompts : sujet, composition, style, éclairage, palette, ratio. Donne "
            "une version courte et une détaillée. Pour le branding : nom, palette "
            "(codes hex), typographies, ton."
        ),
    },
    "data": {
        "key": "data",
        "name": "Data Agent",
        "role": "Analyse CSV/Excel, rapports, statistiques",
        "skills": ["analyse CSV", "analyse Excel", "rapports", "statistiques"],
        "origin": "native",
        "system_prompt": (
            "Tu es le DATA AGENT d'Angeleck OS, data analyst senior. Interprète les "
            "données fournies, dégage tendances, anomalies et corrélations, puis "
            "donne des recommandations. Structure : constat chiffré, insights, "
            "recommandations. N'invente jamais de chiffres."
        ),
    },
}

# Mots-clés pour le routage (Module 1)
KEYWORDS = {
    "writer": ["publicité", "pub", "ad", "copy", "email", "vente", "script", "storytelling", "slogan", "accroche"],
    "marketing": ["stratégie", "marketing", "tunnel", "funnel", "acquisition", "client", "positionnement", "business", "campagne", "lancement"],
    "code": ["code", "script", "automatiser", "automatisation", "bug", "api", "programme", "développe", "fonction"],
    "visual": ["image", "vidéo", "video", "prompt", "branding", "logo", "design", "visuel", "charte"],
    "data": ["csv", "excel", "données", "data", "analyse", "statistique", "rapport", "tableau", "kpi"],
}


def all_agents() -> Dict[str, Dict[str, Any]]:
    """Agents natifs + agents générés (chargés depuis SQLite)."""
    agents = dict(NATIVE_AGENTS)
    with closing(db()) as conn:
        for row in conn.execute("SELECT * FROM agents WHERE origin='generated'"):
            agents[row["key"]] = {
                "key": row["key"],
                "name": row["name"],
                "role": row["role"],
                "skills": json.loads(row["skills"] or "[]"),
                "system_prompt": row["system_prompt"],
                "origin": "generated",
            }
    return agents


# --------------------------------------------------------------------------- #
#  Accès Ollama (optionnel)
# --------------------------------------------------------------------------- #
async def ollama_online() -> bool:
    try:
        async with httpx.AsyncClient(timeout=4) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            return r.status_code == 200
    except httpx.HTTPError:
        return False


async def ollama_models() -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
    except httpx.HTTPError:
        return []


async def ollama_chat(system: str, user: str, model: str = AGENT_MODEL) -> Optional[str]:
    """Renvoie la réponse du modèle, ou None si Ollama indisponible."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=180) as c:
            r = await c.post(f"{OLLAMA_URL}/api/chat", json=payload)
            r.raise_for_status()
            return r.json().get("message", {}).get("content", "").strip()
    except httpx.HTTPError:
        return None


# --------------------------------------------------------------------------- #
#  Cerveau central — routage + recrutement + exécution (Modules 1 & 3)
# --------------------------------------------------------------------------- #
def route(request: str) -> List[str]:
    """Choisit le(s) agent(s) par score de mots-clés. Renvoie [] si aucun."""
    text = request.lower()
    scores: Dict[str, int] = {}
    agents = all_agents()
    for key in agents:
        words = KEYWORDS.get(key, [])
        s = sum(1 for w in words if w in text)
        # Pour les agents générés, on score aussi sur leurs compétences.
        if agents[key]["origin"] == "generated":
            s += sum(1 for sk in agents[key]["skills"] if sk.lower() in text)
        if s:
            scores[key] = s
    if not scores:
        return []
    ordered = sorted(scores, key=scores.get, reverse=True)
    return ordered[:2]


async def recruit(skill: str, online: bool) -> Dict[str, Any]:
    """Crée un nouvel agent pour une compétence absente (Module 3)."""
    key = re.sub(r"[^a-z0-9_]+", "_", skill.lower()).strip("_")[:40] or f"agent_{uuid.uuid4().hex[:6]}"
    # éviter collision
    existing = all_agents()
    base, i = key, 2
    while key in existing:
        key = f"{base}_{i}"
        i += 1

    spec = None
    if online:
        prompt = (
            f"Conçois un agent expert pour la compétence : '{skill}'. "
            "Réponds en JSON: {\"name\":\"...\",\"role\":\"...\",\"skills\":[\"..\"],"
            "\"system_prompt\":\"instructions expertes\"}."
        )
        raw = await ollama_chat("Tu es le recruteur d'agents d'Angeleck OS.", prompt, BRAIN_MODEL)
        if raw:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if m:
                try:
                    spec = json.loads(m.group(0))
                except json.JSONDecodeError:
                    spec = None

    if not spec:
        # Mode démo / fallback : fiche générée par gabarit.
        spec = {
            "name": skill.title() + " Specialist Agent",
            "role": f"Agent spécialisé : {skill}",
            "skills": [skill],
            "system_prompt": (
                f"Tu es un agent expert d'Angeleck OS spécialisé dans : {skill}. "
                "Fournis des réponses précises, structurées et actionnables."
            ),
        }

    agent = {
        "key": key,
        "name": spec.get("name", key),
        "role": spec.get("role", skill),
        "skills": spec.get("skills", [skill]),
        "system_prompt": spec.get("system_prompt", ""),
        "origin": "generated",
    }
    with closing(db()) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO agents (key,name,role,skills,system_prompt,origin,created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (agent["key"], agent["name"], agent["role"], json.dumps(agent["skills"], ensure_ascii=False),
             agent["system_prompt"], "generated", now_iso()),
        )
        conn.commit()
    log_event("recruit", {"skill": skill, "key": key})
    return agent


def demo_answer(agent: Dict[str, Any], request: str) -> str:
    """Réponse de démonstration quand Ollama n'est pas disponible."""
    return (
        f"🟡 **Mode démonstration** (Ollama n'est pas lancé — réponse simulée)\n\n"
        f"**Agent sélectionné :** {agent['name']} — _{agent['role']}_\n\n"
        f"**Ta demande :** {request}\n\n"
        f"En mode réel, cet agent traiterait ta demande avec ses compétences : "
        f"{', '.join(agent['skills'])}.\n\n"
        f"👉 Pour activer la vraie IA : installe Ollama (https://ollama.com), puis "
        f"dans un terminal lance `ollama pull llama3.1`. Recharge ensuite cette page."
    )


async def handle(request: str, conversation_id: str, extra_context: str = "") -> Dict[str, Any]:
    """Pipeline complet du cerveau central."""
    online = await ollama_online()
    agents = all_agents()
    keys = route(request)
    recruited = None

    # Aucun agent ne correspond → recrutement automatique (Module 3).
    if not keys:
        new_agent = await recruit(request[:60], online)
        recruited = new_agent["key"]
        keys = [new_agent["key"]]
        agents = all_agents()

    # Exécution des agents sélectionnés.
    outputs = []
    for key in keys:
        agent = agents.get(key)
        if not agent:
            continue
        user_block = request if not extra_context else f"{request}\n\n[CONTEXTE]\n{extra_context}"
        if online:
            reply = await ollama_chat(agent["system_prompt"], user_block, AGENT_MODEL)
            reply = reply or demo_answer(agent, request)
        else:
            reply = demo_answer(agent, request)
        outputs.append({"agent": key, "name": agent["name"], "content": reply})

    # Synthèse si plusieurs agents.
    if len(outputs) > 1 and online:
        combined = "\n\n".join(f"### {o['name']}\n{o['content']}" for o in outputs)
        synth = await ollama_chat(
            "Tu es le cerveau central Angeleck OS. Synthétise les contributions des agents en une réponse cohérente.",
            f"Demande : {request}\n\n{combined}",
            BRAIN_MODEL,
        )
        answer = synth or combined
    elif outputs:
        answer = outputs[0]["content"] if len(outputs) == 1 else "\n\n".join(
            f"### {o['name']}\n{o['content']}" for o in outputs
        )
    else:
        answer = "Aucun agent disponible pour traiter la demande."

    # Mémorisation (SQLite).
    with closing(db()) as conn:
        conn.execute(
            "INSERT INTO messages (id,conversation_id,role,content,agents,created_at) VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), conversation_id, "user", request, "", now_iso()),
        )
        conn.execute(
            "INSERT INTO messages (id,conversation_id,role,content,agents,created_at) VALUES (?,?,?,?,?,?)",
            (str(uuid.uuid4()), conversation_id, "assistant", answer,
             ",".join(o["agent"] for o in outputs), now_iso()),
        )
        conn.commit()

    log_event("chat", {"agents": [o["agent"] for o in outputs], "recruited": recruited})
    return {
        "answer": answer,
        "conversation_id": conversation_id,
        "agents_used": [o["agent"] for o in outputs],
        "recruited": recruited,
        "online": online,
    }


# --------------------------------------------------------------------------- #
#  API FastAPI (Modules 5 & 7)
# --------------------------------------------------------------------------- #
app = FastAPI(title="Angeleck OS — Local", version="1.0-local")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class ChatBody(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class CreateAgentBody(BaseModel):
    skill: str


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.post("/api/chat")
async def api_chat(body: ChatBody):
    conv = body.conversation_id or str(uuid.uuid4())
    result = await handle(body.message, conv)
    return result


@app.get("/api/agents")
async def api_agents():
    agents = list(all_agents().values())
    return {"agents": agents, "count": len(agents)}


@app.post("/api/create-agent")
async def api_create_agent(body: CreateAgentBody):
    agent = await recruit(body.skill, await ollama_online())
    return {"created": True, "agent": agent}


@app.post("/api/upload")
async def api_upload(file: UploadFile = File(...), message: str = Form("Analyse ce fichier.")):
    dest = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}")
    with open(dest, "wb") as fh:
        fh.write(await file.read())
    # Lecture simple du contenu (texte/CSV) pour le contexte.
    context = ""
    try:
        with open(dest, "r", encoding="utf-8", errors="replace") as fh:
            context = fh.read()[:6000]
    except Exception:  # noqa: BLE001
        context = f"(fichier binaire : {file.filename})"
    result = await handle(message, str(uuid.uuid4()), extra_context=context)
    result["file"] = file.filename
    return result


@app.get("/api/history")
async def api_history(conversation_id: Optional[str] = None):
    with closing(db()) as conn:
        if conversation_id:
            rows = conn.execute(
                "SELECT role,content,agents,created_at FROM messages WHERE conversation_id=? ORDER BY created_at",
                (conversation_id,),
            ).fetchall()
            return {"messages": [dict(r) for r in rows]}
        rows = conn.execute(
            "SELECT DISTINCT conversation_id FROM messages ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        return {"conversations": [r["conversation_id"] for r in rows]}


@app.get("/api/system/status")
async def api_status():
    online = await ollama_online()
    return {
        "app": "Angeleck OS (local)",
        "ollama": {"online": online, "models": await ollama_models() if online else []},
        "agents": {"count": len(all_agents())},
        "mode": "IA réelle" if online else "démonstration",
    }


# --------------------------------------------------------------------------- #
#  Interface web intégrée (chat) — servie sur /
# --------------------------------------------------------------------------- #
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(INDEX_HTML)


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Angeleck OS — Command Center</title>
<style>
  :root { --bg:#060A15; --card:#0d1426; --line:#1c2742; --accent:#4FB0FF; --accent2:#7FC8FF; --txt:#EAF1FF; --muted:#7E91B2; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--txt); font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif; height:100vh; display:flex; flex-direction:column; }
  header { padding:14px 20px; border-bottom:1px solid var(--line); display:flex; align-items:center; gap:12px; }
  header .logo { width:34px; height:34px; border-radius:8px; background:radial-gradient(circle at 30% 30%, var(--accent2), var(--accent)); }
  header h1 { font-size:16px; letter-spacing:1px; }
  header .sub { font:11px monospace; color:var(--muted); letter-spacing:2px; }
  #status { margin-left:auto; font-size:12px; color:var(--muted); }
  #status b { color:var(--accent2); }
  main { flex:1; display:flex; overflow:hidden; }
  #side { width:240px; border-right:1px solid var(--line); padding:16px; overflow:auto; }
  #side h3 { font-size:11px; text-transform:uppercase; color:var(--muted); margin-bottom:10px; letter-spacing:1px; }
  .agent { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px; margin-bottom:8px; }
  .agent .n { font-size:13px; font-weight:600; }
  .agent .r { font-size:11px; color:var(--muted); margin-top:2px; }
  .agent.gen { border-color:var(--accent); }
  #chatwrap { flex:1; display:flex; flex-direction:column; }
  #chat { flex:1; overflow:auto; padding:20px; display:flex; flex-direction:column; gap:14px; }
  .msg { max-width:760px; padding:12px 16px; border-radius:12px; line-height:1.5; white-space:pre-wrap; font-size:14px; }
  .msg.user { align-self:flex-end; background:linear-gradient(135deg,var(--accent),#2f7fd0); color:#fff; }
  .msg.bot { align-self:flex-start; background:var(--card); border:1px solid var(--line); }
  .msg .meta { font-size:11px; color:var(--muted); margin-top:8px; }
  #welcome { color:var(--muted); text-align:center; margin:auto; max-width:520px; }
  #welcome h2 { color:var(--txt); margin-bottom:10px; }
  #welcome .ex { display:inline-block; background:var(--card); border:1px solid var(--line); border-radius:20px; padding:6px 12px; margin:4px; cursor:pointer; font-size:12px; }
  #welcome .ex:hover { border-color:var(--accent); }
  footer { padding:14px 20px; border-top:1px solid var(--line); display:flex; gap:10px; }
  #input { flex:1; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 14px; color:var(--txt); font-size:14px; resize:none; }
  #input:focus { outline:none; border-color:var(--accent); }
  #send { background:linear-gradient(135deg,var(--accent),#2f7fd0); border:none; color:#fff; border-radius:10px; padding:0 22px; font-weight:600; cursor:pointer; }
  #send:disabled { opacity:.5; cursor:default; }
</style>
</head>
<body>
<header>
  <div class="logo"></div>
  <div>
    <h1>ANGELECK OS</h1>
    <div class="sub">POWERED BY EMK BLUE DIAMOND</div>
  </div>
  <div id="status">…</div>
</header>
<main>
  <aside id="side">
    <h3>Agents disponibles</h3>
    <div id="agents"></div>
  </aside>
  <section id="chatwrap">
    <div id="chat">
      <div id="welcome">
        <h2>Bienvenue dans Angeleck OS</h2>
        <p>Demande quelque chose, le cerveau choisira (ou créera) le bon agent.</p>
        <div style="margin-top:16px">
          <span class="ex">Crée une publicité Facebook pour mon produit</span>
          <span class="ex">Écris un script vidéo de 30 secondes</span>
          <span class="ex">Analyse mes campagnes TikTok</span>
          <span class="ex">Donne-moi une stratégie d'acquisition client</span>
        </div>
      </div>
    </div>
    <footer>
      <textarea id="input" rows="1" placeholder="Écris ta demande..."></textarea>
      <button id="send">Envoyer</button>
    </footer>
  </section>
</main>
<script>
let conversationId = null;
const chat = document.getElementById('chat');
const input = document.getElementById('input');
const send = document.getElementById('send');

async function loadStatus() {
  try {
    const s = await (await fetch('/api/system/status')).json();
    document.getElementById('status').innerHTML =
      'Mode : <b>' + s.mode + '</b> · Agents : <b>' + s.agents.count + '</b>' +
      (s.ollama.online ? ' · Ollama 🟢' : ' · Ollama 🔴');
  } catch(e) {}
}
async function loadAgents() {
  const d = await (await fetch('/api/agents')).json();
  document.getElementById('agents').innerHTML = d.agents.map(a =>
    '<div class="agent ' + (a.origin==='generated'?'gen':'') + '">' +
      '<div class="n">' + (a.origin==='generated'?'⚡ ':'') + a.name + '</div>' +
      '<div class="r">' + a.role + '</div></div>'
  ).join('');
}
function addMsg(text, cls, meta) {
  const w = document.getElementById('welcome'); if (w) w.remove();
  const d = document.createElement('div');
  d.className = 'msg ' + cls;
  d.textContent = text;
  if (meta) { const m = document.createElement('div'); m.className='meta'; m.textContent=meta; d.appendChild(m); }
  chat.appendChild(d); chat.scrollTop = chat.scrollHeight;
  return d;
}
async function ask(message) {
  addMsg(message, 'user');
  input.value=''; send.disabled=true;
  const loading = addMsg('Le cerveau réfléchit…', 'bot');
  try {
    const res = await fetch('/api/chat', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message, conversation_id: conversationId})
    });
    const data = await res.json();
    conversationId = data.conversation_id;
    loading.textContent = data.answer;
    let meta = 'Agents : ' + (data.agents_used.join(', ') || '—');
    if (data.recruited) meta += ' · ⚡ Nouvel agent créé : ' + data.recruited;
    const m = document.createElement('div'); m.className='meta'; m.textContent=meta; loading.appendChild(m);
    loadAgents();
  } catch(e) {
    loading.textContent = 'Erreur : ' + e.message;
  }
  send.disabled=false; loadStatus();
}
send.onclick = () => { if (input.value.trim()) ask(input.value.trim()); };
input.onkeydown = e => { if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); send.onclick(); } };
document.querySelectorAll('.ex').forEach(el => el.onclick = () => ask(el.textContent));
loadStatus(); loadAgents();
</script>
</body>
</html>"""


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 54)
    print("  ANGELECK OS — version locale")
    print("  Ouvre ton navigateur sur :  http://localhost:8000")
    print("=" * 54 + "\n")
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
