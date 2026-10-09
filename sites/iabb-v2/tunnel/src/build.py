"""Construit la copie restylée du tunnel IABB (piste A) à partir des pages en ligne.

Lecture seule de la source. Le JavaScript existant n'est JAMAIS réécrit : chaque bloc
<script> de l'original est recopié octet pour octet (vérifié à la fin). Seuls changent :
le CSS, le HTML de présentation (icônes, logo, accueil à deux chemins, logos de paiement,
garantie expliquée), et un petit script AJOUTÉ pour le raccourci « voir l'offre ».

Usage : python3 build.py <dossier_source> <dossier_sortie> <dossier_icones_lucide>
"""
import re, sys, pathlib, shutil

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])
ICONES = pathlib.Path(sys.argv[3])
ICI = pathlib.Path(__file__).resolve().parent

FONTS_OLD = '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Caveat:wght@500;700&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&display=swap" rel="stylesheet">'
FONTS_URL = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=Plus+Jakarta+Sans:ital,wght@0,500;0,700;0,800;1,700&display=swap'
# Chargement non bloquant (la page s'affiche avec la police système, puis bascule)
FONTS_NEW = (f'<link rel="preload" as="style" href="{FONTS_URL}">\n'
             f'<link rel="stylesheet" href="{FONTS_URL}" media="print" onload="this.media=\'all\'">\n'
             f'<noscript><link rel="stylesheet" href="{FONTS_URL}"></noscript>')

# ---------- icônes (Lucide, licence ISC) ----------
EMOJI_ICONE = {
    # options du quiz
    '💼': 'briefcase', '🚀': 'rocket', '💻': 'laptop', '🎓': 'graduation-cap', '🌱': 'sprout',
    '💪': 'biceps-flexed', '🎯': 'target', '🌟': 'star', '😮‍💨': 'clock', '💸': 'wallet',
    '😰': 'trending-down', '🧱': 'lightbulb', '🔁': 'repeat', '🤷': 'circle-help', '👂': 'ear',
    '🧪': 'flask-conical', '🧠': 'brain', '🤖': 'bot', '⚡': 'zap', '🛒': 'shopping-bag',
    '🌐': 'globe', '💰': 'coins', '🙅': 'circle-x', '👀': 'eye', '🤏': 'puzzle',
    '👨‍💻': 'terminal', '🆕': 'sparkles', '📺': 'circle-play', '😞': 'circle-pause',
    '💳': 'credit-card', '☕': 'coffee', '🌆': 'sunset', '🔥': 'flame', '🧭': 'compass',
    '⏳': 'hourglass', '😵‍💫': 'puzzle', '💭': 'heart', '📣': 'megaphone', '🤝': 'handshake',
    '🌴': 'tree-palm', '📈': 'trending-up',
    # résultat
    '📍': 'map-pin', '⏰': 'clock', '🏆': 'trophy',
    # bénéfices
    '🛡️': 'shield-check', '💬': 'message-circle', '🔄': 'refresh-cw', '📱': 'smartphone',
    # modules et leçons
    '⚙️': 'settings', '🎨': 'palette', '🗄️': 'database', '🎁': 'gift',
    '🎬': 'circle-play', '📝': 'notebook-pen',
    # bonus
    '✅': 'list-checks', '📄': 'file-text',
    # comparaison
    '😔': 'frown', '😎': 'badge-check',
    # accueil
    '✨': 'sparkles',
    # carte prix
    '📚': 'book-open',
}
BONUS_ICONE = {'📝': 'wand-sparkles'}  # dans la carte bonus, 📝 = les prompts


def sprite(noms):
    out = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">']
    for n in sorted(noms):
        txt = (ICONES / f'{n}.svg').read_text()
        inner = re.search(r'<svg[^>]*>(.*)</svg>', txt, re.S).group(1)
        inner = re.sub(r'\s+', ' ', inner).replace(' />', '/>').strip()
        out.append(f'<symbol id="i-{n}" viewBox="0 0 24 24">{inner}</symbol>')
    out.append('</svg>')
    return '\n'.join(out)


def ic(nom, utilises):
    utilises.add(nom)
    return f'<svg class="i" aria-hidden="true"><use href="#i-{nom}"/></svg>'


# ---------- découpage : on ne touche jamais au contenu des <script> ----------
def decouper(html):
    parts, pos = [], 0
    for m in re.finditer(r'<script\b[^>]*>.*?</script>', html, re.S):
        parts.append(('html', html[pos:m.start()]))
        parts.append(('js', m.group(0)))
        pos = m.end()
    parts.append(('html', html[pos:]))
    return parts


def remplacer(s, ancien, nouveau, n=1):
    c = s.count(ancien)
    assert c == n, f'attendu {n} occurrence(s), trouvé {c} : {ancien[:90]!r}'
    return s.replace(ancien, nouveau)


# ---------- typographie française, dans le texte visible uniquement ----------
NBSP, NNBSP = ' ', ' '


def typo_texte(t):
    t = t.replace("'", '’')
    t = re.sub(r' ([?!;»])', NNBSP + r'\1', t)
    t = re.sub(r' :', NBSP + ':', t)
    t = re.sub(r'« ', '«' + NNBSP, t)
    return t


def typo(html):
    """Applique typo_texte aux nœuds texte, hors balises, <style>, <title> et attributs."""
    morceaux = re.split(r'(<style\b.*?</style>|<title>.*?</title>|<[^>]+>)', html, flags=re.S)
    return ''.join(m if (m.startswith('<') or not m) else typo_texte(m) for m in morceaux)


def css_bloc(nom):
    return (ICI / nom).read_text()


# =====================================================================
#  index.html
# =====================================================================
def construire_index():
    src = (SRC / 'index.html').read_text(encoding='utf-8')
    utilises = set()
    parts = decouper(src)
    js_orig = [p for k, p in parts if k == 'js']
    out = []
    for k, p in parts:
        if k == 'js':
            out.append(p)
            continue
        h = p
        # 1. polices + feuille de style principale
        if FONTS_OLD in h:
            h = remplacer(h, FONTS_OLD, FONTS_NEW)
            h = re.sub(r'<style>\n  :root\{.*?</style>', lambda m: '<style>\n' + css_bloc('tunnel.css') + '</style>', h, count=1, flags=re.S)
            assert 'var(--fond)' in h
        if '.emk-notif-widget{' in h:
            # notifications de ventes : mêmes règles, couleurs de la piste A
            h = remplacer(h, "font-family:'Manrope',-apple-system,BlinkMacSystemFont,sans-serif;", "font-family:var(--sans);")
            h = remplacer(h, "color:#0F172A;\n  max-width:340px", "color:#0C1446;\n  max-width:340px")
            h = remplacer(h, "text-transform:uppercase;color:#D97706;", "text-transform:none;letter-spacing:0;color:#3A47D5;")
            h = remplacer(h, "font-size:11.5px;font-weight:800;letter-spacing:0.08em;", "font-size:12.5px;font-weight:700;letter-spacing:0;")
            h = remplacer(h, "font-weight:800;color:#0F172A;font-size:14.5px;", "font-weight:800;color:#0C1446;font-size:14.5px;")
            h = remplacer(h, "font-size:12.5px;color:#64748B;font-weight:500;", "font-size:13px;color:#4A5178;font-weight:500;")
            h = remplacer(h, "border:1px solid rgba(15,23,42,0.08);", "border:1px solid #E4E8FC;")
            h = remplacer(h, "  background:#059669;color:#fff;", "  background:#1E7A4C;color:#fff;")
        h = construire_html_index(h, utilises)
        out.append(h)
    html = ''.join(out)

    # 2. sprite d'icônes juste après <body>
    html = remplacer(html, '<body>\n', '<body>\n' + sprite(utilises) + '\n')

    # 3. script AJOUTÉ (raccourci de l'accueil), juste avant </body>
    raccourci = (ICI / 'raccourci.js').read_text()
    html = remplacer(html, '\n</body>', '\n<script>\n' + raccourci + '</script>\n\n</body>')

    manquants = [a for a in REMPL_TOUS if a not in APPLIQUES]
    assert not manquants, f'remplacements non appliqués : {manquants}'
    # 4. contrôle : chaque <script> d'origine est présent, intact, dans le même ordre
    js_new = [p for k, p in decouper(html) if k == 'js']
    assert js_new[:len(js_orig)] == js_orig, 'un script original a changé'
    assert len(js_new) == len(js_orig) + 1
    return html


APPLIQUES = set()
REMPL_TOUS = []


def construire_html_index(h, U):
    R = remplacer
    logo_a = '<a href="/" class="logo"><span class="logo-emk">EMK</span><span class="logo-diamond">Blue Diamond</span></a>'
    logo_div = '<div class="logo"><span class="logo-emk">EMK</span><span class="logo-diamond">Blue Diamond</span></div>'
    img = '<img src="assets/logo-emk.webp" alt="EMK Blue Diamond" width="561" height="66">'
    h = h.replace(logo_a, f'<a href="/" class="logo">{img}</a>')
    img_lazy = img[:-1] + ' loading="lazy">'
    h = h.replace(logo_div, f'<div class="logo">{img_lazy}</div>')

    # ---- accueil : deux chemins (bilan = principal, offre directe = secondaire) ----
    if '<div id="welcomeScreen">' in h:
        ancien = re.search(r'  <div class="welcome-content">.*?\n  </div>\n</div>', h, re.S).group(0)
        nouveau = f'''  <div class="welcome-content">
    <div class="welcome-text">
      <div class="welcome-icon" aria-hidden="true">{ic('sparkles', U)}</div>
      <h1 class="welcome-title">3 minutes pour <em>te connaître</em></h1>
      <p class="welcome-sub">Et concevoir un programme sur mesure adapté à ton profil.</p>
      <div class="welcome-paths">
        <button class="welcome-btn" onclick="startQuizFromWelcome()">Faire mon bilan sur mesure {ic('arrow-right', U)}</button>
        <div class="welcome-footnote">Aucune bonne ou mauvaise réponse — juste toi.</div>
        <div class="welcome-or">ou</div>
        <button type="button" class="welcome-shortcut" onclick="voirOffreDirectement()">Je connais déjà la formation : voir l'offre directement {ic('arrow-right', U)}</button>
      </div>
    </div>
    <figure class="welcome-scene">
      <div class="chat" role="img" aria-label="Exemple de conversation avec un agent WhatsApp">
        <div class="bar"><span class="av">IA</span><span><b>Ta Boutique</b><i>Agent IA · en ligne</i></span></div>
        <div class="msgs">
          <p class="m in">Bonsoir, la robe bleue est encore dispo ?</p>
          <p class="m out">Oui ! Il reste du M et du L. Je te la réserve ?</p>
        </div>
      </div>
      <span class="badge24">24h/24</span>
      <img class="enock" src="assets/enock.webp" alt="Enock Mahougnan, bras croisés, en costume bleu nuit" width="524" height="720" decoding="async">
      <figcaption><b>Enock Mahougnan</b><span>Ton formateur</span></figcaption>
    </figure>
  </div>
</div>'''
        h = R(h, ancien, nouveau)

    # ---- icônes : spans d'emoji -> SVG ----
    def sub_span(classe, table=EMOJI_ICONE):
        nonlocal h
        def f(m):
            e = m.group(2)
            assert e in table, f'emoji sans icône : {e!r} ({classe})'
            return f'{m.group(1)}{ic(table[e], U)}</span>'
        h = re.sub(r'(<span class="' + re.escape(classe) + r'">)([^<]+)</span>', f, h)

    def sub_div(classe, table=EMOJI_ICONE):
        nonlocal h
        def f(m):
            e = m.group(2)
            assert e in table, f'emoji sans icône : {e!r} ({classe})'
            return f'{m.group(1)}{ic(table[e], U)}</div>'
        h = re.sub(r'(<div class="' + re.escape(classe) + r'"[^>]*>)([^<]+)</div>', f, h)

    for c in ['option-emoji', 'module-icon', 'lesson-icon icon-video', 'lesson-icon icon-eval']:
        sub_span(c)
    for c in ['result-summary-emoji', 'outcome-emoji', 'compare-avatar', 'guarantee-emoji']:
        sub_div(c)
    sub_div('bonus-emoji', {**EMOJI_ICONE, **BONUS_ICONE})

    if 'class="price-includes"' in h:
        def f(m):
            return f'<div class="item">{ic(EMOJI_ICONE[m.group(1)], U)}<span>'
        h = re.sub(r'<div class="item"><span>([^<]+)</span><span>', f, h)
        # la liste de la carte prix : une coche pour chaque ligne, plus lisible
        h = re.sub(r'<div class="item"><svg class="i" aria-hidden="true"><use href="#i-[a-z-]+"/></svg>',
                   lambda m: f'<div class="item">{ic("check", U)}', h)

    # ---- petits libellés : l'emoji de tête devient une icône, le texte ne change pas ----
    rempl = [
        ('<span class="unlock-pill">🎁 Débloqué</span>', f'<span class="unlock-pill">{ic("gift", U)}Débloqué</span>'),
        ('onclick="switchProfile(\'salarie\')">💼 Salarié</button>', f'onclick="switchProfile(\'salarie\')">{ic("briefcase", U)}Salarié</button>'),
        ('onclick="switchProfile(\'freelance\')">💻 Freelance</button>', f'onclick="switchProfile(\'freelance\')">{ic("laptop", U)}Freelance</button>'),
        ('onclick="switchProfile(\'entrepreneur\')">🚀 Entrepreneur</button>', f'onclick="switchProfile(\'entrepreneur\')">{ic("rocket", U)}Entrepreneur</button>'),
        ('<div class="bonus-flash"><span>🎁 5 bonus débloqués par ton bilan</span></div>', f'<div class="bonus-flash">{ic("gift", U)}<span>5 bonus débloqués par ton bilan</span></div>'),
        ('<div class="section-kicker">💬 Ils l\'ont déjà fait</div>', f'<div class="section-kicker">{ic("message-circle", U)}Ils l\'ont déjà fait</div>'),
        ('<div class="price-differentiator">🔒 Un seul paiement', f'<div class="price-differentiator">{ic("lock", U)}Un seul paiement'),
        ('<div class="price-unlock-tag">🎁 Offre débloquée par ton bilan</div>', f'<div class="price-unlock-tag">{ic("gift", U)}Offre débloquée par ton bilan</div>'),
        ('<div class="price-forever">🎉 Tarif de lancement', f'<div class="price-forever">{ic("sparkles", U)}Tarif de lancement'),
        ('<b>✨ Ce n\'est pas un abonnement.</b>', '<b>Ce n\'est pas un abonnement.</b>'),
        ('<p style="text-align:center;margin-top:24px;font-size:13px;color:var(--muted)">📩 Si l\'email', f'<p class="note-centre">{ic("mail", U)}<span>Si l\'email'),
        ('vérifie tes spams ou écris-nous.</p>', 'vérifie tes spams ou écris-nous.</span></p>'),
        ('placeholder="✉️  ton@email.com"', 'placeholder="ton@email.com"'),
        ('<p style="font-size:12.5px;color:var(--muted);margin-top:14px;line-height:1.55;font-weight:500">🔒 Zéro spam', f'<p class="note-discrete">{ic("lock", U)}<span>Zéro spam'),
        ('Tu peux te désinscrire en un clic.</p>', 'Tu peux te désinscrire en un clic.</span></p>'),
        ('dans la section juste en dessous 👇</p>', 'dans la section juste en dessous.</p>'),
        ('title="WhatsApp" aria-label="Contacter par WhatsApp">💬</a>', f'title="WhatsApp" aria-label="Contacter par WhatsApp">{ic("message-circle", U)}</a>'),
        ('title="Email" aria-label="Contacter par email">✉️</a>', f'title="Email" aria-label="Contacter par email">{ic("mail", U)}</a>'),
        ('<span class="emk-notif-title">Nouvelle inscription 🎉</span>', '<span class="emk-notif-title">Nouvelle inscription</span>'),
        ('<div class="section-eyebrow">◆ ', '<div class="section-eyebrow">'),
        ('>Découvrir mon plan →</button>', f'>Découvrir mon plan {ic("arrow-right", U)}</button>'),
        ('onclick="revealProduct()">Voir mon programme →</button>', f'onclick="revealProduct()">Voir mon programme {ic("arrow-right", U)}</button>'),
        ('class="product-nav-cta">Voir mon offre →</a>', 'class="product-nav-cta">Voir mon offre</a>'),
        ('style="max-width:360px;margin:0 auto">Je décroche ma certification →</a>', f'style="max-width:380px;margin:0 auto">Je décroche ma certification {ic("arrow-right", U)}</a>'),
    ]
    if not REMPL_TOUS:
        REMPL_TOUS.extend(a for a, _ in rempl)
    for a, b in rempl:
        if a in h:
            APPLIQUES.add(a)
            h = h.replace(a, b)
    # moyens de paiement : texte sans emoji + logos officiels sous le bouton d'achat
    a = '<div class="price-payment">💳 Carte bancaire &nbsp;·&nbsp; 📱 Mobile Money &nbsp;·&nbsp; 100% sécurisé</div>'
    if a in h:
        logos = ('<ul class="moyens" aria-label="Moyens de paiement acceptés">'
                 '<li><img src="assets/paiement/mtn-momo.webp" alt="MTN MoMo" width="24" height="24" loading="lazy" decoding="async"></li>'
                 '<li><img src="assets/paiement/moov-money.webp" alt="Moov Money" width="27" height="24" loading="lazy" decoding="async"></li>'
                 '<li><img src="assets/paiement/orange-money.svg" alt="Orange Money" width="67" height="18" loading="lazy" decoding="async"></li>'
                 '<li><img src="assets/paiement/wave.webp" alt="Wave" width="55" height="24" loading="lazy" decoding="async"></li>'
                 '<li><img src="assets/paiement/visa.svg" alt="Visa" width="55" height="18" loading="lazy" decoding="async"></li>'
                 '<li><img src="assets/paiement/mastercard.svg" alt="Mastercard" width="36" height="22" loading="lazy" decoding="async"></li></ul>')
        h = R(h, a, logos + f'\n        <div class="price-payment">{ic("lock", U)}<span>Carte bancaire &nbsp;·&nbsp; Mobile Money &nbsp;·&nbsp; 100% sécurisé</span></div>')
    # garantie expliquée simplement, juste sous la carte prix (faits tirés des CGV, article 5)
    a = '      <div class="price-nono">'
    if a in h:
        g = f'''      <div class="garantie-simple">
        <div class="gs-tete"><span class="gs-ic">{ic("shield-check", U)}</span><h3>La garantie 7 jours, simplement</h3></div>
        <ol>
          <li><span><b>Tu as 7 jours pour essayer,</b> comptés à partir du jour de ton achat.</span></li>
          <li><span><b>Ça ne te convient pas ?</b> Écris à <a href="mailto:contact@emkbluediamond.online?subject=Demande%20de%20remboursement">contact@emkbluediamond.online</a> avec pour objet « Demande de remboursement » et l'email utilisé pour l'achat.</span></li>
          <li><span><b>Tu es remboursé en entier,</b> sans avoir à te justifier, sous 3 à 5 jours ouvrables, sur le moyen de paiement que tu as utilisé.</span></li>
        </ol>
      </div>

'''
        h = R(h, a, g + a)
    # le bouton de l'écran prénom et les boutons « continuer » reçoivent une flèche
    for lib in ['Je continue', 'Continuer', 'Montre-moi ça', 'Je veux être du bon côté']:
        h = h.replace(f'<button class="continue-btn" onclick="next()">{lib}</button>',
                      f'<button class="continue-btn" onclick="next()">{lib} {ic("arrow-right", U)}</button>')
    return typo(h)


# =====================================================================
#  merci.html
# =====================================================================
def construire_merci():
    src = (SRC / 'merci.html').read_text(encoding='utf-8')
    utilises = set()
    parts = decouper(src)
    js_orig = [p for k, p in parts if k == 'js']
    out = []
    for k, p in parts:
        if k == 'js':
            out.append(p)
            continue
        h = p
        if FONTS_OLD in h:
            h = remplacer(h, FONTS_OLD, FONTS_NEW)
        if '<style>' in h:
            h = re.sub(r'<style>.*?</style>', lambda m: '<style>\n' + css_bloc('merci.css') + '</style>', h, count=1, flags=re.S)
        h = re.sub(r'<a href="/" class="logo">\s*<span class="logo-emk">EMK</span>\s*<span class="logo-diamond">Blue Diamond</span>\s*</a>',
                   '<a href="/" class="logo"><img src="assets/logo-emk.webp" alt="EMK Blue Diamond" width="561" height="66"></a>', h)
        h = re.sub(r'<div class="logo">\s*<span class="logo-emk">EMK</span>\s*<span class="logo-diamond">Blue Diamond</span>\s*</div>',
                   '<div class="logo"><img src="assets/logo-emk.webp" alt="EMK Blue Diamond" width="561" height="66" loading="lazy"></div>', h)
        h = h.replace('<div class="kicker">✨ Paiement confirmé</div>', f'<div class="kicker">{ic("badge-check", utilises)}Paiement confirmé</div>')
        h = h.replace('<a href="https://portal.chariow.com/login" class="portal-cta">\n      🚀 Accéder à mon espace apprenant\n    </a>',
                      f'<a href="https://portal.chariow.com/login" class="portal-cta">\n      Accéder à mon espace apprenant {ic("arrow-right", utilises)}\n    </a>')
        h = h.replace('<div class="reassure-icon">💬</div>', f'<div class="reassure-icon">{ic("message-circle", utilises)}</div>')
        out.append(typo(h))
    html = ''.join(out)
    html = remplacer(html, '<body>\n', '<body>\n' + sprite(utilises) + '\n')
    js_new = [p for k, p in decouper(html) if k == 'js']
    assert js_new == js_orig, 'un script original de merci.html a changé'
    for e in ['✨', '🚀', '💬']:
        assert e not in re.sub(r'<script\b.*?</script>', '', html, flags=re.S), e
    return html


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'index.html').write_text(construire_index(), encoding='utf-8')
    (OUT / 'merci.html').write_text(construire_merci(), encoding='utf-8')
    a = OUT / 'assets'
    (a / 'paiement').mkdir(parents=True, exist_ok=True)
    marque = pathlib.Path('/home/user/Enomah/sites/iabb-v2/branding/assets')
    for f in ['logo-emk.webp', 'enock.webp']:
        shutil.copy(marque / f, a / f)
    for f in pathlib.Path('/home/user/Enomah/sites/livensya/images/paiement').iterdir():
        shutil.copy(f, a / 'paiement' / f.name)
    print('ok')
