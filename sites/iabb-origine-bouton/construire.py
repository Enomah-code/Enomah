"""Page IABB d'ORIGINE (sauvegarde du 9 octobre 2026), à l'identique, avec seulement :
1. un lien discret « Passer » à partir de la question qui suit le prénom (demande d'Enock) :
   il mène à l'écran email existant, puis directement à la page d'offre ;
   le prénom et l'email sont donc toujours récupérés (lead enregistré comme dans le quiz) ;
2. le retrait du bandeau « Bon retour » qui restait figé en haut pendant le quiz et sur l'offre.
L'accueil, les textes, les couleurs, les icônes et les polices d'origine ne changent pas.
Usage : python3 construire.py <index_origine.html> <sortie.html>"""
import sys, pathlib
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
t = src.read_text(encoding="utf-8")

def remplacer(ancien, nouveau):
    global t
    assert t.count(ancien) == 1, ancien
    t = t.replace(ancien, nouveau)

# 1. Le lien « Passer », en haut à droite de la zone des questions (caché sur l'écran du prénom)
remplacer('  <div class="stage">\n',
 '  <div class="stage">\n'
 '    <div class="passer-wrap" id="passerWrap" hidden><button type="button" class="passer-lien" onclick="passerVersOffre()">Passer →</button></div>\n')
remplacer('  .stage{max-width:600px;',
 '  .passer-wrap{text-align:right;margin:-18px 0 6px}\n'
 '  .passer-wrap[hidden]{display:none}\n'
 '  .passer-lien{background:none;border:none;padding:8px 2px;color:var(--muted);font-size:13.5px;font-weight:600;font-family:inherit;cursor:pointer;text-decoration:underline;text-underline-offset:3px}\n'
 '  .passer-lien:hover{color:var(--amber)}\n'
 '  .stage{max-width:600px;')

SCRIPT = r'''
<script>
/* ===== Ajout : lien « Passer » (à partir de la question qui suit le prénom) =====
   Il affiche l'écran email EXISTANT (q12) avec un titre adapté, puis va directement à l'offre.
   Le lead part avec la fonction existante saveLead(), et l'événement Lead exactement comme dans
   startAnalysis() (même eventID déterministe, donc dédupliqué avec l'API Conversions).
   Pas de QuizComplete : la personne n'a pas fini le quiz. */
var _passer = null;
var _showScreenOrigine = showScreen;
showScreen = function(n){
  _showScreenOrigine(n);
  var w = document.getElementById('passerWrap');
  if (w) w.hidden = (_passer !== null) || ['q1','q12','analysis','result'].indexOf(n) !== -1;
};
function passerVersOffre(){
  var sous = document.querySelector('[data-screen="q12"] .question-sub');
  _passer = { idx: idx, titre: document.getElementById('emailTitle').innerHTML, sous: sous.innerHTML };
  sous.textContent = 'Ton offre de lancement s\'affiche juste après.';
  idx = screens.indexOf('q12');
  document.getElementById('emailTitle').textContent = 'Où on t\'envoie ton offre de lancement ?';
  document.getElementById('emailBtn').setAttribute('onclick', 'terminerPasser()');
  document.getElementById('emailBtn').textContent = 'Voir mon offre →';
  showScreen('q12'); updateProgress(); validateEmail();
}
var _goBackOrigine = goBack;
goBack = function(){
  if (_passer && screens[idx] === 'q12') {
    idx = _passer.idx;
    document.getElementById('emailTitle').innerHTML = _passer.titre;
    document.querySelector('[data-screen="q12"] .question-sub').innerHTML = _passer.sous;
    document.getElementById('emailBtn').setAttribute('onclick', 'startAnalysis()');
    document.getElementById('emailBtn').textContent = 'Découvrir mon plan →';
    _passer = null;
    showScreen(screens[idx]); updateProgress(); saveQuizProgress();
    return;
  }
  _goBackOrigine();
};
function terminerPasser(){
  if (!state.a.email) return;
  saveLead();
  generatePixelMatchEventId(state.a.email, 'lead').then(function(eventId){
    trackStd('Lead', {content_name:'IA Business Builder', value:0, currency:'XOF'}, {eventID: eventId});
  }).catch(function(){
    trackStd('Lead', {content_name:'IA Business Builder', value:0, currency:'XOF'});
  });
  revealProduct();
}
/* ===== Correctif : le bandeau « Bon retour » restait figé en haut de l'écran
   pendant tout le quiz puis sur l'offre, si le visiteur ne cliquait sur aucun de ses deux boutons. ===== */
function retirerReprise(){ var b=document.getElementById('resumeBanner'); if(b) b.remove(); }
(function(){
  var bilan=document.querySelector('#welcomeScreen .welcome-btn');
  if(bilan) bilan.addEventListener('click', retirerReprise);
  var page=document.getElementById('productPage');
  if(page && 'MutationObserver' in window) new MutationObserver(function(){ if(page.classList.contains('active')) retirerReprise(); })
    .observe(page,{attributes:true,attributeFilter:['class']});
})();
</script>
'''
assert t.count('</body>') == 1
t = t.replace('</body>', SCRIPT + '</body>')
out.write_text(t, encoding="utf-8")
print("ok", out)
