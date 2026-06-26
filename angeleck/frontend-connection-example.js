/**
 * ============================================================
 *  Angeleck OS — Exemple de connexion frontend (Module 7)
 * ============================================================
 *
 *  Ce fichier N'EST PAS le frontend. C'est un client JavaScript
 *  minimal montrant comment l'interface EMK Blue Diamond Studio
 *  doit dialoguer avec l'API Angeleck. Copiez ces fonctions dans
 *  votre code frontend existant — aucune modification du design
 *  n'est nécessaire.
 *
 *  Base URL de l'API (adaptez en production) :
 */
const ANGELECK_API = "http://localhost:8000";

/** Stocke le token JWT après connexion. */
let ANGELECK_TOKEN = localStorage.getItem("angeleck_token") || null;

/** En-têtes authentifiés. */
function authHeaders(extra = {}) {
  return ANGELECK_TOKEN
    ? { Authorization: `Bearer ${ANGELECK_TOKEN}`, ...extra }
    : { ...extra };
}

/** 1) Inscription d'un utilisateur. */
async function register(email, password, fullName = "") {
  const res = await fetch(`${ANGELECK_API}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  const data = await res.json();
  if (res.ok) {
    ANGELECK_TOKEN = data.access_token;
    localStorage.setItem("angeleck_token", ANGELECK_TOKEN);
  }
  return data;
}

/** 2) Connexion (OAuth2 password flow — username = email). */
async function login(email, password) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  const res = await fetch(`${ANGELECK_API}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });
  const data = await res.json();
  if (res.ok) {
    ANGELECK_TOKEN = data.access_token;
    localStorage.setItem("angeleck_token", ANGELECK_TOKEN);
  }
  return data;
}

/** 3) Envoyer une demande au cerveau central. */
async function chat(message, conversationId = null) {
  const res = await fetch(`${ANGELECK_API}/api/chat`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  return res.json(); // { answer, conversation_id, agents_used, recruited, reasoning }
}

/** 4) Lister les agents disponibles. */
async function listAgents() {
  const res = await fetch(`${ANGELECK_API}/api/agents`, { headers: authHeaders() });
  return res.json();
}

/** 5) Créer dynamiquement un agent. */
async function createAgent(skill, context = "") {
  const res = await fetch(`${ANGELECK_API}/api/create-agent`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ skill, context }),
  });
  return res.json();
}

/** 6) Uploader et analyser un fichier. */
async function uploadFile(file, message = "Analyse ce fichier.") {
  const form = new FormData();
  form.append("file", file);
  form.append("message", message);
  const res = await fetch(`${ANGELECK_API}/api/upload`, {
    method: "POST",
    headers: authHeaders(), // ne PAS fixer Content-Type : le navigateur le gère
    body: form,
  });
  return res.json();
}

/** 7) Récupérer l'historique. */
async function getHistory(conversationId = null) {
  const url = conversationId
    ? `${ANGELECK_API}/api/history?conversation_id=${conversationId}`
    : `${ANGELECK_API}/api/history`;
  const res = await fetch(url, { headers: authHeaders() });
  return res.json();
}

// Exemple d'usage :
// await login("admin@angeleck.os", "changeme123");
// const reply = await chat("Crée une publicité Facebook pour mon produit");
// console.log(reply.answer, reply.agents_used);
