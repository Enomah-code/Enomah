// Simulateur minimal de Google Apps Script pour tester Code.gs SANS réseau :
// aucun appel réel à Meta ni à Chariow, tout est imité ici.
const fs = require('fs'), path = require('path'), crypto = require('crypto');

const JETON = 'EAAfauxjeton' + 'x'.repeat(30);           // faux secrets, seulement pour vérifier qu'ils ne fuient pas
const CLE_CHARIOW = 'sk_live_faussecle' + 'y'.repeat(20);

function charger({ jeton = JETON, cleChariow = CLE_CHARIOW, codeTest = '' } = {}) {
  const props = new Map();
  if (jeton) props.set('META_ACCESS_TOKEN', jeton);
  if (cleChariow) props.set('CHARIOW_API_KEY', cleChariow);
  if (codeTest) props.set('META_TEST_EVENT_CODE', codeTest);
  const feuilles = {}, envoisMeta = [], lecturesChariow = [], declencheurs = [], logs = [];
  const fiches = {};                      // id -> fiche Chariow (ou { code: 404/500 })
  const reponsesMeta = [];                // file de réponses Meta imposées ({ code, corps } ou 'exception')
  const pannes = { verrouLibre: true, bloquerEcriture: null };   // bloquerEcriture(cle, valeur) -> true : setProperty échoue
  let horloge = Date.parse('2026-10-09T10:00:00Z');
  const VraieDate = Date;
  class FausseDate extends VraieDate {
    constructor(...a) { if (a.length) super(...a); else super(horloge); }
    static now() { return horloge; }
  }

  function feuille(nom) {
    const lignes = [];
    return {
      _lignes: lignes,
      getLastRow: () => lignes.length,
      appendRow: v => lignes.push([...v]),
      setFrozenRows: () => {},
      getRange: (r, c, nr = 1, nc = 1) => ({
        getValues: () => Array.from({ length: nr }, (_, i) => Array.from({ length: nc }, (_, j) => (lignes[r - 1 + i] || [])[c - 1 + j] ?? '')),
        setValue: x => { lignes[r - 1][c - 1] = x; },
      }),
    };
  }
  const classeur = { getSheetByName: n => feuilles[n] || null, insertSheet: n => (feuilles[n] = feuille(n)) };

  const UrlFetchApp = {
    fetch(url, o) {
      if (url.startsWith('https://api.chariow.com/v1/sales/')) {
        const id = decodeURIComponent(url.split('/').pop());
        lecturesChariow.push({ id, auth: o.headers.Authorization });
        const f = fiches[id];
        if (f === 'exception') throw new Error('réseau coupé');
        if (!f) return rep(404, { message: 'Sale not found' });
        if (f.code) return rep(f.code, { message: 'erreur' });
        return rep(200, { message: 'success', data: f });
      }
      if (url.startsWith('https://graph.facebook.com/')) {
        envoisMeta.push({ url, corps: JSON.parse(o.payload) });
        const r = reponsesMeta.shift() || { code: 200, corps: { events_received: 1, messages: [], fbtrace_id: 'Atrace' } };
        if (r === 'exception') throw new Error('délai dépassé');
        return rep(r.code, r.corps);
      }
      throw new Error('Appel réseau inattendu : ' + url);
    },
  };
  const rep = (code, corps) => ({ getResponseCode: () => code, getContentText: () => JSON.stringify(corps) });

  const bac = {
    Date: FausseDate, JSON, Math, String, Number, Object, Array, Error, RegExp, parseInt, encodeURIComponent, console,
    Logger: { log: t => logs.push(String(t)) },
    SpreadsheetApp: { getActiveSpreadsheet: () => classeur },
    PropertiesService: { getScriptProperties: () => ({
      getProperty: k => props.get(k) ?? null,
      setProperty: (k, v) => { if (pannes.bloquerEcriture && pannes.bloquerEcriture(k, String(v))) throw new Error('écriture refusée (simulée)'); props.set(k, String(v)); },
      deleteProperty: k => { props.delete(k); }, getProperties: () => Object.fromEntries(props) }) },
    LockService: { getScriptLock: () => ({ tryLock: () => pannes.verrouLibre, releaseLock: () => {} }) },
    UrlFetchApp,
    Utilities: { DigestAlgorithm: { SHA_256: 'sha256' }, Charset: { UTF_8: 'utf8' },
      computeDigest: (a, t) => [...crypto.createHash('sha256').update(String(t), 'utf8').digest()].map(b => (b > 127 ? b - 256 : b)) },
    ContentService: { MimeType: { JSON: 'json' }, createTextOutput: t => ({ setMimeType: () => ({ texte: t }) }) },
    ScriptApp: {
      getProjectTriggers: () => declencheurs.map(n => ({ getHandlerFunction: () => n })),
      newTrigger: n => ({ timeBased: () => ({ everyMinutes: () => ({ create: () => declencheurs.push(n) }) }) }),
    },
  };
  const code = fs.readFileSync(path.join(__dirname, '..', 'Code.gs'), 'utf8');
  const exporte = ['doPost', 'doGet', 'envoyerEnAttente', 'verifierConfiguration', 'testerAchatFictif', 'ipValide_', 'telephone_', 'sha256_'];
  const api = new Function(...Object.keys(bac), code + '\nreturn {' + exporte.join(',') + '};')(...Object.values(bac));
  return { api, props, feuilles, envoisMeta, lecturesChariow, declencheurs, logs, fiches, reponsesMeta, pannes,
           avancer: ms => { horloge += ms; }, maintenant: () => horloge };
}

/* Données de test : forme RÉELLE d'une fiche Chariow (get_sale, boutique EMK, données personnelles remplacées) */
const fiche = (id, plus = {}) => Object.assign({
  id, status: 'settled', channel: { value: 'widget' },
  amount: { value: 3999, formatted: 'F CFA 3,999', currency: 'XOF' }, original_amount: { value: 3999, currency: 'XOF' },
  payment: { status: 'success', method: { name: 'MTN MoMo' }, amount: { value: 4119, currency: 'XAF' } },
  context: { user_agent: 'Mozilla/5.0 (Linux; Android 14) Chariow', ip_address: '160.155.244.158', country: { code: 'BJ' }, device_type: 'mobile', locale: 'fr' },
  store: { id: 'store_6is731jk2ybk', name: 'Livensya', url: 'https://ykhzgspm.mychariow.store' },
  product: { id: 'prd_4bisyd7x', name: 'Défi 60 jours' },
  customer: { id: 'cus_1', first_name: 'Awa', last_name: 'Kossou', email: 'Awa.Test@Gmail.com ',
              phone: { number: 2290197000000, country: { code: 'BJ', dial_code: '+229' } } },
  campaign: null, failed_at: null, abandoned_at: null,
  completed_at: '2026-10-09T09:59:30.000000Z', created_at: '2026-10-09T09:57:10.000000Z',
}, plus);
const webhook = (id, plus = {}) => Object.assign({
  event: 'successful.sale',
  sale: { id, status: 'completed', amount: { value: 3999, currency: 'XOF' }, completed_at: '2026-10-09T09:59:30+00:00' },
  product: { id: 'prd_4bisyd7x', name: 'Défi 60 jours' },
  customer: { email: 'awa.test@gmail.com', first_name: 'Awa', last_name: 'Kossou', phone: '+229 01 97 00 00 00', country: 'BJ' },
  affiliate: null, checkout: { url: 'https://ykhzgspm.mychariow.store/checkout/' + id },
  store: { id: 'store_6is731jk2ybk', name: 'Livensya', url: 'https://ykhzgspm.mychariow.store' },
}, plus);
const signal = id => ({ purchaseId: id, _fbp: 'fb.1.1760000000000.1234567890', _fbc: 'fb.1.1760000000000.IwAR0abc_DEF-123',
  _userAgent: 'Mozilla/5.0 (Linux; Android 14) Page', _eventSourceUrl: 'https://livensya.emkbluediamond.online/?fbclid=IwAR0abc' });
const post = (e, obj) => e.api.doPost({ postData: { contents: JSON.stringify(obj), type: 'text/plain' } });
const purchases = e => e.envoisMeta.map(x => x.corps.data[0]).filter(d => d.event_name === 'Purchase');
const ventes = e => (e.feuilles['Ventes'] ? e.feuilles['Ventes']._lignes.slice(1) : []);
const debug = e => (e.feuilles['_Debug'] ? e.feuilles['_Debug']._lignes.slice(1).map(l => l[1] + ' | ' + l[2]) : []);
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');

let echecs = 0, total = 0;
const verifier = (ok, texte) => { total++; console.log((ok ? '  OK    ' : '  ÉCHEC ') + texte); if (!ok) echecs++; };
module.exports = { charger, fiche, webhook, signal, post, purchases, ventes, debug, sha, verifier, JETON, CLE_CHARIOW,
                   bilan: () => ({ echecs, total }) };
