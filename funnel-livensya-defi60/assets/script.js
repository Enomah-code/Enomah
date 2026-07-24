/*
 * Tunnel de vente Livensya — Défi 60 Jours
 * Config centrale : URL de checkout Chariow + webhook optionnel pour les leads.
 */
window.FUNNEL_CONFIG = {
  checkoutUrl: "https://ykhzgspm.mychariow.store/prd_4bisyd7x",
  // Colle ici l'URL d'un webhook (Chariow Pulse, Zapier, Make, Google Sheet, Formspree...)
  // pour recevoir automatiquement chaque lead capturé. Laisser vide = stockage local seulement.
  leadWebhookUrl: "",
  leadStorageKey: "livensya_defi60_lead"
};

function saveLead(lead) {
  try {
    localStorage.setItem(window.FUNNEL_CONFIG.leadStorageKey, JSON.stringify(lead));
  } catch (e) { /* stockage indisponible, on continue sans */ }
}

function getLead() {
  try {
    const raw = localStorage.getItem(window.FUNNEL_CONFIG.leadStorageKey);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function pushLeadToWebhook(lead) {
  const url = window.FUNNEL_CONFIG.leadWebhookUrl;
  if (!url) return;
  fetch(url, {
    method: "POST",
    mode: "no-cors",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lead)
  }).catch(() => { /* best-effort, ne bloque jamais le funnel */ });
}

/* ---------- Page: capture (index.html) ---------- */
function initCaptureForm() {
  const form = document.getElementById("capture-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const prenom = form.prenom.value.trim();
    const email = form.email.value.trim();
    const telephone = form.telephone.value.trim();

    const lead = { prenom, email, telephone, ts: new Date().toISOString(), source: "capture" };
    saveLead(lead);
    pushLeadToWebhook(lead);

    window.location.href = "vente.html";
  });
}

/* ---------- Page: vente (vente.html) ---------- */
function initPersonalization() {
  const lead = getLead();
  const banner = document.getElementById("welcome-banner");
  if (lead && lead.prenom && banner) {
    banner.textContent = "Bravo " + lead.prenom + ", ton programme personnalisé t'attend juste en dessous ↓";
    banner.classList.add("show");
  }
}

function initCountdown() {
  const el = document.getElementById("countdown");
  if (!el) return;
  const h = document.getElementById("cd-h");
  const m = document.getElementById("cd-m");
  const s = document.getElementById("cd-s");

  function tick() {
    const now = new Date();
    const end = new Date(now);
    end.setHours(23, 59, 59, 999);
    let diff = Math.max(0, end - now);

    const hours = Math.floor(diff / 3600000);
    const mins = Math.floor((diff % 3600000) / 60000);
    const secs = Math.floor((diff % 60000) / 1000);

    h.textContent = String(hours).padStart(2, "0");
    m.textContent = String(mins).padStart(2, "0");
    s.textContent = String(secs).padStart(2, "0");
  }
  tick();
  setInterval(tick, 1000);
}

function initFaq() {
  document.querySelectorAll(".faq-item").forEach(function (item) {
    const q = item.querySelector(".faq-q");
    const a = item.querySelector(".faq-a");
    q.addEventListener("click", function () {
      const isOpen = item.classList.contains("open");
      document.querySelectorAll(".faq-item.open").forEach(function (openItem) {
        openItem.classList.remove("open");
        openItem.querySelector(".faq-a").style.maxHeight = null;
      });
      if (!isOpen) {
        item.classList.add("open");
        a.style.maxHeight = a.scrollHeight + "px";
      }
    });
  });
}

function initStickyCta() {
  const sticky = document.getElementById("sticky-cta");
  const heroBtn = document.getElementById("hero-cta");
  if (!sticky || !heroBtn) return;
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      sticky.classList.toggle("show", !entry.isIntersecting);
    });
  }, { threshold: 0 });
  observer.observe(heroBtn);
}

function initReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length || !("IntersectionObserver" in window)) return;
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: "0px 0px -10% 0px" });
  items.forEach(function (item) {
    item.classList.add("reveal-armed");
    observer.observe(item);
    // Filet de sécurité : si l'observer ne se déclenche jamais, on affiche quand même.
    setTimeout(function () { item.classList.add("in"); }, 1200);
  });
}

function initBookTilt() {
  const stages = document.querySelectorAll(".book-stage");
  if (!stages.length) return;

  const canTilt = window.matchMedia("(hover: hover) and (pointer: fine)").matches
    && !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!canTilt) return;

  stages.forEach(function (stage) {
    const book = stage.querySelector(".book-3d");
    if (!book) return;

    stage.addEventListener("pointermove", function (e) {
      const rect = stage.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      const rotY = -18 + x * 26;
      const rotX = 6 - y * 20;
      book.style.animationPlayState = "paused";
      book.style.transform = "rotateY(" + rotY.toFixed(2) + "deg) rotateX(" + rotX.toFixed(2) + "deg)";
    });

    stage.addEventListener("pointerleave", function () {
      book.style.transform = "";
      book.style.animationPlayState = "running";
    });
  });
}

function wireCheckoutLinks() {
  document.querySelectorAll("[data-checkout]").forEach(function (link) {
    link.setAttribute("href", window.FUNNEL_CONFIG.checkoutUrl);
    link.addEventListener("click", function () {
      const lead = getLead() || {};
      lead.clicked_checkout_at = new Date().toISOString();
      saveLead(lead);
    });
  });
}

document.addEventListener("DOMContentLoaded", function () {
  initCaptureForm();
  initPersonalization();
  initCountdown();
  initFaq();
  initStickyCta();
  initReveal();
  initBookTilt();
  wireCheckoutLinks();
});
