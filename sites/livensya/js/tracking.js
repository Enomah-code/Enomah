/* Livensya · suivi Meta (Pixel standard uniquement)
   ------------------------------------------------------------------
   1. L'identifiant du Pixel Meta de Livensya est renseigné ci-dessous (PIXEL_ID).
   2. Tant que PIXEL_ID est vide, RIEN n'est chargé (aucun script Meta, aucun cookie).
   3. Aucun jeton de l'API Conversions ici : un site statique est public,
      le jeton doit rester sur un serveur (voir LISEZMOI.md).
   On ne touche pas aux « événements automatiques » de Meta : réglage par défaut.

   Événements envoyés, chacun avec un eventID unique (prêt pour la déduplication
   future avec l'API Conversions : même nom d'événement + même event_id) :
   - PageView         : toutes les pages
   - ViewContent      : quand la section de l'offre s'affiche (une fois par page vue)
   - Lead             : fin du test, une seule fois par visiteur (drapeau localStorage)
   - InitiateCheckout : clic sur un bouton d'achat, une fois par clic (anti double-clic)
   - Purchase         : PAS côté navigateur (voir merci.html et LISEZMOI.md)
*/
(function () {
  'use strict';

  var PIXEL_ID = '5010730402487338'; // Pixel Meta de Livensya (laisser vide '' pour tout couper)

  function nouvelId(nom) {
    var alea = (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
      : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
    return nom + '.' + alea;
  }

  var actif = /^\d{6,20}$/.test(PIXEL_ID);

  if (actif) {
    /* Code de base officiel du Pixel Meta */
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
    document,'script','https://connect.facebook.net/en_US/fbevents.js');
    window.fbq('init', PIXEL_ID);
  }

  /* suivre('Lead', {…}) : renvoie l'eventID utilisé (utile pour le relier plus tard au serveur). */
  function suivre(nom, params) {
    var eventID = nouvelId(nom);
    if (actif && typeof window.fbq === 'function') {
      window.fbq('track', nom, params || {}, { eventID: eventID });
    } else if (/[?&]apercu=1/.test(location.search)) {
      console.info('[suivi désactivé] ' + nom, params || {}, eventID);
    }
    return eventID;
  }

  window.lvSuivi = {
    actif: actif,
    suivre: suivre,

    /* Lead : une seule fois par visiteur */
    lead: function (params) {
      try { if (localStorage.getItem('lv_lead_envoye')) return null; } catch (e) {}
      var id = suivre('Lead', params);
      try { localStorage.setItem('lv_lead_envoye', id); } catch (e) {}
      return id;
    },

    /* InitiateCheckout : une fois par clic, clics répétés en moins de 2 s ignorés */
    _dernierClic: 0,
    initiateCheckout: function (params) {
      var maintenant = Date.now();
      if (maintenant - this._dernierClic < 2000) return null;
      this._dernierClic = maintenant;
      var id = suivre('InitiateCheckout', params);
      /* Gardé pour un futur envoi serveur du Purchase avec le même identifiant de parcours */
      try { localStorage.setItem('lv_initiate_checkout_id', id); } catch (e) {}
      return id;
    }
  };

  suivre('PageView');
})();
