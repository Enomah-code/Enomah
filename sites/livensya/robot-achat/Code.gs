/* Livensya · robot achat (Google Apps Script)
   ------------------------------------------------------------------
   Envoie l'événement Purchase à Meta (API Conversions), UNE SEULE FOIS par vente Chariow.

   1. Chariow (Pulse « Vente réussie ») appelle doPost avec la vente.
   2. Le robot relit la fiche de la vente chez Chariow (CHARIOW_API_KEY) : c'est sa preuve
      que la vente existe, est payée et concerne bien le produit Livensya. Sans cette preuve, rien ne part.
      (Chariow signe ses Pulses dans un en-tête HTTP, mais Apps Script ne donne pas accès aux en-têtes :
      la relecture de la fiche remplace la vérification de signature.)
   3. La page du site envoie un petit signal facultatif (purchaseId + cookies Meta _fbp/_fbc).
      Le robot l'attend au plus ATTENTE_SIGNAL_MIN minutes, puis envoie sans fbp/fbc.
   4. event_id = identifiant de la vente Chariow. Chaque vente est notée dans les propriétés
      du script ET dans l'onglet Ventes : un renvoi du webhook ou un signal répété ne renvoie jamais rien.

   Propriétés du script (Paramètres du projet > Propriétés du script), jamais dans ce fichier :
   - META_ACCESS_TOKEN    : jeton de l'API Conversions (obligatoire)
   - CHARIOW_API_KEY      : clé API de la boutique Livensya (obligatoire)
   - META_TEST_EVENT_CODE : code de l'onglet « Tester les événements » (facultatif). Il sert UNIQUEMENT
                            à testerAchatFictif() : les vraies ventes ne partent jamais avec ce code.
*/

/* ---------------- Réglages (rien de secret ici) ---------------- */
const ENVOYER_VENTES_AFFILIES = false;   // comme IABB : une vente apportée par un affilié n'est pas envoyée à Meta
var PIXEL_ID = '5010730402487338';
var VERSION_API_META = 'v25.0';
var PRODUIT_ID = 'prd_4bisyd7x';
var NOM_PRODUIT = 'Défi 60 jours';
var BOUTIQUE_ID = 'store_6is731jk2ybk';
var BOUTIQUE_URL = 'ykhzgspm.mychariow.store';
var SITE = 'https://livensya.emkbluediamond.online/';
var PRIX = 3999;
var DEVISE = 'XOF';
var ATTENTE_SIGNAL_MIN = 10;   // attente maximale du signal de la page avant d'envoyer sans fbp/fbc
var ESSAIS_MAX = 12;           // essais de lecture de la fiche Chariow (un toutes les 5 min, soit 1 h)
var ESSAIS_META_MAX = 12;      // essais d'envoi à Meta si Meta ne répond pas, répond 5xx/429 ou events_received 0
var GARDER_JOURS = 10;         // mémoire des ventes terminées (au-delà de 7 jours, Meta refuse l'achat de toute façon)
var STATUTS_PAYES = ['completed', 'settled', 'success', 'paid'];
var STATUTS_REFUSES = ['failed', 'cancelled', 'canceled', 'abandoned', 'refunded', 'expired'];
var JOUR = 24 * 3600 * 1000;

/* ---------------- Points d'entrée web ---------------- */
function doGet() { return json_({ status: 'ok' }); }

function doPost(e) {
  var corps;
  try { corps = JSON.parse((e && e.postData && e.postData.contents) || ''); }
  catch (err) { journal_('Ignoré', 'message illisible'); return json_({ status: 'ok' }); }
  try {
    if (corps && corps.event === 'successful.sale') recevoirVente_(corps);
    else if (corps && corps.purchaseId) recevoirSignal_(corps);
    else journal_('Ignoré', 'message non attendu : ' + String((corps && corps.event) || '?').slice(0, 40));
  } catch (err) {
    journal_('ERREUR', err.message);
  }
  return json_({ status: 'ok' });
}

/* ---------------- Webhook de vente Chariow ---------------- */
function recevoirVente_(p) {
  var id = idValide_(p.sale && p.sale.id);
  if (!id) { journal_('Ignoré', 'vente sans identifiant'); return; }
  if (!(p.product && p.product.id === PRODUIT_ID)) { journal_('Ignoré', id + ' : autre produit'); return; }
  // La boutique est vérifiée de façon sûre sur la fiche Chariow ; ici, un simple signalement.
  if (!boutiqueLivensya_(p.store)) journal_('Attention', id + ' : boutique du webhook non reconnue, vérification par la fiche');
  var c = p.customer || {}, tel = telephoneBrut_(c.phone);
  var indices = { email: String(c.email || ''), telephone: tel.texte, indicatif: tel.indicatif,
                  pays: String((c.country && c.country.code) || c.country || ''),
                  affilie: !!(p.affiliate && typeof p.affiliate === 'object') };
  var res = '';
  var fait = avecVerrou_(function () { res = accepterVente_(id, indices); });
  if (!fait || res === 'plein') garderPourPlusTard_(id, indices, fait ? 'trop de ventes à vérifier' : 'robot occupé');
}

function garderPourPlusTard_(id, indices, motif) {
  if (compterPrefixe_('brut_') >= 300) { journal_('Ignoré', id + ' : file d\'attente pleine (' + motif + ')'); return; }
  proprietes_().setProperty('brut_' + id, JSON.stringify(indices));   // repris par envoyerEnAttente()
  journal_('Mise en file', id + ' : ' + motif + ', sera traitée au prochain passage');
}

/* Renvoie 'doublon', 'plein' ou 'ok'. */
function accepterVente_(id, indices, vus) {
  var etat = lireEtat_(id);
  if (etat && etat.etape !== 'echec') { journal_('Doublon ignoré', id + ' (' + etat.etape + ')'); return 'doublon'; }
  if (compterEtapes_('verif') >= 50) return 'plein';
  etat = { id: id, etape: 'verif', recuLe: Date.now(), essais: 0, indices: indices };
  ecrireEtat_(etat);
  if (vus) vus[id] = true;
  avancer_(etat);
  return 'ok';
}

/* ---------------- Signal de la page (app.js) ---------------- */
function recevoirSignal_(b) {
  var id = idValide_(b.purchaseId);
  if (!id) { journal_('Ignoré', 'signal sans identifiant valable'); return; }
  var signal = {
    fbp: /^fb\.\d\.\d{10,16}\.[^\s"'<>\\]{1,120}$/.test(String(b._fbp || '')) ? String(b._fbp) : '',
    fbc: /^fb\.\d\.\d{10,16}\.[^\s"'<>\\]{1,800}$/.test(String(b._fbc || '')) ? String(b._fbc) : '',
    ua: String(b._userAgent || '').slice(0, 512),
    url: String(b._eventSourceUrl || '').indexOf(SITE) === 0 ? String(b._eventSourceUrl).slice(0, 1000) : '',
    t: Date.now()
  };
  var fait = avecVerrou_(function () {
    var props = proprietes_();
    var etat = lireEtat_(id);
    if (etat && etat.etape !== 'verif' && etat.etape !== 'attente') { journal_('Signal ignoré', id + ' : vente déjà traitée'); return; }
    if (props.getProperty('signal_' + id)) { journal_('Signal ignoré', id + ' : signal déjà reçu'); return; }
    if (compterPrefixe_('signal_') >= 200) { journal_('Signal ignoré', 'trop de signaux en attente'); return; }
    props.setProperty('signal_' + id, JSON.stringify(signal));
    journal_('Signal reçu', id + (signal.fbp ? ' fbp' : '') + (signal.fbc ? ' fbc' : ''));
    if (etat && etat.etape === 'attente') avancer_(etat);
  });
  if (!fait) journal_('Signal perdu', id + ' : robot occupé, l\'achat partira sans fbp/fbc');
}

/* ---------------- Avancement d'une vente : vérifier, attendre, envoyer ---------------- */
function avancer_(etat) {
  var id = etat.id;
  if (etat.etape === 'verif') {
    var r = verifierVente_(id, etat.indices || {});
    if (r.refus) {
      proprietes_().deleteProperty('vente_' + id);
      journal_('Refusé', id + ' : ' + r.refus + '. Rien envoyé à Meta.');
      return;
    }
    if (r.reessayer) {
      if (!r.sansCompter) etat.essais++;
      if (etat.essais >= ESSAIS_MAX || Date.now() - etat.recuLe > 7 * JOUR) {
        marquerFin_(id, 'echec');
        ligneVente_({ id: id, email: (etat.indices || {}).email }, 'Échec : ' + r.reessayer + '. Rejoue la livraison depuis Chariow (Pulses > Livraisons).');
        journal_('Abandonné', id + ' : ' + r.reessayer);
      } else {
        if (etat.raison !== r.reessayer) journal_('Nouvel essai bientôt', id + ' : ' + r.reessayer);   // une ligne par nouveau motif
        etat.raison = r.reessayer;
        ecrireEtat_(etat);
      }
      return;
    }
    if (r.affilie) {
      if (r.affilie === 'fiche') marquerFin_(id, 'affilie');
      else proprietes_().deleteProperty('vente_' + id);   // d'après le seul webhook : aucun état, un faux ne bloque jamais le vrai
      ligneVente_(r.vente, 'Vente affilié, non envoyée' + (r.affilie === 'webhook' ? ' (d\'après le webhook)' : ''));
      return;
    }
    etat = { id: id, etape: 'attente', recuLe: etat.recuLe, essais: 0, vente: r.vente };
    ecrireEtat_(etat);
    ligneVente_(etat.vente, 'En attente du signal de la page');
  }
  if (etat.etape !== 'attente') return;

  if (statutVente_(id).indexOf('Envoyé') === 0) {   // déjà envoyé mais l'état n'avait pas pu être noté
    marquerFin_(id, 'envoye');
    return;
  }
  var brut = proprietes_().getProperty('signal_' + id);
  var signal = brut ? JSON.parse(brut) : null;
  if (!signal && Date.now() - etat.recuLe < ATTENTE_SIGNAL_MIN * 60000) return;   // on attend encore

  var res = envoyerPurchase_(etat.vente, signal);
  if (res.attendre) { majStatut_(id, res.message); return; }
  if (res.ok) {
    try { majStatut_(id, res.message, signal); } catch (err) { journal_('ERREUR', id + ' : onglet Ventes non mis à jour (' + err.message + ')'); }
    marquerFin_(id, 'envoye');
    try { proprietes_().deleteProperty('signal_' + id); } catch (err) {}
    return;
  }
  etat.essais++;
  if (res.reessayer && etat.essais < ESSAIS_META_MAX) {
    ecrireEtat_(etat);
    majStatut_(id, 'Erreur Meta, nouvel essai dans 5 min : ' + res.message);
  } else {
    marquerFin_(id, 'echec');
    majStatut_(id, 'Échec Meta : ' + res.message);
  }
}

/* Note l'état final d'une vente. Si l'écriture échoue, essaie une écriture minimale, puis journalise.
   (Après un envoi réussi, l'onglet Ventes « Envoyé… » empêche de toute façon un renvoi.) */
function marquerFin_(id, etape) {
  var court = JSON.stringify({ id: id, etape: etape, t: Date.now() });
  try { proprietes_().setProperty('vente_' + id, court); return true; } catch (err1) {
    try { proprietes_().setProperty('vente_' + id, '{"etape":"' + etape + '","t":' + Date.now() + '}'); journal_('ERREUR', id + ' : état « ' + etape + ' » noté en version minimale'); return true; }
    catch (err2) { journal_('ERREUR', id + ' : impossible de noter l\'état « ' + etape + ' » (' + err2.message + ')'); return false; }
  }
}

/* Lit la fiche de la vente chez Chariow. Renvoie { vente, affilie } ou { refus } ou { reessayer }. */
function verifierVente_(id, indices) {
  var cle = proprietes_().getProperty('CHARIOW_API_KEY') || '';
  if (!cle) return { reessayer: 'clé CHARIOW_API_KEY absente', sansCompter: true };
  var rep;
  try {
    rep = UrlFetchApp.fetch('https://api.chariow.com/v1/sales/' + encodeURIComponent(id), {
      method: 'get', headers: { Authorization: 'Bearer ' + cle, Accept: 'application/json' }, muteHttpExceptions: true
    });
  } catch (err) { return { reessayer: 'Chariow injoignable' }; }
  var code = rep.getResponseCode();
  if (code === 404) return { refus: 'vente inconnue chez Chariow (faux appel ?)' };
  if (code === 401 || code === 403) return { reessayer: 'clé Chariow refusée (code ' + code + ')', sansCompter: true };
  if (code !== 200) return { reessayer: 'Chariow répond ' + code };
  var f;
  try { f = JSON.parse(rep.getContentText()); f = (f && f.data) || f; } catch (err) { return { reessayer: 'fiche Chariow illisible' }; }
  if (!f || String(f.id) !== id) return { refus: 'fiche Chariow d\'une autre vente' };
  if (!f.product || !f.product.id) return { reessayer: 'produit absent de la fiche Chariow' };
  if (f.product.id !== PRODUIT_ID) return { refus: 'la fiche Chariow concerne un autre produit' };
  if (!boutiqueLivensya_(f.store)) return { refus: 'la fiche Chariow concerne une autre boutique' };

  var statut = String(f.status || '').toLowerCase(), paiement = String((f.payment && f.payment.status) || '').toLowerCase();
  if (STATUTS_REFUSES.indexOf(statut) > -1 || /^(failed|cancelled|canceled)$/.test(paiement)) {
    return { refus: 'vente au statut « ' + statut + ' » (paiement « ' + paiement + ' »)' };
  }
  if (STATUTS_PAYES.indexOf(statut) === -1 && paiement !== 'success') {
    return { reessayer: 'statut « ' + statut + ' » pas encore payé ou inconnu' };
  }
  var temps = Date.parse(f.completed_at || '') || Date.parse(f.created_at || '') || Date.now();
  if (Date.now() - temps > 7 * JOUR) return { refus: 'vente de plus de 7 jours, Meta la refuserait' };

  var client = f.customer || {}, ctx = f.context || {};
  var email = String(client.email || '').trim();
  var memeClient = !!email && email.toLowerCase() === String(indices.email || '').trim().toLowerCase();
  var tel = telephoneBrut_(client.phone);
  if (!tel.texte && memeClient) tel = { texte: indices.telephone || '', indicatif: indices.indicatif || '' };   // secours : webhook du même client
  var paysTel = (client.phone && client.phone.country) || {};
  var montant = f.amount || {};
  var devise = /^[A-Z]{3}$/.test(String(montant.currency || '')) ? String(montant.currency)
    : (montant.currency && /^[A-Z]{3}$/.test(String(montant.currency.code || '')) ? String(montant.currency.code) : '');
  if (!devise) { devise = DEVISE; journal_('Attention', id + ' : devise illisible dans la fiche, ' + DEVISE + ' utilisé'); }

  var vente = {
    id: id,
    temps: temps,
    email: email,
    telephone: tel.texte,
    indicatif: tel.indicatif || String((ctx.country && ctx.country.dial_code) || ''),
    prenom: String(client.first_name || ''),
    nom: String(client.last_name || ''),
    pays: String(paysTel.code || (ctx.country && ctx.country.code) || (memeClient ? indices.pays : '') || ''),
    ip: ipValide_(ctx.ip_address),
    ua: String(ctx.user_agent || '').slice(0, 512),
    valeur: (typeof montant.value === 'number' && montant.value >= 0) ? montant.value : PRIX,
    devise: devise
  };
  var affilie = '';
  if (!ENVOYER_VENTES_AFFILIES) {
    var parFiche = affilieFiche_(f);
    if (parFiche === true) affilie = 'fiche';
    else if (parFiche === null && indices.affilie) affilie = 'webhook';
  }
  return { vente: vente, affilie: affilie };
}

/* true : vente d'affilié, false : vente directe, null : la fiche ne le dit pas. */
function affilieFiche_(f) {
  var a = f.store_affiliate !== undefined ? f.store_affiliate : f.affiliate;
  if (a && typeof a === 'object') return true;
  if (f.channel && f.channel.value) return String(f.channel.value) === 'affiliate';
  if (a === null) return false;
  return null;
}

/* Téléphone de Chariow : objet { number, country: { dial_code } } dans la fiche, ou texte. */
function telephoneBrut_(ph) {
  if (ph && typeof ph === 'object') {
    return { texte: ph.number === undefined || ph.number === null ? '' : String(ph.number),
             indicatif: String((ph.country && ph.country.dial_code) || '') };
  }
  return { texte: ph ? String(ph) : '', indicatif: '' };
}

/* ---------------- Envoi à Meta (API Conversions) ---------------- */
/* codeTest : seulement pour testerAchatFictif(). Les vraies ventes n'ont jamais de test_event_code. */
function envoyerPurchase_(v, signal, nomProduit, codeTest) {
  var jeton = proprietes_().getProperty('META_ACCESS_TOKEN') || '';
  if (!jeton) return { attendre: true, message: 'En attente : jeton META_ACCESS_TOKEN absent' };
  var tempsSec = Math.floor(Math.min(v.temps, Date.now()) / 1000);
  if (Date.now() / 1000 - tempsSec > 7 * 24 * 3600 - 3600) return { ok: false, message: 'vente de plus de 7 jours, Meta la refuserait' };

  var u = {};
  var em = String(v.email || '').trim().toLowerCase();
  if (em) { u.em = [sha256_(em)]; u.external_id = [sha256_(em)]; }
  var ph = telephone_(v.telephone, v.indicatif);
  if (ph) u.ph = [sha256_(ph)];
  if (nomPropre_(v.prenom)) u.fn = [sha256_(nomPropre_(v.prenom))];
  if (nomPropre_(v.nom)) u.ln = [sha256_(nomPropre_(v.nom))];
  if (/^[a-z]{2}$/i.test(v.pays)) u.country = [sha256_(v.pays.toLowerCase())];
  if (ipValide_(v.ip)) u.client_ip_address = ipValide_(v.ip);
  var ua = v.ua || (signal && signal.ua) || '';
  if (ua) u.client_user_agent = ua;
  else journal_('Attention', v.id + ' : navigateur (client_user_agent) inconnu, achat envoyé quand même');
  if (signal && signal.fbp) u.fbp = signal.fbp;
  if (signal && signal.fbc) u.fbc = signal.fbc;

  var corps = { data: [{
    event_name: 'Purchase',
    event_time: tempsSec,
    event_id: v.id,
    action_source: 'website',
    event_source_url: (signal && signal.url) || v.url || SITE,
    user_data: u,
    custom_data: { value: v.valeur, currency: v.devise, content_ids: [PRODUIT_ID], content_type: 'product',
                   content_name: nomProduit || NOM_PRODUIT, order_id: v.id }
  }] };
  if (codeTest) corps.test_event_code = codeTest;

  var rep;
  try {
    rep = UrlFetchApp.fetch('https://graph.facebook.com/' + VERSION_API_META + '/' + PIXEL_ID + '/events?access_token=' + encodeURIComponent(jeton), {
      method: 'post', contentType: 'application/json', payload: JSON.stringify(corps), muteHttpExceptions: true
    });
  } catch (err) {
    return { ok: false, reessayer: true, message: 'Meta injoignable' };
  }
  var code = rep.getResponseCode(), texte = sansSecret_(rep.getContentText() || '');
  var r = {};
  try { r = JSON.parse(texte) || {}; } catch (err) {}
  journal_('Réponse Meta', v.id + ' : code ' + code + ' ' + texte.slice(0, 300));
  if (code === 200 && r.events_received >= 1) {
    return { ok: true, message: 'Envoyé' + (codeTest ? ' (test)' : '') + ', events_received=' + r.events_received };
  }
  var codeErreur = r.error && r.error.code;
  if (code === 401 || code === 403 || codeErreur === 190 || codeErreur === 102) {
    return { attendre: true, message: 'En attente : jeton Meta refusé (code ' + (codeErreur || code) + '). Remplace META_ACCESS_TOKEN.' };
  }
  var msg = 'code ' + code + ' ' + String((r.error && r.error.message) || texte).slice(0, 150);
  return { ok: false, reessayer: code >= 500 || code === 429 || (code === 200 && !(r.events_received >= 1)), message: msg };
}

/* ---------------- Déclencheur toutes les 5 minutes ---------------- */
function envoyerEnAttente() {
  var props = proprietes_();
  var vus = {};   // ventes déjà vérifiées pendant ce passage : pas deux lectures Chariow
  var tout = props.getProperties();
  Object.keys(tout).forEach(function (cle) {
    if (cle.indexOf('brut_') !== 0) return;
    try {
      var id = cle.slice(5), indices = JSON.parse(tout[cle]), res = '';
      var fait = avecVerrou_(function () { res = accepterVente_(id, indices, vus); });
      if (fait && res !== 'plein') props.deleteProperty(cle);
    } catch (err) { journal_('ERREUR', cle + ' : ' + err.message); }
  });
  avecVerrou_(function () {
    var maintenant = Date.now();
    var tout2 = props.getProperties();
    Object.keys(tout2).forEach(function (cle) {
      try {
        if (cle.indexOf('vente_') === 0) {
          var val = JSON.parse(tout2[cle]);
          if (val.etape === 'verif' || val.etape === 'attente') {
            if (!vus[val.id]) avancer_(val);
          } else if (maintenant - (val.t || 0) > GARDER_JOURS * JOUR) {
            props.deleteProperty(cle);   // vente terminée depuis plus de 10 jours
          }
        } else if (cle.indexOf('signal_') === 0) {
          var sig = JSON.parse(tout2[cle]);
          if (maintenant - (sig.t || 0) > JOUR) {
            props.deleteProperty(cle);
            if (!props.getProperty('vente_' + cle.slice(7))) {
              journal_('Signal sans vente', cle.slice(7) + ' : aucun webhook avec cet identifiant en 24 h');
            }
          }
        }
      } catch (err) { journal_('ERREUR', cle + ' : ' + err.message); }
    });
  });
}

/* ---------------- À lancer à la main depuis l'éditeur ---------------- */
function verifierConfiguration() {
  var props = proprietes_(), lignes = [];
  var jeton = props.getProperty('META_ACCESS_TOKEN') || '';
  var cle = props.getProperty('CHARIOW_API_KEY') || '';
  var codeTest = (props.getProperty('META_TEST_EVENT_CODE') || '').trim();
  lignes.push(jeton ? 'OK : META_ACCESS_TOKEN est rempli (' + jeton.length + ' caractères).'
    : 'MANQUE : META_ACCESS_TOKEN. Sans lui, aucun achat ne part vers Meta (les ventes attendent).');
  lignes.push(cle ? 'OK : CHARIOW_API_KEY est rempli (' + cle.length + ' caractères).'
    : 'MANQUE : CHARIOW_API_KEY. Sans elle, le robot ne peut pas vérifier les ventes : rien ne part.');
  lignes.push(codeTest ? 'OK : META_TEST_EVENT_CODE est rempli. Il sert seulement à testerAchatFictif ; les vraies ventes partent toujours normalement.'
    : 'Info : META_TEST_EVENT_CODE est vide. testerAchatFictif refusera de partir (normal en dehors des tests).');
  var dejaLa = ScriptApp.getProjectTriggers().some(function (t) { return t.getHandlerFunction() === 'envoyerEnAttente'; });
  if (!dejaLa) ScriptApp.newTrigger('envoyerEnAttente').timeBased().everyMinutes(5).create();
  lignes.push(dejaLa ? 'OK : le déclencheur « envoyerEnAttente » (toutes les 5 min) existe.'
    : 'Fait : déclencheur « envoyerEnAttente » (toutes les 5 min) installé.');
  feuille_('Ventes', ENTETES_VENTES); feuille_('_Debug', ENTETES_DEBUG);
  lignes.push('OK : onglets « Ventes » et « _Debug » prêts. Ventes en attente : ' +
    (compterEtapes_('verif') + compterEtapes_('attente') + compterPrefixe_('brut_')) + '.');
  var texte = lignes.join('\n');
  Logger.log(texte);
  return texte;
}

/* Envoie un Purchase FICTIF, seulement vers l'onglet « Tester les événements ». */
function testerAchatFictif() {
  var codeTest = (proprietes_().getProperty('META_TEST_EVENT_CODE') || '').trim();
  if (!codeTest) {
    var refus = 'Refusé : remplis d\'abord META_TEST_EVENT_CODE (onglet « Tester les événements »). Sans ce code, un achat fictif irait dans tes vraies données.';
    Logger.log(refus);
    return refus;
  }
  var v = { id: 'TEST-' + Date.now(), temps: Date.now(), email: 'test.robot@livensya.invalid', telephone: '+229 01 00 00 00 00',
            prenom: 'Test', nom: 'Robot', pays: 'BJ', indicatif: '+229', ip: '', ua: 'Mozilla/5.0 (test robot achat Livensya)',
            valeur: PRIX, devise: DEVISE, url: SITE };
  var res = envoyerPurchase_(v, null, 'TEST robot achat (fictif)', codeTest);
  var texte = (res.ok ? 'Achat fictif envoyé avec le code de test. Regarde l\'onglet « Tester les événements ». ' : 'Échec : ') + res.message;
  journal_('Test fictif', texte);
  Logger.log(texte);
  return texte;
}

/* ---------------- Outils ---------------- */
var ENTETES_VENTES = ['Date de la vente', 'ID vente', 'Prénom', 'E-mail', 'Montant', 'IP (masquée)', 'Signal page', 'Statut Meta', 'Mis à jour'];
var ENTETES_DEBUG = ['Date', 'Quoi', 'Détail'];

function proprietes_() { return PropertiesService.getScriptProperties(); }
function json_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function idValide_(x) { var s = String(x || ''); return /^[A-Za-z0-9_-]{3,100}$/.test(s) ? s : ''; }

/* Boutique Livensya : on se fie à store.id. L'adresse ne sert que si l'id manque, et ne bloque jamais
   (la clé API Chariow est celle de la boutique Livensya : une vente d'une autre boutique y est introuvable). */
function boutiqueLivensya_(store) {
  store = store || {};
  if (store.id) return String(store.id) === BOUTIQUE_ID;
  var m = /^https?:\/\/([^\/:?#]+)/i.exec(String(store.url || ''));
  if (m && m[1].toLowerCase() !== BOUTIQUE_URL) journal_('Attention', 'adresse de boutique inattendue : ' + m[1]);
  return true;
}

function lireEtat_(id) { var b = proprietes_().getProperty('vente_' + id); return b ? JSON.parse(b) : null; }
function ecrireEtat_(etat) { proprietes_().setProperty('vente_' + etat.id, JSON.stringify(etat)); }
function compterPrefixe_(p) { return Object.keys(proprietes_().getProperties()).filter(function (k) { return k.indexOf(p) === 0; }).length; }
function compterEtapes_(etape) {
  var tout = proprietes_().getProperties();
  return Object.keys(tout).filter(function (k) { return k.indexOf('vente_') === 0 && tout[k].indexOf('"etape":"' + etape + '"') > -1; }).length;
}

function avecVerrou_(fn) {
  var verrou = LockService.getScriptLock();
  if (!verrou.tryLock(30000)) return false;
  try { fn(); } finally { verrou.releaseLock(); }
  return true;
}

function sha256_(texte) {
  return Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, String(texte), Utilities.Charset.UTF_8)
    .map(function (b) { return ('0' + (b & 255).toString(16)).slice(-2); }).join('');
}

/* Prénom, nom : minuscules, sans espaces ni ponctuation (règle Meta), accents gardés (UTF-8). */
function nomPropre_(t) { return String(t || '').toLowerCase().replace(/[\s\p{P}\p{S}]/gu, ''); }

/* Téléphone au format international, chiffres seulement (ex. 2290197000000). Vide si l'indicatif est inconnu. */
function telephone_(brut, indicatif) {
  var s = String(brut || '').trim(), chiffres = s.replace(/\D/g, '');
  if (chiffres.length < 6) return '';
  if (s.charAt(0) === '+') return chiffres.replace(/^0+/, '');
  if (chiffres.indexOf('00') === 0) return chiffres.slice(2).replace(/^0+/, '');
  var ind = String(indicatif || '').replace(/\D/g, '');
  if (!ind) return '';
  if (chiffres.indexOf(ind) === 0 && chiffres.length >= ind.length + 8) return chiffres;
  return ind + (ind === '229' ? chiffres : chiffres.replace(/^0+/, ''));   // Bénin : le 0 de « 01 » fait partie du numéro
}

/* IP gardée seulement si c'est une IPv4 ou IPv6 valide et publique (sinon Meta rejetterait l'événement). */
function ipValide_(ip) {
  var v = String(ip || '').trim().toLowerCase();
  if (!v || v.length > 45) return '';
  if (v.indexOf(':') === -1) return ipv4Publique_(v) ? v : '';
  var mots = ipv6EnMots_(v);
  if (!mots) return '';
  var debutNul = mots.slice(0, 7).every(function (m) { return m === 0; });
  if (debutNul && (mots[7] === 0 || mots[7] === 1)) return '';           // :: et ::1
  if ((mots[0] & 0xffc0) === 0xfe80 || (mots[0] & 0xfe00) === 0xfc00) return '';   // locales
  if (mots.slice(0, 5).every(function (m) { return m === 0; }) && mots[5] === 0xffff) {
    return ipv4Publique_([mots[6] >> 8, mots[6] & 255, mots[7] >> 8, mots[7] & 255].join('.')) ? v : '';
  }
  return v;
}
var IPV4_ = /^(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}$/;
function ipv4Publique_(v) {
  if (!IPV4_.test(v)) return false;
  var o = v.split('.').map(Number);
  return !(o[0] === 0 || o[0] === 10 || o[0] === 127 || (o[0] === 172 && o[1] >= 16 && o[1] <= 31) ||
           (o[0] === 192 && o[1] === 168) || (o[0] === 169 && o[1] === 254) || o[0] >= 224);
}
function ipv6EnMots_(v) {
  if (!/^[0-9a-f:.]+$/.test(v)) return null;
  var morceaux = v.split('::');
  if (morceaux.length > 2) return null;
  var compresse = morceaux.length === 2;
  var gauche = morceaux[0] ? morceaux[0].split(':') : [];
  var droite = compresse ? (morceaux[1] ? morceaux[1].split(':') : []) : [];
  var queue = compresse ? droite : gauche, finV4 = null;
  if (queue.length && queue[queue.length - 1].indexOf('.') !== -1) {
    finV4 = queue.pop();
    if (!IPV4_.test(finV4)) return null;
  }
  var groupes = gauche.concat(droite);
  if (!groupes.every(function (g) { return /^[0-9a-f]{1,4}$/.test(g); })) return null;
  var total = groupes.length + (finV4 ? 2 : 0);
  if (compresse ? total > 7 : total !== 8) return null;
  var g = gauche.map(function (x) { return parseInt(x, 16); }), d = droite.map(function (x) { return parseInt(x, 16); });
  if (finV4) { var o = finV4.split('.').map(Number); d.push(o[0] * 256 + o[1], o[2] * 256 + o[3]); }
  if (!compresse) return g.concat(d);
  var zeros = [];
  for (var k = 0; k < 8 - g.length - d.length; k++) zeros.push(0);
  return g.concat(zeros, d);
}

function masquerIp_(ip) {
  var v = String(ip || '');
  if (!v) return '';
  if (v.indexOf(':') !== -1) return v.split(':').slice(0, 2).join(':') + ':…';
  var o = v.split('.');
  return o.length === 4 ? o[0] + '.' + o[1] + '.x.x' : '(masquée)';
}

/* Retire tout secret (jeton Meta, clé Chariow) et masque les IP d'un texte avant de l'écrire. */
function sansSecret_(texte) {
  var t = String(texte);
  ['META_ACCESS_TOKEN', 'CHARIOW_API_KEY'].forEach(function (nom) {
    var s = proprietes_().getProperty(nom);
    if (s && s.length >= 8) t = t.split(s).join('[masqué]');
  });
  return t.replace(/\b(\d{1,3})\.(\d{1,3})\.\d{1,3}\.\d{1,3}\b/g, '$1.$2.x.x');
}

function feuille_(nom, entetes) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var f = ss.getSheetByName(nom) || ss.insertSheet(nom);
  if (f.getLastRow() === 0) { f.appendRow(entetes); f.setFrozenRows(1); }
  return f;
}

function journal_(quoi, detail) {
  try { feuille_('_Debug', ENTETES_DEBUG).appendRow([new Date(), quoi, sansSecret_(detail).slice(0, 500)]); } catch (err) {}
}

function ligneVente_(v, statut) {
  feuille_('Ventes', ENTETES_VENTES).appendRow([new Date(v.temps || Date.now()), v.id, v.prenom || '', v.email || '',
    (v.valeur === undefined ? '' : v.valeur + ' ' + v.devise), masquerIp_(v.ip), 'non', statut, new Date()]);
}

/* Statut Meta de la dernière ligne de cette vente dans l'onglet Ventes ('' si aucune). */
function statutVente_(id) {
  var f = feuille_('Ventes', ENTETES_VENTES), n = f.getLastRow();
  if (n < 2) return '';
  var lignes = f.getRange(2, 2, n - 1, 7).getValues();
  for (var i = lignes.length - 1; i >= 0; i--) if (String(lignes[i][0]) === id) return String(lignes[i][6]);
  return '';
}

function majStatut_(id, statut, signal) {
  var f = feuille_('Ventes', ENTETES_VENTES), n = f.getLastRow();
  if (n < 2) return;
  var ids = f.getRange(2, 2, n - 1, 1).getValues();
  for (var i = ids.length - 1; i >= 0; i--) {
    if (String(ids[i][0]) === id) {
      if (signal) f.getRange(i + 2, 7).setValue((signal.fbp ? 'fbp ' : '') + (signal.fbc ? 'fbc' : '') || 'oui');
      f.getRange(i + 2, 8).setValue(statut);
      f.getRange(i + 2, 9).setValue(new Date());
      return;
    }
  }
}
