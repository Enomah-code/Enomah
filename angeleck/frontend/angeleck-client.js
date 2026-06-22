/**
 * Connecteur frontend Angeleck OS.
 *
 * Client JavaScript léger (sans dépendance) à brancher sur votre interface
 * existante. Gère l'authentification (JWT) et les appels à l'API backend.
 *
 * Exemple :
 *   const api = new AngeleckClient("http://localhost:8000/api/v1");
 *   await api.register("user@mail.com", "motdepasse123");
 *   const res = await api.chat("Crée une stratégie TikTok pour mon produit");
 *   console.log(res.response, res.missions);
 */
class AngeleckClient {
  constructor(baseUrl = "http://localhost:8000/api/v1") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.token = localStorage.getItem("angeleck_token") || null;
  }

  _headers(json = true) {
    const h = {};
    if (json) h["Content-Type"] = "application/json";
    if (this.token) h["Authorization"] = `Bearer ${this.token}`;
    return h;
  }

  _setToken(token) {
    this.token = token;
    localStorage.setItem("angeleck_token", token);
  }

  async register(email, password, fullName = "") {
    const resp = await fetch(`${this.baseUrl}/auth/register`, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    if (!resp.ok) throw new Error((await resp.json()).detail);
    const data = await resp.json();
    this._setToken(data.access_token);
    return data.user;
  }

  async login(email, password) {
    // OAuth2 password flow attend un form-urlencoded (username = email).
    const body = new URLSearchParams({ username: email, password });
    const resp = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!resp.ok) throw new Error((await resp.json()).detail);
    const data = await resp.json();
    this._setToken(data.access_token);
    return data.user;
  }

  logout() {
    this.token = null;
    localStorage.removeItem("angeleck_token");
  }

  /** Envoie une demande au cerveau central. */
  async chat(message, conversationId = null) {
    const resp = await fetch(`${this.baseUrl}/chat`, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    if (!resp.ok) throw new Error((await resp.json()).detail);
    return resp.json();
  }

  /** Liste les agents disponibles. */
  async getAgents() {
    const resp = await fetch(`${this.baseUrl}/agents`, { headers: this._headers() });
    return resp.json();
  }

  /** Récupère la mémoire utilisateur (préférences + missions). */
  async getMemory() {
    const resp = await fetch(`${this.baseUrl}/memory`, { headers: this._headers() });
    return resp.json();
  }

  /** Déclenche la création d'un nouvel agent spécialisé. */
  async createAgent(domain, skills = [], description = "") {
    const resp = await fetch(`${this.baseUrl}/create-agent`, {
      method: "POST",
      headers: this._headers(),
      body: JSON.stringify({ domain, skills, description }),
    });
    if (!resp.ok) throw new Error((await resp.json()).detail);
    return resp.json();
  }

  /** Upload d'un fichier pour analyse. */
  async upload(file) {
    const form = new FormData();
    form.append("file", file);
    const resp = await fetch(`${this.baseUrl}/upload`, {
      method: "POST",
      headers: this._headers(false),
      body: form,
    });
    if (!resp.ok) throw new Error((await resp.json()).detail);
    return resp.json();
  }
}

// Export ESM + global navigateur
if (typeof module !== "undefined" && module.exports) {
  module.exports = { AngeleckClient };
}
if (typeof window !== "undefined") {
  window.AngeleckClient = AngeleckClient;
}
