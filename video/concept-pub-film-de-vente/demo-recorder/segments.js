// Live-demo choreography. Times are seconds from the start of each recorded clip.
// Each clip is placed in the film at: V1 = 28.8 s, V2 = 53.5 s, V3 = 71.05 s (global),
// so every action lands on the matching word of the voice-over (see vo/timing.json).
const BODY = (off) => ({ sel: "body", off });
module.exports = [
  {
    name: "v1-vitrine", dur: 20.95, cursor: [1250, 990], startScroll: BODY(0),
    setup: () => { window.scrollTo(0, 0); document.querySelectorAll("#top [data-reveal], #top [data-mask], #top [data-grow]").forEach((e) => e.classList.remove("in")); },
    actions: [
      { t: 0.6, type: "eval", js: () => document.querySelectorAll("#top [data-reveal], #top [data-mask], #top [data-grow]").forEach((e) => e.classList.add("in")) },
      { t: 2.2, type: "move", dur: 1.1, to: { sel: "#top .cp-btn", text: "Obtenir mon devis" } },
      { t: 4.2, type: "move", dur: 0.9, to: { sel: "#top .cp-btn", text: "Voir les réalisations" } },
      { t: 6.2, type: "move", dur: 1.2, to: { x: 1180, y: 640 } },
      // « Regardez : chaque section se révèle au défilement… »
      { t: 8.9, type: "scroll", dur: 1.9, to: { sel: ".sec", off: -30 } },
      { t: 11.4, type: "scroll", dur: 1.7, to: { sel: "#prestations", off: -64 } },
      { t: 13.2, type: "move", dur: 0.8, to: { sel: "#prestations .svc", i: 0 } },
      { t: 14.2, type: "move", dur: 0.7, to: { sel: "#prestations .svc", i: 2 } },
      // « Vos neuf métiers… vos réalisations défilent comme au cinéma. »
      { t: 15.3, type: "scroll", dur: 1.4, to: { sel: "#prestations", off: 420 } },
      { t: 15.6, type: "move", dur: 1.0, to: { x: 1250, y: 760 } },
      { t: 17.0, type: "scroll", dur: 1.3, to: { sel: "#realisations", off: 0 } },
      { t: 18.3, type: "scroll", dur: 2.6, ease: "inOutCubic", to: { sel: "#realisations", off: 2160 } },
    ],
  },
  {
    name: "v2-devis-rdv", dur: 18.35, cursor: [760, 990], startScroll: BODY(7470),
    actions: [
      // « Votre client choisit sa prestation… »
      { t: 0.7, type: "move", dur: 0.9, to: { sel: "#chips .chip", text: "Motion design" } },
      { t: 1.7, type: "click" },
      // « …règle la durée… »
      { t: 2.3, type: "move", dur: 0.8, to: { sel: "#qtyRange", fx: 0.299 } },
      { t: 3.15, type: "drag", dur: 1.0, sel: "#qtyRange", min: 5, max: 90, from: 30, to: 60 },
      // « …ajoute ses options… »
      { t: 4.0, type: "scroll", dur: 0.9, y: 7700 },
      { t: 4.3, type: "move", dur: 0.7, to: { sel: "#opts .opt", text: "Voix off" } },
      { t: 5.05, type: "click" },
      { t: 5.3, type: "move", dur: 0.6, to: { sel: "#opts .opt", text: "Étalonnage" } },
      { t: 5.95, type: "click" },
      // « …et le prix se met à jour en direct, sous ses yeux. »
      { t: 6.3, type: "move", dur: 0.7, to: { sel: "#delays .delay", text: "Express" } },
      { t: 7.05, type: "click" },
      { t: 7.5, type: "move", dur: 0.8, to: { sel: "#price", fx: 0.8, fy: 0.7 } },
      // « Il valide, et sa commande est enregistrée. »
      { t: 8.0, type: "move", dur: 0.7, to: { sel: "#devisSubmit" } },
      { t: 8.75, type: "click" },
      { t: 10.2, type: "move", dur: 1.0, to: { x: 1250, y: 620 } },
      // « Il réserve lui-même son rendez-vous : le jour, l'heure, en visio ou au studio. »
      { t: 12.3, type: "scroll", dur: 1.2, to: { sel: "#rendez-vous", off: 40 } },
      { t: 13.6, type: "move", dur: 0.8, to: { sel: "#days .day", i: 3 } },
      { t: 14.5, type: "click" },
      { t: 14.8, type: "move", dur: 0.7, to: { sel: "#slots .slot:not([disabled])", i: 4 } },
      { t: 15.6, type: "click" },
      { t: 16.2, type: "move", dur: 0.6, to: { sel: ".mode", i: 1 } },
      { t: 16.85, type: "click" },
      { t: 17.25, type: "move", dur: 0.75, to: { sel: "#rdvBook" } },
      { t: 18.05, type: "click" },
    ],
  },
  {
    name: "v3-espace-client", dur: 25.2, cursor: [1100, 990], startScroll: BODY(10150),
    actions: [
      // « …l'espace client. »
      { t: 0.8, type: "scroll", dur: 2.6, ease: "inOutCubic", y: 10190 },
      { t: 2.5, type: "move", dur: 0.8, to: { sel: "#authPanel input[type=email]" } },
      { t: 3.3, type: "click" },
      // « Votre client se connecte… »
      { t: 3.45, type: "type", dur: 0.9, text: "contact@maisonkola.com" },
      { t: 4.45, type: "move", dur: 0.45, to: { sel: "#authPanel input[type=password]" } },
      { t: 4.95, type: "click" },
      { t: 5.05, type: "type", dur: 0.5, text: "concept2026" },
      { t: 5.65, type: "move", dur: 0.5, to: { sel: "#authCta" } },
      { t: 6.2, type: "click" },
      // « …et retrouve toutes ses commandes au même endroit. »
      { t: 6.6, type: "scroll", dur: 1.2, y: 10380 },
      // « Les projets en cours, avec leur avancement, étape par étape. »
      { t: 8.2, type: "move", dur: 0.8, to: { sel: "#orders .order", i: 0, fx: 0.3, fy: 0.3 } },
      { t: 9.8, type: "move", dur: 0.8, to: { sel: "#orders .order", i: 0, fx: 0.35, fy: 0.78 } },
      { t: 10.6, type: "scroll", dur: 1.4, y: 10600 },
      // « Les commandes livrées, avec les fichiers prêts à télécharger. »
      { t: 12.0, type: "scroll", dur: 0.9, y: 10380 },
      { t: 12.3, type: "move", dur: 0.6, to: { sel: "#dashTabs .tab", text: "Livrées" } },
      { t: 12.95, type: "click" },
      { t: 13.7, type: "move", dur: 0.8, to: { sel: "#orders .cp-btn", text: "Télécharger", visible: true } },
      { t: 14.9, type: "scroll", dur: 1.0, y: 10470 },
      // « Et les devis à valider, en un seul clic. »
      { t: 15.8, type: "scroll", dur: 0.6, y: 10380 },
      { t: 15.9, type: "move", dur: 0.6, to: { sel: "#dashTabs .tab", text: "Devis" } },
      { t: 16.55, type: "click" },
      { t: 17.0, type: "move", dur: 0.7, to: { sel: "#orders .cp-btn", text: "Valider", visible: true } },
      { t: 17.85, type: "click" },
      // « Plus de relances, plus de fichiers perdus… »
      { t: 19.2, type: "move", dur: 0.7, to: { sel: "#dashTabs .tab", text: "En cours" } },
      { t: 20.0, type: "click" },
      { t: 20.4, type: "move", dur: 1.0, to: { x: 1250, y: 700 } },
      { t: 20.6, type: "scroll", dur: 4.0, ease: "inOutCubic", y: 10290 },
    ],
  },
];
