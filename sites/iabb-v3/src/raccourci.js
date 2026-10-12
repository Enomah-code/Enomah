/* ============ ACCUEIL : « Voir directement l'offre de lancement » (ajout v3) ============
   N'envoie AUCUN événement et ne touche à aucune donnée envoyée.
   1. ferme l'accueil et appelle revealProduct(), la fonction existante qui affiche l'offre
      (c'est elle qui envoie OfferReveal, prépare PricingView et InitiateCheckout, comme d'habitude) ;
   2. remplace uniquement des TEXTES AFFICHÉS qui parlent du bilan, puisque ce visiteur n'en a pas fait. */
function texteOffreDirecte(){
  document.body.classList.add('arrivee-directe');
  document.querySelectorAll('[data-direct]').forEach(function(el){ el.textContent = el.getAttribute('data-direct'); });
  var nom = document.getElementById('heroName'); if (nom) nom.textContent = 'Le programme complet';
  var bandeau = document.getElementById('unlockText'); if (bandeau) bandeau.textContent = 'Offre de lancement en cours';
}
function voirOffreDirectement(){
  var reprise = document.getElementById('resumeBanner');
  if (reprise) reprise.remove();
  document.getElementById('welcomeScreen').style.display = 'none';
  revealProduct();
  texteOffreDirecte();
}
/* Retour d'un visiteur passé par ce bouton (pas de prénom enregistré) : même textes neutres. */
(function(){
  var reprise = document.getElementById('resumeBanner');
  if (!reprise || (typeof state !== 'undefined' && state.name)) return;
  var sauve = null;
  try { sauve = JSON.parse(localStorage.getItem('emk_quiz_progress') || 'null'); } catch(e) {}
  if (!sauve || (sauve.state && sauve.state.name)) return;
  reprise.innerHTML = reprise.innerHTML.replace('Bon retour \u202f!', 'Bon retour\u202f!').replace('Ton offre personnalisée', 'Ton offre de lancement');
  reprise.addEventListener('click', function(e){
    if (e.target.closest('button')) setTimeout(function(){
      if (document.getElementById('productPage').classList.contains('active')) texteOffreDirecte();
    }, 0);
  });
})();

/* ============ APERÇU DU CERTIFICAT (ajout v3) ============
   Remplace « Ton nom ici » par le prénom saisi et la mention de date par la date de fin
   calculée au bilan. Ne lit que des données déjà présentes dans la page, n'envoie rien. */
function remplirCertificat(){
  var nom = (typeof state !== 'undefined' && state.name) ? state.name : '';
  if (!nom) { try { nom = JSON.parse(localStorage.getItem('emk_lead') || '{}').name || ''; } catch(e) {} }
  var elNom = document.getElementById('certNom');
  if (elNom) elNom.textContent = nom ? nom : 'Ton nom ici';
  var fin = document.getElementById('sumDate');
  var date = fin ? fin.textContent.trim() : '';
  var elDate = document.getElementById('certDate');
  if (elDate && date && date !== '—') elDate.textContent = 'Délivré le ' + date;
  if (typeof scaleCert === 'function') requestAnimationFrame(scaleCert);
}
(function(){
  var page = document.getElementById('productPage');
  if (!page || !('MutationObserver' in window)) return;
  new MutationObserver(function(){ if (page.classList.contains('active')) remplirCertificat(); })
    .observe(page, {attributes: true, attributeFilter: ['class']});
})();
