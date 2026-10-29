/* ============ RACCOURCI DE L'ACCUEIL (ajout, piste A) ============
   « Je connais déjà la formation : voir l'offre directement ».
   Ce script n'envoie AUCUN événement lui-même et ne touche à aucune donnée :
   il ferme l'écran d'accueil puis appelle revealProduct(), la fonction existante
   qui affiche l'offre. Comme pour le parcours normal, c'est revealProduct() qui
   envoie OfferReveal, prépare PricingView (quand la carte prix devient visible)
   et InitiateCheckout (clic sur le widget Chariow). Aucun Lead, aucun envoi /exec. */
function voirOffreDirectement(){
  var bandeau = document.getElementById('resumeBanner');
  if (bandeau) bandeau.remove();
  document.getElementById('welcomeScreen').style.display = 'none';
  revealProduct();
}
