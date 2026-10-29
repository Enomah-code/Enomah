import json, pathlib
from playwright.sync_api import sync_playwright
ORIG=pathlib.Path("/home/user/emk-chariow/iabb/pages/quizcertification/index.html")
NEW=pathlib.Path("/home/user/Enomah/sites/iabb-origine-bouton/index.html")
OUT=pathlib.Path(__file__).parent
HOTE="https://quizcertification.emkbluediamond.online/"
FAUX_FBQ="""window.__fbq=[];!function(){var n=function(){window.__fbq.push(JSON.parse(JSON.stringify([].slice.call(arguments))));};
n.queue=[];n.loaded=true;n.version='2.0';n.push=n;var old=window.fbq;if(old&&old.queue){old.queue.forEach(function(a){n.apply(null,a);});}
window.fbq=n;window._fbq=n;}();"""
CHROME="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
ok=True
def verif(c,m):
    global ok; print(("  OK    " if c else "  ECHEC ")+m); ok=ok and c
def session(fichier, etapes, largeur=390, prefixe=None):
    execs=[]; err=[]; out={}
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=CHROME); ctx=b.new_context(viewport={"width":largeur,"height":844}); pg=ctx.new_page()
        pg.on("pageerror",lambda e:err.append(str(e)))
        def r(route):
            u=route.request.url
            if u.startswith(HOTE): return route.fulfill(status=200,body=fichier.read_bytes(),content_type="text/html; charset=utf-8")
            if "connect.facebook.net" in u: return route.fulfill(status=200,body=FAUX_FBQ,content_type="application/javascript")
            if "ipify" in u: return route.fulfill(status=200,body='{"ip":"2c0f:f0f8:1:2::3"}',content_type="application/json")
            if "script.google.com" in u:
                if route.request.post_data: execs.append(json.loads(route.request.post_data))
                return route.fulfill(status=200,body='{"status":"ok","sales":[]}',content_type="application/json")
            if "fonts.g" in u: return route.continue_()
            return route.abort()
        ctx.route("**/*",r)
        pg.goto(HOTE,wait_until="load"); pg.wait_for_timeout(1200)
        for e in etapes:
            if isinstance(e,tuple): out[e[0]]=pg.evaluate(e[1])
            elif e.startswith("WAIT"): pg.wait_for_timeout(int(e[4:]))
            elif e.startswith("SHOT"): pg.screenshot(path=str(OUT/f"{prefixe}-{e[4:]}-{largeur}.png"))
            elif e.startswith("TYPE "): sel,txt=e[5:].split("|"); pg.fill(sel,txt); pg.dispatch_event(sel,"input")
            elif e.startswith("CLICK "): pg.click(e[6:])
            else: pg.evaluate(e)
        out["fbq"]=pg.evaluate("window.__fbq||[]"); out["execs"]=execs; out["err"]=err
        out["largeur"]=pg.evaluate("document.documentElement.scrollWidth")
        b.close(); return out
ev=lambda r:[(a[0],a[1]) for a in r["fbq"]]
VIS="!document.getElementById('passerWrap').hidden && getComputedStyle(document.getElementById('passerWrap')).display!=='none'"
DEBUT=["SHOTaccueil","CLICK #welcomeScreen .welcome-btn","WAIT400",("passer_q1",VIS),"SHOTprenom","TYPE #nameInput|David","CLICK #nameBtn","WAIT500",("passer_q2",VIS),"SHOTq2"]

print("== chargement et accueil : identiques à l'original")
a=session(ORIG,[]); b=session(NEW,[])
verif(ev(a)==ev(b) and not a["err"] and not b["err"],f"mêmes appels Pixel, aucune erreur : {ev(b)}")
verif(b["largeur"]==390,"pas de débordement")

print("== lien « Passer »")
for L in (360,390):
    s=session(NEW,DEBUT+["CLICK .passer-lien","WAIT400",("titre","document.getElementById('emailTitle').textContent"),("sous","document.querySelector('[data-screen=q12] .question-sub').textContent"),"SHOTemail","TYPE #emailInput|test-local@example.com","CLICK #emailBtn","WAIT1500",
        ("offre","document.getElementById('productPage').classList.contains('active')"),("unlock","document.getElementById('unlockText').textContent"),"WAIT4500","SHOToffre-apres-confettis"],largeur=L,prefixe="passer")
    verif(not s["passer_q1"] and s["passer_q2"],f"{L}px : caché sur l'écran du prénom, visible à la question suivante")
    verif(s["titre"]=="Où on t'envoie ton offre de lancement ?" and s["offre"],f"{L}px : écran email puis offre ({s['unlock']})")
    verif(not s["err"] and s["largeur"]<=L,f"{L}px : aucune erreur JS, pas de débordement {s['err']}")
n=[x[1] for x in s["fbq"]]
verif(n.count("Lead")==1 and "QuizComplete" not in n and "OfferReveal" in n,f"un Lead (avec eventID), OfferReveal, pas de QuizComplete : {ev(s)}")
lead=[x for x in s["fbq"] if x[1]=="Lead"][0]
verif(len(lead)>3 and lead[3].get("eventID"),f"eventID du Lead présent : {lead[3] if len(lead)>3 else None}")
leads=[x for x in s["execs"] if x.get("email")]
verif(len(leads)==1 and leads[0]["prenom"]=="David" and leads[0]["email"]=="test-local@example.com",f"lead envoyé au Sheet avec prénom et email ({len(leads)})")

print("== retour arrière depuis l'écran email du « Passer »")
r=session(NEW,DEBUT+["CLICK .passer-lien","WAIT300","CLICK #backBtn","WAIT400",("ecran","document.querySelector('.screen.active').dataset.screen"),(
 "btn","document.getElementById('emailBtn').getAttribute('onclick')"),("vis",VIS),("sous","document.querySelector('[data-screen=q12] .question-sub').textContent")])
verif(r["ecran"]=="q2" and r["btn"]=="startAnalysis()" and r["vis"],f"retour à la question, quiz normal rétabli ({r['ecran']}, {r['btn']})")

print("== quiz complet normal : Lead et données identiques à l'original")
FIN=["state.name='David';state.a.email='test-local@example.com';state.a.pain='temps';startAnalysis()","WAIT7500"]
o=session(ORIG,FIN); m=session(NEW,FIN)
verif(ev(o)==ev(m) and not m["err"],f"mêmes événements : {ev(m)}")
lo=[dict(x) for x in o["execs"] if x.get("email")]; lm=[dict(x) for x in m["execs"] if x.get("email")]
for d in lo+lm: d.pop("date",None)
verif(lo==lm and len(lm)==1,"même lead envoyé")
print("\nRÉSULTAT :","TOUT EST OK" if ok else "AU MOINS UN ÉCHEC")
print("sous-titre en mode Passer :", s.get("sous")); print("sous-titre rétabli :", r.get("sous"))
