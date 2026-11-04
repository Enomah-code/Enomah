/* ============ Ajout v3.2 : accueil sans second prénom ============
   Le prénom figure déjà dans le titre « Félicitations David… ». Le paragraphe d'accueil,
   réécrit par le script d'origine avec le prénom, redevient neutre. Texte affiché seulement. */
(function(){
  var l = document.getElementById('lede');
  if (l) l.innerHTML = 'Bienvenue. Ton accès est prêt. Tu fais maintenant partie des <strong>AI Business Builders</strong>.';
})();
