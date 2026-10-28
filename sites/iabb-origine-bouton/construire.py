"""Page IABB d'ORIGINE (sauvegarde du 9 octobre 2026), à l'identique, avec seulement :
1. le bouton « Voir directement l'offre de lancement » sur l'accueil (demande d'Enock) ;
2. le retrait du bandeau « Bon retour » qui restait figé en haut pendant le quiz et sur l'offre.
Aucun texte, aucune couleur, aucune icône, aucune police d'origine ne change. Aucun événement Meta ajouté.
Usage : python3 construire.py <index_origine.html> <sortie.html>"""
import sys, pathlib
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
t = src.read_text(encoding="utf-8")

def remplacer(ancien, nouveau):
    global t
    assert t.count(ancien) == 1, ancien
    t = t.replace(ancien, nouveau)

# 1. Le bouton, juste sous la phrase « Aucune bonne ou mauvaise réponse »
remplacer('<div class="welcome-footnote">Aucune bonne ou mauvaise réponse — juste toi.</div>\n',
 '<div class="welcome-footnote">Aucune bonne ou mauvaise réponse — juste toi.</div>\n'
 '    <div class="welcome-ou"><span>ou</span></div>\n'
 '    <button type="button" class="welcome-btn-offre" onclick="voirOffreDirectement()">Voir directement l\'offre de lancement 🎁</button>\n'
 '    <div class="welcome-footnote">Tu connais déjà la formation ? Le tarif de lancement t\'attend.</div>\n')

# Style du bouton : mêmes couleurs que la page (variables d'origine), en contour pour rester secondaire
remplacer('  .welcome-footnote{margin-top:24px;font-size:13px;color:var(--muted);font-weight:500}\n',
 '  .welcome-footnote{margin-top:24px;font-size:13px;color:var(--muted);font-weight:500}\n'
 '  .welcome-ou{display:flex;align-items:center;gap:12px;width:100%;max-width:340px;margin:22px auto 18px;color:var(--muted);font-size:13px;font-weight:600}\n'
 '  .welcome-ou::before,.welcome-ou::after{content:"";flex:1;height:1px;background:rgba(100,116,139,.25)}\n'
 '  .welcome-btn-offre{background:transparent;color:var(--amber-dark);border:2px solid var(--amber);padding:15px 30px;border-radius:100px;font-size:16px;font-weight:800;font-family:inherit;cursor:pointer;transition:all .2s;max-width:100%}\n'
 '  .welcome-btn-offre:hover{background:var(--amber);color:#fff;transform:translateY(-2px)}\n'
 '  .welcome-btn-offre + .welcome-footnote{margin-top:12px}\n')

# 2. Le script ajouté, juste avant </body>
SCRIPT = r'''
<script>
/* ===== Ajout : « Voir directement l'offre de lancement » =====
   N'envoie AUCUN événement de plus : il appelle revealProduct(), la fonction existante qui affiche l'offre
   (OfferReveal, PricingView et InitiateCheckout partent comme d'habitude, aucun Lead puisqu'il n'y a pas de quiz).
   Il remplace seulement les deux phrases qui contiennent le prénom, puisque ce visiteur ne l'a pas donné. */
function retirerReprise(){ var b=document.getElementById('resumeBanner'); if(b) b.remove(); }
function voirOffreDirectement(){
  retirerReprise();
  document.getElementById('welcomeScreen').style.display='none';
  revealProduct();
  document.getElementById('heroName').textContent='🎯 Le programme complet';
  document.getElementById('unlockText').textContent='Ton offre de lancement est activée';
}
/* ===== Correctif : le bandeau « Bon retour » restait figé en haut de l'écran
   pendant tout le quiz puis sur l'offre, si le visiteur ne cliquait sur aucun de ses deux boutons. ===== */
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
