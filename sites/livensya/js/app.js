/* Livensya · Défi 60 jours · logique de la page
   ------------------------------------------------------------------
   RÉGLAGES (les seules lignes à modifier) */

/* Paiement : le widget Chariow (dans la carte de l'offre) est la voie principale.
   LIEN_PAIEMENT ne sert que de repli si le widget n'a pas pu se charger (réseau, bloqueur) :
   page de paiement Chariow du produit prd_4bisyd7x (vérifiée : elle répond). */
const LIEN_PAIEMENT = 'https://ykhzgspm.mychariow.store/prd_4bisyd7x/checkout';
const WIDGET_JS = 'https://js.chariowcdn.com/v1/widget.min.js';
const WIDGET_CSS = 'https://js.chariowcdn.com/v1/widget.min.css';
const DELAI_REPLI_MS = 6000;

/* Après un achat réussi dans le widget Chariow : page où l'on envoie l'acheteur
   (au lieu de la page d'achat Chariow). L'identifiant de l'achat est ajouté : merci.html?achat=<purchaseId>.
   Mets une adresse complète si besoin, ex. 'https://livensya.emkbluediamond.online/merci.html'. */
const PAGE_APRES_ACHAT = 'merci.html';

/* Robot achat (Google Apps Script, dossier robot-achat/) : adresse /exec de l'application web.
   Ce n'est pas un secret. Tant que c'est vide (''), rien n'est envoyé.
   À la fin du paiement, la page lui envoie UNE fois { purchaseId, _fbp, _fbc, _userAgent, _eventSourceUrl }
   pour améliorer la correspondance du Purchase que le robot envoie à Meta (le robot seul envoie le Purchase). */
const ROBOT_ACHAT = '';

/* Vidéo faceless (HyperFrames) : laisse vide tant que le fichier n'existe pas.
   Exemple : 'videos/defi-60-jours.mp4' et 'videos/affiche.webp' */
const VIDEO_SRC = '';
const VIDEO_AFFICHE = '';

/* Prénom du narrateur, celui du livre « Défi 60 jours ». Il remplit tous les [data-prenom] de la page
   et parle dans le test. Laisse vide ('') pour un texte neutre (la phrase « Moi, c'est … » disparaît). */
const PRENOM_NARRATEUR = 'David';

/* Pour brancher plus tard une collecte (Google Sheets, CRM, WhatsApp…).
   Pour l'instant : NE FAIT RIEN, aucune donnée ne quitte le téléphone. */
function envoyerLead(donnees) {
  // Exemple futur :
  // fetch('https://ton-service.exemple/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(donnees) });
  return donnees && false;
}

/* ------------------------------------------------------------------ */
(function () {
  'use strict';

  var APERCU = /[?&]apercu=1/.test(location.search);
  var reduit = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var PRODUIT = { content_ids: ['prd_4bisyd7x'], content_type: 'product', content_name: 'Défi 60 jours', value: 3999, currency: 'XOF' };

  /* Typographie française : espace fine insécable avant ? ! : ; et dans les guillemets */
  function typo(t) {
    return String(t)
      .replace(/ ([?!:;»])/g, ' $1')
      .replace(/([«]) /g, '$1 ');
  }
  function echapper(t) {
    return String(t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function lire(cle) { try { return JSON.parse(localStorage.getItem(cle)); } catch (e) { return null; } }
  function ecrire(cle, v) { try { localStorage.setItem(cle, JSON.stringify(v)); } catch (e) {} }
  var suivi = window.lvSuivi || { suivre: function () {}, lead: function () {}, initiateCheckout: function () { return 'x'; }, actif: false };

  var ICONE_COCHE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  function icone(id) { return '<svg class="icone" aria-hidden="true"><use href="#' + id + '"/></svg>'; }

  /* ---------------- Après l'achat (message du widget Chariow) ----------------
     À la fin du paiement, la fenêtre Chariow envoie { type: 'chariow-purchase-completed', purchaseId }.
     On garde purchaseId (lv_purchase_id, pour le futur Purchase côté serveur) et on redirige vers PAGE_APRES_ACHAT.
     Écoute en phase de capture + stopImmediatePropagation : le widget, qui redirige sinon vers sa propre page
     d'achat, ne reçoit pas ce message. AUCUN événement Meta n'est envoyé ici : le Purchase part du robot achat (serveur).
     signalerAchat() lui passe seulement les cookies Meta, une seule fois par achat, sans retarder la redirection. */
  function origineChariow(origine) {
    var u;
    try { u = new URL(origine); } catch (e) { return false; }
    return u.protocol === 'https:' && /(^|\.)(mychariow\.store|chariow\.com)$/.test(u.hostname);
  }
  function cookie(nom) {
    var m = document.cookie.match(new RegExp('(?:^|; )' + nom + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : '';
  }
  function signalerAchat(id) {
    if (!ROBOT_ACHAT || !id) return;
    try { if (localStorage.getItem('lv_signal_achat') === id) return; localStorage.setItem('lv_signal_achat', id); } catch (err) {}
    var fbc = cookie('_fbc');
    var clic = /[?&]fbclid=([^&#]+)/.exec(location.search);
    if (!fbc && clic) fbc = 'fb.1.' + Date.now() + '.' + decodeURIComponent(clic[1]);
    var corps = JSON.stringify({ purchaseId: id, _fbp: cookie('_fbp'), _fbc: fbc, _userAgent: navigator.userAgent, _eventSourceUrl: location.href.slice(0, 1000) });
    var parti = false;
    try { parti = !!(navigator.sendBeacon && navigator.sendBeacon(ROBOT_ACHAT, new Blob([corps], { type: 'text/plain' }))); } catch (err) {}
    if (!parti) {
      try { fetch(ROBOT_ACHAT, { method: 'POST', mode: 'no-cors', keepalive: true, headers: { 'Content-Type': 'text/plain' }, body: corps }); } catch (err) {}
    }
  }
  var achatTraite = false;
  window.addEventListener('message', function (e) {
    var d = e.data;
    if (!d || typeof d !== 'object' || d.type !== 'chariow-purchase-completed') return;
    if (!origineChariow(e.origin)) return;
    var id = (typeof d.purchaseId === 'string' || typeof d.purchaseId === 'number') ? String(d.purchaseId) : '';
    if (!/^[A-Za-z0-9_-]{1,100}$/.test(id)) id = '';
    e.stopImmediatePropagation();
    if (achatTraite) return;
    achatTraite = true;
    if (id) { try { localStorage.setItem('lv_purchase_id', id); } catch (err) {} }
    try { signalerAchat(id); } catch (err) {}
    location.href = PAGE_APRES_ACHAT + (id ? (PAGE_APRES_ACHAT.indexOf('?') > -1 ? '&' : '?') + 'achat=' + encodeURIComponent(id) : '');
  }, true);

  /* ---------------- Widget de paiement Chariow ---------------- */
  var widget = { charge: false, pret: false, attente: [] };
  function boutonWidget() { var w = document.getElementById('chariow-widget'); return w && w.querySelector('button'); }
  function chargerWidget() {
    if (widget.charge) return;
    widget.charge = true;
    var w = document.getElementById('chariow-widget');
    if (!w) return;
    if (reduit) w.setAttribute('data-cta-animation', 'none');
    var css = document.createElement('link'); css.rel = 'stylesheet'; css.href = WIDGET_CSS; document.head.appendChild(css);
    var js = document.createElement('script'); js.src = WIDGET_JS; js.async = true; document.body.appendChild(js);
    var mo = new MutationObserver(function () {
      var b = boutonWidget();
      if (!b || widget.pret) return;
      widget.pret = true; mo.disconnect();
      document.getElementById('paiement').classList.add('pret');
      widget.attente.splice(0).forEach(function (f) { f(); });
    });
    mo.observe(w, { childList: true, subtree: true });
    /* InitiateCheckout : au clic sur le bouton du widget (anti double-clic dans tracking.js) */
    w.addEventListener('click', function (e) {
      /* Seulement le bouton d'achat : pas la croix de fermeture ni les autres boutons de la fenêtre de paiement */
      var b = e.target.closest && e.target.closest('button');
      if (b && !b.closest('.cw-modal-wrapper')) suivi.initiateCheckout(PRODUIT);
    }, true);
  }
  function quandWidgetPret(f, siEchec) {
    if (widget.pret) { f(); return; }
    var fait = false;
    widget.attente.push(function () { if (!fait) { fait = true; f(); } });
    setTimeout(function () { if (!fait) { fait = true; siEchec(); } }, DELAI_REPLI_MS);
  }
  function ouvrirPaiement(declencheur) {
    chargerWidget();
    var carte = document.getElementById('paiement');
    if (carte) carte.scrollIntoView({ behavior: reduit ? 'auto' : 'smooth', block: 'center' });
    if (widget.ouverture) return; /* une ouverture attend déjà le widget : pas de 2e InitiateCheckout */
    widget.ouverture = true;
    if (declencheur) declencheur.setAttribute('aria-busy', 'true');
    quandWidgetPret(function () {
      widget.ouverture = false;
      if (declencheur) declencheur.removeAttribute('aria-busy');
      setTimeout(function () { var b = boutonWidget(); if (b) b.click(); }, reduit ? 0 : 650);
    }, function () {
      /* Repli : page de paiement Chariow */
      widget.ouverture = false;
      suivi.initiateCheckout(PRODUIT);
      setTimeout(function () { location.href = lienAchat(); }, suivi.actif ? 300 : 0); /* laisse partir l'événement */
    });
  }

  /* Liens d'achat : tous mènent au widget (défilement doux puis ouverture du paiement) */
  function lienAchat() {
    var url = LIEN_PAIEMENT;
    var p = new URLSearchParams(location.search), garder = [];
    p.forEach(function (v, k) { if (/^utm_|^fbclid$/.test(k)) garder.push(encodeURIComponent(k) + '=' + encodeURIComponent(v)); });
    if (garder.length) url += (url.indexOf('?') > -1 ? '&' : '?') + garder.join('&');
    return url;
  }
  function brancherAchats(racine) {
    (racine || document).querySelectorAll('[data-achat]').forEach(function (a) {
      if (a.dataset.branche) return;
      a.dataset.branche = '1';
      a.href = '#paiement';
      a.addEventListener('click', function (e) { e.preventDefault(); ouvrirPaiement(a); });
    });
    (racine || document).querySelectorAll('[data-achat-direct]').forEach(function (a) {
      if (a.dataset.branche) return;
      a.dataset.branche = '1';
      a.href = lienAchat();
      a.addEventListener('click', function (e) {
        var id = suivi.initiateCheckout(PRODUIT);
        if (id === null) { e.preventDefault(); return; }
        if (suivi.actif) { e.preventDefault(); setTimeout(function () { location.href = a.href; }, 300); }
      });
    });
  }

  /* ---------------- Le narrateur ---------------- */
  function narrateur() {
    var p = String(PRENOM_NARRATEUR || '').trim();
    return p;
  }
  function appliquerNarrateur() {
    var p = narrateur();
    document.querySelectorAll('[data-prenom]').forEach(function (el) {
      el.textContent = p || el.getAttribute('data-repli') || '';
    });
    document.querySelectorAll('[data-si-prenom]').forEach(function (el) { el.hidden = !p; });
  }

  /* ---------------- Le test ---------------- */
  /* Le prénom de la personne, nettoyé (jamais injecté tel quel dans le HTML) */
  function sonPrenom() {
    var p = String(R.prenom || '').trim().replace(/\s+/g, ' ').slice(0, 30);
    return p ? p.charAt(0).toUpperCase() + p.slice(1) : '';
  }
  function avecPrenom(avant, apres) { var p = sonPrenom(); return p ? avant + echapper(p) + apres : ''; }

  var ETAPES = [
    { id: 'prenom', type: 'prenom',
      titre: function () { return 'Pour commencer, faisons connaissance. Comment tu t\'appelles ?'; },
      aide: function () { var n = narrateur(); return (n ? 'Moi, c\'est ' + echapper(n) + '. ' : '') + 'C\'est facultatif, mais j\'aime savoir à qui je parle.'; } },
    { id: 'depuis', type: 'unique',
      titre: function () { return avecPrenom('Enchanté, ', '. ') + 'Depuis quand tu te trouves mince ?'; },
      options: [['enfance', "Depuis toujours, depuis l'enfance"], ['ado', "Depuis l'adolescence"], ['annees', 'Depuis quelques années'], ['recent', "Depuis peu : j'ai perdu du poids sans savoir pourquoi"]] },
    { id: 'phrases', type: 'multi', titre: "Qu'est-ce qu'on te dit le plus souvent ?", aide: 'Choisis tout ce que tu entends.', citations: true,
      options: [['vent', '« Le vent va t\'emporter. »'], ['mange', '« Mange un peu, toi. »'], ['malade', '« Tu es malade ? »'], ['age', '« On dirait que tu n\'as pas changé depuis le lycée. »'], ['maison', '« On ne te donne pas à manger chez toi ? »'], ['rien', "On ne me dit rien, mais je le pense"], ['autre', 'Autre chose']], autre: true },
    { id: 'blessure', type: 'texte',
      encart: function () { return '<strong>Je comprends.</strong> Moi aussi, j\'ai entendu ces phrases, presque mot pour mot.'; },
      titre: "Quelle est la remarque la plus blessante qu'on t'ait faite, ou le moment le plus gênant que tu as vécu à cause de ton poids ?",
      aide: 'Facultatif. Écris-le seulement si tu en as envie, avec tes mots. Ça reste sur ton téléphone : personne d\'autre ne le lira.',
      placeholder: 'ex. Le jour où…', passer: 'Je préfère passer cette question' },
    { id: 'essais', type: 'multi', titre: "Qu'est-ce que tu as déjà essayé pour prendre du poids ?", aide: 'Choisis tout ce qui te concerne.',
      encart: function () { return R.blessure ? '<strong>Merci de m\'avoir confié ça.</strong> Ce n\'est pas rien de l\'écrire. Moi aussi, j\'ai vécu un moment comme ça.' : ''; },
      options: [['forcer', 'Me forcer à manger plus'], ['sirops', 'Des sirops ou des comprimés pour grossir'], ['poudres', 'Des poudres ou des compléments'], ['sport', 'Le sport ou la musculation'], ['rien', "Rien de précis pour l'instant"]] },
    { id: 'miroir', type: 'unique', titre: 'Devant le miroir ou sur une photo, tu…',
      options: [['evite', "J'évite les photos"], ['cache', 'Je cache mon corps sous des habits larges'], ['compare', 'Je me compare aux autres'], ['ok', 'Ça va, mais je veux me sentir mieux']] },
    { id: 'mesures', type: 'mesures', titre: 'Ton âge, ta taille et ton poids',
      aide: 'Pourquoi je te demande ça : pour calculer ton IMC, un repère indicatif. Rien n\'est envoyé, tout reste sur ton téléphone.' },
    { id: 'image', type: 'unique',
      encart: function () { return '<strong>' + (avecPrenom('Merci, ', '.') || 'Merci.') + '</strong> Un chiffre n\'est pas un jugement, c\'est juste ton point de départ. Moi aussi, je suis parti de là.'; },
      titre: "Imagine-toi avec ton poids idéal. Quelle serait la première chose que tu aimerais sur toi ?",
      options: [['visage', 'Mon visage, plus plein et reposé'], ['epaules', 'Mes épaules et mes bras, plus solides'], ['habits', 'Mes vêtements, enfin à ma taille'], ['silhouette', 'Ma silhouette, plus harmonieuse'], ['regard', 'Mon regard, plus sûr de moi']] },
    { id: 'vivre', type: 'vivre', titre: 'Comment tu te vois dans 60 jours ?', aide: 'Choisis ce qui te parle, puis dis-le avec tes mots si tu veux.',
      options: [['tenue', 'Je porte une tenue ajustée, sans gêne'], ['enfant', 'On ne me prend plus pour un enfant'], ['photo', "J'ai une photo de moi que j'ai envie de partager"], ['plage', 'Je vais à la plage sans me cacher'], ['remarques', 'Les remarques ne me touchent plus']] },
    { id: 'pret', type: 'unique',
      titre: function () { return 'Dernière question' + avecPrenom(', ', '') + '. Le défi demande de suivre le programme chaque jour, pendant 60 jours. Tu es prêt ou prête ?'; },
      options: [['oui', 'Oui, je suis prêt ou prête'], ['essayer', 'Je veux essayer'], ['sais-pas', 'Je ne sais pas encore']] }
  ];
  var PHRASES_VIVRE = {
    tenue: 'Dans 60 jours, je porte une tenue ajustée, sans gêne.',
    enfant: 'Dans 60 jours, on ne me prend plus pour un enfant.',
    photo: "Dans 60 jours, j'ai une photo de moi que j'ai envie de partager.",
    plage: 'Dans 60 jours, je vais à la plage sans me cacher.',
    remarques: 'Dans 60 jours, les remarques ne me touchent plus.'
  };
  var IMAGES = { visage: 'un visage plus plein et reposé', epaules: 'des épaules et des bras plus solides', habits: 'des vêtements enfin à ta taille', silhouette: 'une silhouette plus harmonieuse', regard: 'un regard plus sûr de toi' };
  function val(x) { return typeof x === 'function' ? x() : (x || ''); }

  var carte = document.getElementById('carte-test');
  var R = {}; var etape = -1;

  function rendreIntro() {
    etape = -1;
    carte.innerHTML = typo(
      '<div class="intro-test etape-entree">' +
      '<p class="titre-q" style="font-family:var(--serif);font-size:clamp(1.5rem,5.6vw,2rem);line-height:1.18;color:var(--foret);margin:0 0 12px">Prends deux minutes rien que pour toi.</p>' +
      '<p>Il n\'y a pas de bonne ou de mauvaise réponse. Tu me racontes, et tu verras ensuite ta situation résumée en une page.</p>' +
      '<ul><li>' + icone('i-coche') + '<span>Une dizaine de questions courtes</span></li>' +
      '<li>' + icone('i-coche') + '<span>Ton IMC indicatif, expliqué simplement</span></li>' +
      '<li>' + icone('i-cadenas') + '<span>Tes réponses restent sur ton téléphone</span></li></ul>' +
      '<button class="bouton bouton--plein" type="button" data-commencer>Commencer le test ' + icone('i-fleche') + '</button></div>');
    carte.querySelector('[data-commencer]').addEventListener('click', function () { aller(0, true); });
  }

  function htmlOptions(e, multi) {
    var nom = 'q-' + e.id, v = R[e.id];
    return '<div class="choix' + (multi ? ' choix--multi' : '') + '">' + e.options.map(function (o) {
      var coche = multi ? (v || []).indexOf(o[0]) > -1 : v === o[0];
      return '<label><input type="' + (multi ? 'checkbox' : 'radio') + '" name="' + nom + '" value="' + o[0] + '"' + (coche ? ' checked' : '') + '>' +
        '<span class="case">' + ICONE_COCHE + '</span><span' + (e.citations && o[0] !== 'rien' && o[0] !== 'autre' ? ' class="citation"' : '') + '>' + o[1] + '</span></label>';
    }).join('') + '</div>';
  }

  function aller(n, focus) {
    etape = n;
    var e = ETAPES[n], total = ETAPES.length;
    var titre = val(e.titre), aide = val(e.aide), encart = val(e.encart);
    var h = '<div class="etape-entree">';
    h += '<div class="progression"><span>' + (n + 1) + ' sur ' + total + '</span><span class="progression__barre" aria-hidden="true"><span style="width:' + Math.round((n / total) * 100) + '%"></span></span></div>';
    if (encart) h += '<p class="encart">' + encart + '</p>';
    if (e.type === 'unique' || e.type === 'multi') {
      h += '<fieldset class="question"><legend>' + titre + '</legend>' + (aide ? '<p class="aide">' + aide + '</p>' : '') + htmlOptions(e, e.type === 'multi') + '</fieldset>';
      if (e.autre) h += '<div class="champ champ--large champ-autre" style="margin-top:12px"' + ((R[e.id] || []).indexOf('autre') > -1 ? '' : ' hidden') + '><label for="autre-' + e.id + '">La phrase qu\'on te dit</label><input id="autre-' + e.id + '" maxlength="90" autocomplete="off" placeholder="ex. Tu vas t\'envoler" value="' + echapper(R.phraseAutre || '') + '"></div>';
    } else if (e.type === 'prenom') {
      h += '<div class="question"><p class="titre-q">' + titre + '</p><p class="aide">' + aide + '</p>' +
        '<div class="champ champ--large" style="margin-top:16px"><label for="prenom">Ton prénom</label><input id="prenom" autocomplete="given-name" maxlength="30" placeholder="ex. Ellie" value="' + echapper(R.prenom || '') + '"></div></div>';
    } else if (e.type === 'texte') {
      h += '<div class="question"><p class="titre-q" id="t-' + e.id + '">' + titre + '</p><p class="aide">' + aide + '</p>' +
        '<div class="champ champ--large" style="margin-top:16px"><label class="sr" for="txt-' + e.id + '">Ta réponse</label><textarea id="txt-' + e.id + '" maxlength="280" placeholder="' + e.placeholder + '">' + echapper(R[e.id] || '') + '</textarea></div>' +
        '<button class="passer" type="button" data-passer>' + e.passer + '</button></div>';
    } else if (e.type === 'mesures') {
      var m = R.mesures || {};
      h += '<div class="question"><p class="titre-q">' + titre + '</p><p class="aide">' + aide + '</p>' +
        '<fieldset class="question" style="margin-top:14px"><legend class="libelle" style="font:700 .9375rem var(--sans);color:var(--encre)">Ton âge</legend>' +
        '<div class="choix puces">' + [['moins18', 'Moins de 18 ans'], ['18-24', '18 à 24 ans'], ['25-34', '25 à 34 ans'], ['35plus', '35 ans et plus']].map(function (o) {
          return '<label><input type="radio" name="q-age" value="' + o[0] + '"' + (m.age === o[0] ? ' checked' : '') + '><span class="case"></span><span>' + o[1] + '</span></label>';
        }).join('') + '</div></fieldset>' +
        '<div class="champs"><div class="champ"><label for="taille">Taille (cm)</label><input id="taille" inputmode="numeric" pattern="[0-9]*" autocomplete="off" placeholder="ex. 175" value="' + (m.taille || '') + '"></div>' +
        '<div class="champ"><label for="poids">Poids (kg)</label><input id="poids" inputmode="decimal" autocomplete="off" placeholder="ex. 52" value="' + (m.poids || '') + '"></div></div>' +
        '<button class="passer" type="button" data-passer>Je préfère ne pas donner ma taille et mon poids</button></div>';
    } else if (e.type === 'vivre') {
      h += '<fieldset class="question"><legend>' + titre + '</legend><p class="aide">' + aide + '</p>' + htmlOptions(e, true) + '</fieldset>' +
        '<div class="champ champ--large" style="margin-top:16px"><label for="phrase">Ta phrase, avec tes mots (facultatif)</label>' +
        '<textarea id="phrase" maxlength="140" placeholder="ex. Je porte ma chemise sans qu\'elle flotte.">' + echapper(R.phrase || '') + '</textarea></div>';
    }
    h += '<p class="erreur" role="alert"></p>';
    var auto = e.type === 'unique';
    h += '<div class="test__nav"><button class="retour" type="button" data-retour' + (n === 0 ? ' hidden' : '') + '>' + icone('i-retour') + 'Retour</button>' +
      (auto ? '<span class="aide" style="font-size:.875rem;color:var(--sauge)">Choisis une réponse</span>' : '<button class="bouton" type="button" data-suivant>' + (n === total - 1 ? 'Voir mon résultat' : 'Continuer') + ' ' + icone('i-fleche') + '</button>') + '</div></div>';
    carte.innerHTML = typo(h);

    var err = carte.querySelector('.erreur');
    carte.querySelector('[data-retour]').addEventListener('click', function () { n === 0 ? rendreIntro() : aller(n - 1, true); });
    function suivante() { n === total - 1 ? terminer() : aller(n + 1, true); }
    if (auto) {
      carte.querySelectorAll('input[type=radio]').forEach(function (i) {
        i.addEventListener('change', function () { R[e.id] = i.value; setTimeout(suivante, reduit ? 0 : 450); });
      });
    }
    var suiv = carte.querySelector('[data-suivant]');
    if (suiv) suiv.addEventListener('click', function () { valider(e, err) && suivante(); });
    var caseAutre = carte.querySelector('input[value="autre"]');
    if (caseAutre) caseAutre.addEventListener('change', function () {
      var bloc = carte.querySelector('.champ-autre'); bloc.hidden = !caseAutre.checked;
      if (caseAutre.checked) bloc.querySelector('input').focus();
    });
    var champ = carte.querySelector('#prenom');
    if (champ) champ.addEventListener('keydown', function (ev) { if (ev.key === 'Enter') { ev.preventDefault(); suiv.click(); } });
    var passer = carte.querySelector('[data-passer]');
    if (passer) passer.addEventListener('click', function () {
      if (e.type === 'texte') { R[e.id] = ''; suivante(); return; }
      var age = carte.querySelector('input[name=q-age]:checked');
      if (!age) { err.textContent = typo('Choisis au moins ta tranche d\'âge, puis continue.'); return; }
      R.mesures = { age: age.value, passe: true }; suivante();
    });
    if (focus) {
      var cible = carte.querySelector('legend, .titre-q');
      if (cible) { cible.setAttribute('tabindex', '-1'); cible.focus({ preventScroll: true }); }
      var haut = carte.getBoundingClientRect().top;
      if (haut < 0 || haut > window.innerHeight * 0.4) carte.scrollIntoView({ behavior: reduit ? 'auto' : 'smooth', block: 'start' });
    }
  }

  function valider(e, err) {
    err.textContent = '';
    if (e.type === 'prenom') { R.prenom = (carte.querySelector('#prenom').value || '').trim().slice(0, 30); return true; }
    if (e.type === 'texte') { R[e.id] = (carte.querySelector('#txt-' + e.id).value || '').trim().slice(0, 280); return true; }
    if (e.type === 'multi' || e.type === 'vivre') {
      var v = [].map.call(carte.querySelectorAll('input[type=checkbox]:checked'), function (i) { return i.value; });
      if (e.type === 'vivre') {
        R.phrase = (carte.querySelector('#phrase').value || '').trim().slice(0, 140);
        if (!v.length && !R.phrase) { err.textContent = typo('Choisis au moins une réponse, ou écris ta phrase.'); return false; }
      } else if (!v.length) { err.textContent = typo('Choisis au moins une réponse.'); return false; }
      if (e.autre) {
        R.phraseAutre = v.indexOf('autre') > -1 ? (carte.querySelector('#autre-' + e.id).value || '').trim().replace(/^[«"\s]+|[»"\s.!?]+$/g, '').slice(0, 90) : '';
        if (v.indexOf('autre') > -1 && !R.phraseAutre) { err.textContent = typo('Écris la phrase qu\'on te dit, ou décoche « Autre chose ».'); return false; }
      }
      R[e.id] = v; return true;
    }
    if (e.type === 'mesures') {
      var age = carte.querySelector('input[name=q-age]:checked');
      var t = parseFloat((carte.querySelector('#taille').value || '').replace(',', '.'));
      var p = parseFloat((carte.querySelector('#poids').value || '').replace(',', '.'));
      if (!age) { err.textContent = typo('Choisis ta tranche d\'âge.'); return false; }
      if (!(t >= 120 && t <= 220) || !(p >= 25 && p <= 180)) {
        err.textContent = typo('Vérifie ta taille (en centimètres, ex. 175) et ton poids (en kilos, ex. 52). Ou passe cette question.');
        return false;
      }
      R.mesures = { age: age.value, taille: t, poids: p }; return true;
    }
    return true;
  }

  /* ---------------- Le résultat ---------------- */
  function liste(mots) {
    if (mots.length < 2) return mots.join('');
    return mots.slice(0, -1).join(', ') + ' et ' + mots[mots.length - 1];
  }
  function phraseFinale() {
    if (R.phrase) return R.phrase.replace(/^[«"\s]+|[»"\s]+$/g, '');
    var c = (R.vivre || [])[0];
    return PHRASES_VIVRE[c] || 'Dans 60 jours, on ne me prend plus pour un enfant.';
  }

  function terminer() {
    carte.innerHTML = typo('<div class="chargement etape-entree" role="status"><div>' + (avecPrenom('Je relis tes réponses, ', '…') || 'Je relis tes réponses…') + '<div class="points"><span></span><span></span><span></span></div></div></div>');
    setTimeout(afficherResultat, reduit ? 200 : 1600);
  }

  function afficherResultat() {
    var DEPUIS = { enfance: "Depuis l'enfance, tu es le plus mince de la pièce.", ado: "Depuis l'adolescence, tu es « le mince », « la mince ».", annees: 'Depuis quelques années, tu te trouves trop mince.', recent: 'Tu as perdu du poids récemment, sans savoir pourquoi.' };
    var PHR = { vent: '« Le vent va t\'emporter »', mange: '« Mange un peu »', malade: '« Tu es malade ? »', age: '« On dirait que tu n\'as pas changé depuis le lycée »', maison: '« On ne te donne pas à manger ? »' };
    var MIR = { evite: 'Alors tu évites les photos.', cache: 'Alors tu caches ton corps sous des habits larges.', compare: 'Alors tu te compares aux autres, souvent.', ok: 'Ça va, mais tu sens que tu pourrais être mieux dans ton corps.' };
    var ESS = {
      forcer: 'Tu as déjà essayé de te forcer à manger plus. Si ça n\'a pas suffi, ce n\'est pas un manque de volonté : manger plus, sans structure, ne marche pas pour tout le monde. Pour moi non plus, ça n\'a pas marché.',
      sirops: 'Tu as essayé les sirops ou les comprimés. Beaucoup contiennent un médicament, la cyproheptadine, qui ne devrait se prendre que sur avis médical. Le défi n\'en utilise aucun.',
      poudres: 'Tu as essayé les poudres ou les compléments. Le défi n\'en demande aucun : tout passe par les repas d\'ici.',
      sport: 'Tu as essayé le sport. Sans assez d\'énergie dans l\'assiette, l\'effort a du mal à se voir.',
      rien: 'Tu n\'as encore rien essayé de précis. Tu pars sans mauvaises habitudes à défaire.'
    };
    var phrases = (R.phrases || []).filter(function (k) { return PHR[k]; }).map(function (k) { return '<span class="entendu">' + PHR[k] + '</span>'; });
    if (R.phraseAutre) phrases.push('<span class="entendu">« ' + echapper(R.phraseAutre) + ' »</span>');
    var m = R.mesures || {};

    var miroir = avecPrenom('<p class="resultat__salut">Merci, ', ', d\'avoir répondu franchement. Je t\'ai lu attentivement.</p>');
    miroir += '<p>' + (DEPUIS[R.depuis] || '') + '</p>';
    if (phrases.length) miroir += '<p>Autour de toi, on te dit encore ' + liste(phrases) + '. ' + (MIR[R.miroir] || '') + '</p>';
    else if (MIR[R.miroir]) miroir += '<p>' + MIR[R.miroir] + '</p>';
    if (R.blessure) miroir += '<p class="confidence">Tu m\'as confié un moment gênant. Je sais ce que ça fait : le jour où une personne que j\'appréciais m\'a dit qu\'elle me voyait « comme un frère », parce que je paraissais plus jeune, je ne l\'ai jamais oublié. Ce genre de moment reste longtemps. Tu n\'avais rien fait pour le mériter. Et tu as le droit de vouloir que ça change.</p>';
    (R.essais || []).forEach(function (k) { if (ESS[k]) miroir += '<p>' + ESS[k] + '</p>'; });

    var alerte = '';
    if (R.depuis === 'recent') alerte = '<div class="panneau panneau--alerte"><h3>' + icone('i-sante') + 'D\'abord, ta santé</h3><p>Une perte de poids récente et inexpliquée doit être vérifiée par un médecin, avant tout programme. Le défi pourra venir après, si ton médecin est d\'accord.</p></div>';
    if (m.age === 'moins18') alerte += '<div class="panneau panneau--alerte"><h3>' + icone('i-sante') + 'Tu as moins de 18 ans</h3><p>Le défi s\'adresse aux adultes. Parles-en d\'abord à un parent et à un professionnel de santé : à ton âge, le corps change encore beaucoup.</p></div>';

    var imcHtml = '', imc = 0, horsCible = false;
    if (m.taille && m.poids && m.age !== 'moins18') {
      imc = m.poids / Math.pow(m.taille / 100, 2);
      var txt;
      if (imc < 16) txt = 'Ton IMC est très bas. Avant de commencer, fais un contrôle chez un médecin : c\'est la première étape, pas une option.';
      else if (imc < 18.5) txt = 'Selon le repère de l\'OMS, c\'est la zone dite d\'insuffisance pondérale. C\'est exactement pour cette situation que le défi a été pensé.';
      else if (imc < 25) txt = 'Tu es dans la zone dite normale. Tu peux quand même vouloir te sentir plus solide : le défi t\'aide à construire des repas plus riches, sans viser un chiffre.';
      else { txt = 'Avec cet IMC, le défi n\'est probablement pas ce qu\'il te faut : il est fait pour prendre du poids. Parle de ton objectif à un professionnel de santé.'; horsCible = true; }
      var pos = Math.max(2, Math.min(98, (imc - 14) / 16 * 100));
      imcHtml = '<div class="panneau"><h3>Ton IMC indicatif</h3><p class="imc__valeur">' + imc.toFixed(1).replace('.', ',') + '</p>' +
        '<div class="imc__echelle" aria-hidden="true"><span class="imc__curseur" style="left:' + pos + '%"></span></div>' +
        '<div class="imc__reperes" aria-hidden="true"><span>moins de 18,5</span><span>18,5 à 25</span><span>plus de 25</span></div>' +
        '<p style="margin-top:14px">' + txt + '</p><p style="font-size:.875rem;color:var(--sauge)">L\'IMC est un repère, pas un diagnostic. Il ne dit rien, à lui seul, de ta santé. En cas de doute, demande l\'avis d\'un professionnel.</p></div>';
    }

    var image = IMAGES[R.image];
    var phrase = phraseFinale();
    var cta = horsCible || R.depuis === 'recent' || m.age === 'moins18'
      ? '<div class="heros__actions"><a class="lien-discret" href="#histoire">Lire quand même mon histoire ' + icone('i-bas') + '</a></div>'
      : '<div class="heros__actions"><a class="bouton bouton--plein" href="' + lienAchat() + '" data-achat>Commencer le défi ' + icone('i-fleche') + '</a><a class="lien-discret" href="#histoire">D\'abord, lire mon histoire</a></div>';

    var h = '<div class="resultat__grille">' +
      '<div class="miroir"><p class="etiquette">Ton résultat</p><h2 id="titre-resultat">Ce que tes réponses nous apprennent.</h2>' + miroir +
      '<div class="cout"><h3>Dans 60 jours, il existera deux versions de toi.</h3>' +
      '<div class="deux-chemins"><div class="chemin chemin--a"><b>Celle qui n\'a rien changé</b>Elle entend encore les mêmes remarques, évite encore les photos, et se demande encore comment font les autres. Ce n\'est pas un échec : c\'est juste le même chemin.</div>' +
      '<div class="chemin chemin--b"><b>Celle qui a suivi le programme</b>Elle a mangé à son rythme, avec des assiettes plus riches, et coché une case chaque soir. Elle a 60 jours d\'habitudes derrière elle' + (image ? ', et elle s\'est donné une vraie chance d\'approcher ce que tu as imaginé : ' + image + '.' : '.') + '</div></div>' +
      '<p class="choix-doux">Les deux sont possibles. La seule différence, c\'est ce que tu décides ce soir.</p>' +
      cta + '</div></div>' +
      '<div>' + alerte + imcHtml +
      '<div class="panneau"><h3>Ta phrase</h3><p class="phrase-perso">« ' + echapper(phrase) + ' »</p><p style="margin-top:14px">' + (R.phrase ? 'Ce sont tes mots. ' : '') + 'Garde-la. Si tu fais le défi, écris-la sur la première page de ton carnet.</p></div>' +
      (R.pret === 'sais-pas' ? '<div class="panneau"><h3>Tu hésites</h3><p>C\'est normal. Moi aussi, j\'ai eu des jours sans motivation. Je n\'ai pas été parfait, mais je n\'ai pas abandonné. Le défi ne demande pas d\'être parfait : un jour raté n\'efface pas les autres.</p></div>' : '') +
      '</div></div>';

    var sec = document.getElementById('resultat');
    document.getElementById('resultat-contenu').innerHTML = typo(h);
    brancherAchats(sec);
    sec.hidden = false;
    carte.innerHTML = typo('<div class="intro-test etape-entree"><p class="titre-q" style="font-family:var(--serif);font-size:1.75rem;color:var(--foret);margin:0 0 14px">C\'est noté' + avecPrenom(', ', '') + '. Ton résultat est prêt.</p><a class="bouton" href="#resultat">Voir mon résultat ' + icone('i-bas') + '</a><p style="margin:14px 0 0"><button class="passer" type="button" data-refaire>Refaire le test</button></p></div>');
    carte.classList.add('fini');
    carte.querySelector('[data-refaire]').addEventListener('click', function () { R = {}; sec.hidden = true; carte.classList.remove('fini'); aller(0, true); });
    sec.scrollIntoView({ behavior: reduit ? 'auto' : 'smooth', block: 'start' });
    setTimeout(function () { sec.focus({ preventScroll: true }); }, reduit ? 0 : 700);

    ecrire('lv_test', { phrase: phrase, prenom: sonPrenom(), date: new Date().toISOString().slice(0, 10) });
    appliquerPhrase(phrase, !!R.phrase || !!(R.vivre || []).length);
    /* La confidence (R.blessure) n'est jamais stockée ni envoyée. */
    var donnees = { reponses: Object.assign({}, R, { blessure: R.blessure ? '(non transmis)' : '' }), imc: imc ? Math.round(imc * 10) / 10 : null };
    suivi.lead({ content_name: 'Test 2 minutes' });
    envoyerLead(donnees);
  }

  function appliquerPhrase(phrase, sienne) {
    var cible = document.querySelector('[data-phrase-finale]');
    if (!cible || !phrase) return;
    cible.textContent = typo(phrase);
    var leg = document.querySelector('[data-phrase-legende]');
    if (leg && sienne) leg.textContent = typo('C\'est toi qui l\'as écrit dans le test. Les mots qu\'on t\'a dits, tu ne les as pas choisis. Ceux-là, si. Le jour 1 peut commencer ce soir.');
  }

  /* ---------------- Décor : calendrier et trajet ---------------- */
  function decor() {
    var cal = document.getElementById('calendrier');
    if (cal) { var h = ''; for (var i = 1; i <= 60; i++) h += '<span class="' + (i === 9 ? 'rate' : i <= 23 ? 'fait' : '') + '"></span>'; cal.innerHTML = h; }
    var tr = document.getElementById('trajet');
    if (tr) { var t = ''; for (var j = 1; j <= 60; j++) t += '<span class="' + (j === 1 || j === 30 || j === 60 ? 'marque-j' : '') + '"></span>'; tr.innerHTML = t; }
  }

  /* ---------------- Vidéo faceless ---------------- */
  function video() {
    var sec = document.querySelector('[data-video]');
    if (!sec) return;
    if (!VIDEO_SRC && !APERCU) return; /* reste masquée */
    sec.hidden = false;
    var lecteur = document.getElementById('lecteur'), bouton = sec.querySelector('[data-lire-video]');
    if (VIDEO_AFFICHE) { bouton.style.background = 'center / cover no-repeat url("' + VIDEO_AFFICHE + '")'; }
    bouton.addEventListener('click', function () {
      if (!VIDEO_SRC) {
        if (!lecteur.querySelector('.lecteur__message')) lecteur.insertAdjacentHTML('beforeend', '<p class="lecteur__message" role="status">' + typo('Aperçu : la vidéo n\'est pas encore ajoutée (VIDEO_SRC est vide).') + '</p>');
        return;
      }
      var v = document.createElement('video');
      v.src = VIDEO_SRC; v.controls = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'auto';
      if (VIDEO_AFFICHE) v.poster = VIDEO_AFFICHE;
      lecteur.innerHTML = ''; lecteur.appendChild(v);
      var p = v.play(); if (p && p.catch) p.catch(function () {});
    });
  }

  /* ---------------- Observateurs : apparitions, barre d'achat, ViewContent ---------------- */
  function observateurs() {
    if (!('IntersectionObserver' in window)) {
      document.querySelectorAll('.revele').forEach(function (el) { el.classList.add('vu'); });
      var f = document.querySelector('.final'); if (f) f.classList.add('anime');
      return;
    }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vu'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.revele').forEach(function (el) { io.observe(el); });

    var barre = document.getElementById('barre-achat');
    var zones = {}, cibles = ['.heros', '#test', '#resultat', '#offre', '.final'];
    var ob = new IntersectionObserver(function (es) {
      es.forEach(function (e) { zones[e.target.dataset.zone] = e.isIntersecting; });
      var montrer = !zones['.heros'] && !zones['#test'] && !zones['#offre'] && !zones['.final'];
      barre.classList.toggle('visible', montrer);
      barre.setAttribute('aria-hidden', montrer ? 'false' : 'true');
      var a = barre.querySelector('a'); if (a) a.tabIndex = montrer ? 0 : -1;
    });
    cibles.forEach(function (c) { var el = document.querySelector(c); if (el) { el.dataset.zone = c; ob.observe(el); } });

    var contenu = document.getElementById('contenu');
    if (contenu) new IntersectionObserver(function (es, o) {
      if (es[0].isIntersecting) { chargerWidget(); o.disconnect(); }
    }, { rootMargin: '400px 0px' }).observe(contenu);

    var fin = document.querySelector('.final');
    if (fin) new IntersectionObserver(function (es, o) {
      if (es[0].isIntersecting) { fin.classList.add('anime'); o.disconnect(); }
    }, { threshold: 0.45 }).observe(fin);

    var offre = document.getElementById('offre'), vu = false;
    if (offre) new IntersectionObserver(function (es, o) {
      if (!vu && es[0].isIntersecting) { vu = true; suivi.suivre('ViewContent', PRODUIT); o.disconnect(); }
    }, { threshold: 0.35 }).observe(offre);
  }

  /* ---------------- Démarrage ---------------- */
  document.addEventListener('DOMContentLoaded', function () {
    if (reduit) document.documentElement.classList.add('reduit');
    appliquerNarrateur();
    brancherAchats();
    decor();
    video();
    observateurs();
    if (carte) rendreIntro();
    document.querySelectorAll('[data-ouvrir-test]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        document.getElementById('test').scrollIntoView({ behavior: reduit ? 'auto' : 'smooth', block: 'start' });
        if (etape === -1 && document.getElementById('resultat').hidden) setTimeout(function () { aller(0, true); }, reduit ? 0 : 500);
      });
    });
    var memo = lire('lv_test');
    if (memo && memo.phrase) appliquerPhrase(memo.phrase, true);
  });
})();
