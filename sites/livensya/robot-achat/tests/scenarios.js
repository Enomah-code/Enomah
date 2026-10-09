// Lancer : node sites/livensya/robot-achat/tests/scenarios.js
const s = require('./simulateur');
const MIN = 60 * 1000;
let e, p;

console.log('\n1. Vente valide : webhook, puis signal de la page 5 s après');
e = s.charger(); e.fiches.sal_A1 = s.fiche('sal_A1');
s.post(e, s.webhook('sal_A1'));
s.verifier(s.purchases(e).length === 0, 'au webhook : rien envoyé, on attend le signal');
s.verifier(e.lecturesChariow.length === 1 && e.lecturesChariow[0].id === 'sal_A1', 'fiche Chariow relue une fois');
s.verifier(s.ventes(e).length === 1 && s.ventes(e)[0][7] === 'En attente du signal de la page', 'onglet Ventes : en attente');
e.avancer(5000); s.post(e, s.signal('sal_A1'));
p = s.purchases(e);
s.verifier(p.length === 1, '1 seul Purchase (' + p.length + ')');
const d = p[0] || { user_data: {}, custom_data: {} }, u = d.user_data;
s.verifier(d.event_id === 'sal_A1' && d.action_source === 'website', 'event_id = ID de la vente, action_source website');
s.verifier(d.event_time === Date.parse('2026-10-09T09:59:30Z') / 1000, 'event_time = heure de la vente, en secondes');
s.verifier(d.event_source_url === 'https://livensya.emkbluediamond.online/?fbclid=IwAR0abc', 'event_source_url = page du signal');
s.verifier(d.custom_data.value === 3999 && d.custom_data.currency === 'XOF' && d.custom_data.content_ids[0] === 'prd_4bisyd7x', 'value 3999, XOF, content_ids prd_4bisyd7x');
s.verifier(u.em[0] === s.sha('awa.test@gmail.com') && u.external_id[0] === u.em[0], 'e-mail normalisé puis haché (em, external_id)');
s.verifier(u.ph[0] === s.sha('2290197000000'), 'téléphone +229 01 97 00 00 00 -> 2290197000000 haché');
s.verifier(u.fn[0] === s.sha('awa') && u.ln[0] === s.sha('kossou') && u.country[0] === s.sha('bj'), 'prénom, nom, pays hachés');
s.verifier(u.client_ip_address === '160.155.244.158', 'IP du paiement (fiche Chariow), en clair');
s.verifier(u.client_user_agent === 'Mozilla/5.0 (Linux; Android 14) Chariow', 'navigateur du paiement (fiche Chariow)');
s.verifier(u.fbp === 'fb.1.1760000000000.1234567890' && u.fbc === 'fb.1.1760000000000.IwAR0abc_DEF-123', 'fbp et fbc du signal');
s.verifier(!('test_event_code' in e.envoisMeta[0].corps), 'pas de test_event_code en mode normal');
s.verifier(e.envoisMeta[0].url.startsWith('https://graph.facebook.com/v25.0/5010730402487338/events'), 'API Meta v25.0, Pixel Livensya');
s.verifier(String(s.ventes(e)[0][7]).startsWith('Envoyé') && s.ventes(e)[0][6] === 'fbp fbc', 'onglet Ventes : ' + s.ventes(e)[0][7]);
s.verifier(s.ventes(e)[0][5] === '160.155.x.x', 'IP masquée dans l\'onglet Ventes');
e.avancer(20 * MIN); e.api.envoyerEnAttente();
s.verifier(s.purchases(e).length === 1, 'déclencheur des 5 min : pas de doublon');

console.log('\n2. Webhook renvoyé 2 fois (et une 3e fois après l\'envoi), signal répété, rechargement');
e = s.charger(); e.fiches.sal_B2 = s.fiche('sal_B2');
s.post(e, s.webhook('sal_B2')); s.post(e, s.webhook('sal_B2'));
s.post(e, s.signal('sal_B2')); s.post(e, s.signal('sal_B2'));
s.post(e, s.webhook('sal_B2'));
e.avancer(30 * MIN); e.api.envoyerEnAttente();
s.verifier(s.purchases(e).length === 1, '1 seul Purchase (' + s.purchases(e).length + ')');
s.verifier(s.ventes(e).length === 1, '1 seule ligne dans Ventes');
s.verifier(e.lecturesChariow.length === 1, 'fiche Chariow lue une seule fois');
s.verifier(s.debug(e).filter(l => l.startsWith('Doublon ignoré')).length === 2, '2 renvois notés « Doublon ignoré » dans _Debug');

console.log('\n3. Signal AVANT le webhook');
e = s.charger(); e.fiches.sal_C3 = s.fiche('sal_C3');
s.post(e, s.signal('sal_C3'));
s.verifier(s.purchases(e).length === 0, 'signal seul : rien envoyé (un signal ne crée jamais d\'achat)');
s.post(e, s.webhook('sal_C3'));
p = s.purchases(e);
s.verifier(p.length === 1 && p[0].user_data.fbp && p[0].user_data.fbc, 'webhook : Purchase envoyé tout de suite, avec fbp/fbc');

console.log('\n4. Signal absent (acheteur parti) : envoi sans fbp/fbc après l\'attente');
e = s.charger(); e.fiches.sal_D4 = s.fiche('sal_D4');
s.post(e, s.webhook('sal_D4'));
e.avancer(5 * MIN); e.api.envoyerEnAttente();
s.verifier(s.purchases(e).length === 0, 'à 5 min : toujours en attente');
e.avancer(6 * MIN); e.api.envoyerEnAttente();
p = s.purchases(e);
s.verifier(p.length === 1 && !p[0].user_data.fbp && !p[0].user_data.fbc, 'à 11 min : Purchase envoyé sans fbp/fbc');
s.verifier(p[0] && p[0].user_data.client_ip_address && p[0].user_data.client_user_agent && p[0].event_source_url === 'https://livensya.emkbluediamond.online/', 'IP, navigateur et adresse du site quand même présents');
s.verifier(s.ventes(e)[0][6] === 'non', 'onglet Ventes : signal page « non »');
s.post(e, s.signal('sal_D4'));
s.verifier(s.purchases(e).length === 1, 'signal arrivé trop tard : ignoré, pas de 2e envoi');

console.log('\n5. Autre produit, autre boutique : ignorés');
e = s.charger();
s.post(e, s.webhook('sal_E5', { product: { id: 'prd_qh7md6nj' } }));
s.post(e, s.webhook('sal_E6', { store: { url: 'https://emkbluediamond.mychariow.shop' } }));
s.verifier(s.purchases(e).length === 0 && e.lecturesChariow.length === 0 && s.ventes(e).length === 0, 'aucun envoi, aucune lecture Chariow, aucune ligne Ventes');
e.fiches.sal_E7 = s.fiche('sal_E7', { product: { id: 'prd_autre' } });
s.post(e, s.webhook('sal_E7'));
s.verifier(s.purchases(e).length === 0 && s.debug(e).some(l => l.includes('autre produit')), 'webhook qui ment sur le produit : la fiche Chariow le refuse');
s.post(e, { event: 'abandoned.sale', sale: { id: 'sal_E8' }, product: { id: 'prd_4bisyd7x' } });
s.verifier(s.purchases(e).length === 0, 'panier abandonné : ignoré');

console.log('\n6. Faux webhook sur le /exec public (vente inexistante chez Chariow)');
e = s.charger();
s.post(e, s.webhook('sal_FAUX'));
e.avancer(30 * MIN); e.api.envoyerEnAttente();
s.post(e, s.webhook('sal_FAUX'));
s.verifier(s.purchases(e).length === 0, 'aucun Purchase');
s.verifier(s.ventes(e).length === 0, 'aucune ligne dans Ventes');
s.verifier(s.debug(e).some(l => l.startsWith('Refusé') && l.includes('inconnue')), '_Debug : « Refusé : vente inconnue chez Chariow »');
s.verifier(![...e.props.keys()].some(k => k.startsWith('vente_')), 'rien gardé en mémoire pour ce faux appel');
e = s.charger(); e.fiches.sal_F2 = s.fiche('sal_F2', { status: 'failed', payment: { status: 'failed' } });
s.post(e, s.webhook('sal_F2'));
s.verifier(s.purchases(e).length === 0, 'vente réelle mais échouée : aucun Purchase');

console.log('\n7. IP invalide ou privée écartée');
for (const ip of ['192.168.1.10', '10.0.0.1', '1.2.3', 'abc', '::1', 'fe80::1', ' 160.155.244.158 x']) {
  e = s.charger(); e.fiches.sal_G = s.fiche('sal_G', { context: { ip_address: ip, user_agent: 'UA', country: { code: 'BJ', dial_code: '+229' } } });
  s.post(e, s.webhook('sal_G')); s.post(e, s.signal('sal_G'));
  p = s.purchases(e);
  s.verifier(p.length === 1 && !('client_ip_address' in p[0].user_data), 'IP « ' + ip + ' » non envoyée, achat envoyé quand même');
}
s.verifier(e.api.ipValide_('2c0f:f0f8:1::5') === '2c0f:f0f8:1::5' && e.api.ipValide_('::ffff:192.168.0.1') === '', 'IPv6 publique gardée, IPv4 privée déguisée écartée');

console.log('\n8. Mode test : META_TEST_EVENT_CODE rempli');
e = s.charger({ codeTest: 'TEST12345' }); e.fiches.sal_H8 = s.fiche('sal_H8');
s.post(e, s.webhook('sal_H8')); s.post(e, s.signal('sal_H8'));
s.verifier(e.envoisMeta.length === 1 && e.envoisMeta[0].corps.test_event_code === 'TEST12345', 'envoi avec test_event_code en haut de la requête');
s.verifier(String(s.ventes(e)[0][7]).includes('mode test'), 'onglet Ventes : ' + s.ventes(e)[0][7]);

console.log('\n9. testerAchatFictif');
e = s.charger();
let r = e.api.testerAchatFictif();
s.verifier(e.envoisMeta.length === 0 && r.startsWith('Refusé'), 'sans code de test : refusé, rien envoyé');
e = s.charger({ codeTest: 'TEST999' });
r = e.api.testerAchatFictif();
p = e.envoisMeta[0] && e.envoisMeta[0].corps;
s.verifier(e.envoisMeta.length === 1 && p.test_event_code === 'TEST999', 'avec code : 1 envoi, avec test_event_code');
s.verifier(p && p.data[0].event_id.startsWith('TEST-') && p.data[0].custom_data.content_name.startsWith('TEST'), 'clairement marqué TEST (event_id et content_name)');
s.verifier(s.ventes(e).length === 0, 'n\'écrit rien dans l\'onglet Ventes');

console.log('\n10. Pannes : Chariow puis Meta');
e = s.charger(); e.fiches.sal_J1 = { code: 500 };
s.post(e, s.webhook('sal_J1'));
s.verifier(s.purchases(e).length === 0 && s.debug(e).some(l => l.startsWith('Nouvel essai')), 'Chariow en panne : vente gardée, nouvel essai prévu');
e.fiches.sal_J1 = s.fiche('sal_J1'); e.avancer(5 * MIN); e.api.envoyerEnAttente();
s.verifier(s.ventes(e).length === 1, 'Chariow revenu : vente vérifiée au passage suivant');
e.reponsesMeta.push({ code: 500, corps: { error: { message: 'Service temporairement indisponible' } } });
e.avancer(6 * MIN); e.api.envoyerEnAttente();
s.verifier(String(s.ventes(e)[0][7]).startsWith('Erreur Meta, nouvel essai'), 'Meta 500 : ' + s.ventes(e)[0][7]);
e.avancer(5 * MIN); e.api.envoyerEnAttente();
e.avancer(5 * MIN); e.api.envoyerEnAttente();
s.verifier(e.envoisMeta.length === 2 && String(s.ventes(e)[0][7]).startsWith('Envoyé'), '2e essai réussi, puis plus rien (2 appels au total)');
e = s.charger(); e.fiches.sal_J2 = s.fiche('sal_J2');
e.reponsesMeta.push({ code: 400, corps: { error: { message: 'Invalid parameter' } } });
s.post(e, s.webhook('sal_J2')); s.post(e, s.signal('sal_J2'));
e.avancer(30 * MIN); e.api.envoyerEnAttente();
s.verifier(e.envoisMeta.length === 1 && String(s.ventes(e)[0][7]).startsWith('Échec Meta'), 'Meta 400 : pas de relance inutile, échec noté');
e = s.charger({ jeton: '' }); e.fiches.sal_J3 = s.fiche('sal_J3');
s.post(e, s.webhook('sal_J3')); s.post(e, s.signal('sal_J3'));
s.verifier(e.envoisMeta.length === 0 && String(s.ventes(e)[0][7]).includes('META_ACCESS_TOKEN absent'), 'jeton oublié : la vente attend (' + s.ventes(e)[0][7] + ')');
e.props.set('META_ACCESS_TOKEN', s.JETON); e.api.envoyerEnAttente();
s.verifier(s.purchases(e).length === 1 && s.purchases(e)[0].user_data.fbp, 'jeton ajouté : envoyée au passage suivant, avec fbp');
e = s.charger(); e.fiches.sal_J4 = s.fiche('sal_J4', { status: 'awaiting_payment' });
s.post(e, s.webhook('sal_J4'));
e.fiches.sal_J4 = s.fiche('sal_J4'); e.avancer(5 * MIN); e.api.envoyerEnAttente();
e.avancer(10 * MIN); e.api.envoyerEnAttente();
s.verifier(s.purchases(e).length === 1, 'paiement pas encore confirmé : revérifié puis envoyé une fois');

console.log('\n11. Configuration et secrets');
e = s.charger({ jeton: '', cleChariow: '' });
r = e.api.verifierConfiguration();
s.verifier(r.includes('MANQUE : META_ACCESS_TOKEN') && r.includes('MANQUE : CHARIOW_API_KEY') && r.includes('Mode normal'), 'dit ce qui manque');
s.verifier(e.declencheurs.length === 1 && e.declencheurs[0] === 'envoyerEnAttente', 'installe le déclencheur des 5 min');
e.api.verifierConfiguration();
s.verifier(e.declencheurs.length === 1, 'relancée : pas de 2e déclencheur');
e = s.charger({ codeTest: 'TEST1' });
r = e.api.verifierConfiguration();
s.verifier(r.includes('OK : META_ACCESS_TOKEN') && r.includes('MODE TEST ACTIF'), 'tout rempli : OK, et alerte mode test');
e.fiches.sal_K = s.fiche('sal_K');
e.reponsesMeta.push({ code: 400, corps: { error: { message: 'Bad token ' + s.JETON } } });
s.post(e, s.webhook('sal_K')); s.post(e, s.signal('sal_K'));
const toutTexte = JSON.stringify(e.feuilles) + r + e.logs.join('\n');
s.verifier(!toutTexte.includes(s.JETON) && !toutTexte.includes(s.CLE_CHARIOW), 'aucun secret dans les onglets ni dans le journal, même si Meta le renvoie');
s.verifier(!toutTexte.includes('160.155.244.158'), 'aucune IP complète dans les onglets');
s.verifier(e.lecturesChariow[0].auth === 'Bearer ' + s.CLE_CHARIOW, 'la clé Chariow ne sert qu\'à l\'appel Chariow');
s.verifier(JSON.parse(e.api.doGet().texte).status === 'ok', 'doGet renvoie {status:"ok"}');

console.log('\n12. Divers');
e = s.charger(); e.fiches.sal_L = s.fiche('sal_L', { completed_at: '2026-10-01T09:00:00+00:00' });
s.post(e, s.webhook('sal_L')); s.post(e, s.signal('sal_L'));
s.verifier(e.envoisMeta.length === 0 && String(s.ventes(e)[0][7]).includes('plus de 7 jours'), 'vente de plus de 7 jours : pas envoyée (Meta la refuserait)');
e = s.charger();
for (let i = 0; i < 3; i++) s.post(e, s.signal('sal_inconnue' + i));
e.avancer(25 * 3600 * 1000); e.api.envoyerEnAttente();
s.verifier(![...e.props.keys()].some(k => k.startsWith('signal_')) && s.debug(e).filter(l => l.startsWith('Signal sans vente')).length === 3, 'signaux sans vente effacés après 24 h et signalés (repère si purchaseId ≠ ID de vente)');
s.verifier(e.api.telephone_('97000000', '') === '' && e.api.telephone_('0612345678', '+33') === '33612345678' && e.api.telephone_('0197000000', '+229') === '2290197000000', 'téléphones sans indicatif : complétés ou écartés');
e = s.charger(); e.fiches.sal_M = s.fiche('sal_M');
s.post(e, s.webhook('sal_M', { customer: { email: 'autre@gmail.com', phone: '+22990000000', country: 'BJ' } }));
s.post(e, s.signal('sal_M'));
s.verifier(s.purchases(e).length === 1 && !s.purchases(e)[0].user_data.ph, 'webhook avec un autre e-mail que la fiche : son téléphone n\'est pas utilisé');
e.api.doPost({ postData: { contents: 'pas du json' } });
s.verifier(s.debug(e).some(l => l.startsWith('Ignoré | message illisible')), 'message illisible : ignoré sans erreur');

e = s.charger({ cleChariow: '' });
s.post(e, s.webhook('sal_N'));
for (let i = 0; i < 20; i++) { e.avancer(5 * MIN); e.api.envoyerEnAttente(); }
s.verifier(s.debug(e).filter(l => l.startsWith('Nouvel essai')).length === 1, 'clé Chariow absente : la vente attend, une seule ligne dans _Debug (pas de spam)');
e.props.set('CHARIOW_API_KEY', s.CLE_CHARIOW); e.fiches.sal_N = s.fiche('sal_N', { completed_at: new Date(e.maintenant()).toISOString() });
e.avancer(5 * MIN); e.api.envoyerEnAttente(); e.avancer(15 * MIN); e.api.envoyerEnAttente();
s.verifier(s.purchases(e).length === 1, 'clé ajoutée : la vente est vérifiée puis envoyée une fois');

const b = s.bilan();
console.log('\n' + (b.echecs ? 'ÉCHECS : ' + b.echecs + ' sur ' + b.total : 'TOUT EST OK : ' + b.total + ' vérifications'));
process.exit(b.echecs ? 1 : 0);
