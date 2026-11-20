"""Construit la v3 du tunnel IABB (couleurs actuelles) à partir des pages en ligne, en lecture seule.

Garanties vérifiées à chaque construction :
  - les scripts autres que le script principal sont recopiés à l'identique ;
  - dans le script principal, SEUL le contenu de chaînes de caractères change (le « squelette »
    du code, chaînes vidées, est identique) et aucune ligne qui touche au tracking ne change ;
  - merci.html : tous les scripts sont identiques.
Usage : python3 build.py <source> <sortie> <icones_lucide>
"""
import re, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import textes

SRC, OUT, ICONES = (pathlib.Path(a) for a in sys.argv[1:4])
ICI = pathlib.Path(__file__).resolve().parent
NBSP, NNBSP = ' ', ' '
FONTS_OLD = '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Caveat:wght@500;700&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&display=swap" rel="stylesheet">'
FONTS_NEW = '<link rel="preload" href="assets/fonts/manrope-latin.woff2" as="font" type="font/woff2" crossorigin>'
PRECONNECT = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
JETONS_TRACKING = ['fbq', 'track', 'content_name', 'ENDPOINT', 'payload', 'eventID', 'eventId', '_fbc', '_fbp', '_clientIp',
                   'ipify', 'emk_lead', 'localStorage', 'fetch(', 'generatePixel', 'saveLead', 'crypto', 'sendBeacon', '_tr.',
                   'API_URL', 'recent-sales', 'prd_', 'chariow', 'Chariow', 'Purchase', 'purchase', 'enrich', 'ENRICH',
                   'flagKey', 'console.', 'initParams', 'envoyerPing', 'pingEnvoye']

EMOJI_ICONE = {
    '💼': 'briefcase', '🚀': 'rocket', '💻': 'laptop', '🎓': 'graduation-cap', '🌱': 'sprout',
    '💪': 'biceps-flexed', '🎯': 'target', '🌟': 'star', '😮‍💨': 'clock', '💸': 'wallet',
    '😰': 'trending-down', '🧱': 'lightbulb', '🔁': 'repeat', '🤷': 'circle-help', '👂': 'ear',
    '🧪': 'flask-conical', '🧠': 'brain', '🤖': 'bot', '⚡': 'zap', '🛒': 'shopping-bag',
    '🌐': 'globe', '💰': 'coins', '🙅': 'circle-x', '👀': 'eye', '🤏': 'puzzle',
    '👨‍💻': 'terminal', '🆕': 'sparkles', '📺': 'circle-play', '😞': 'circle-pause',
    '💳': 'credit-card', '☕': 'coffee', '🌆': 'sunset', '🔥': 'flame', '🧭': 'compass',
    '⏳': 'hourglass', '😵‍💫': 'puzzle', '💭': 'heart', '📣': 'megaphone', '🤝': 'handshake',
    '🌴': 'tree-palm', '📈': 'trending-up', '📍': 'map-pin', '⏰': 'clock', '🏆': 'trophy',
    '🛡️': 'shield-check', '💬': 'message-circle', '🔄': 'refresh-cw', '📱': 'smartphone',
    '⚙️': 'settings', '🎨': 'palette', '🗄️': 'database', '🎁': 'gift', '🎬': 'circle-play', '📝': 'notebook-pen',
    '✅': 'list-checks', '📄': 'file-text', '😔': 'frown', '😎': 'badge-check', '✨': 'sparkles', '📚': 'book-open',
}
BONUS_ICONE = {'📝': 'wand-sparkles'}


def sprite(noms):
    out = ['<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">']
    for n in sorted(noms):
        inner = re.search(r'<svg[^>]*>(.*)</svg>', (ICONES / f'{n}.svg').read_text(), re.S).group(1)
        inner = re.sub(r"\s+", " ", inner).replace(" />", "/>").strip()
        out.append(f'<symbol id="i-{n}" viewBox="0 0 24 24">{inner}</symbol>')
    return '\n'.join(out + ['</svg>'])


def ic(nom, U):
    U.add(nom)
    return f'<svg class="i" aria-hidden="true"><use href="#i-{nom}"/></svg>'


def decouper(html):
    parts, pos = [], 0
    for m in re.finditer(r'<script\b[^>]*>.*?</script>', html, re.S):
        parts += [('html', html[pos:m.start()]), ('js', m.group(0))]
        pos = m.end()
    return parts + [('html', html[pos:])]


# ---------- petit lexer JS : repère chaînes, commentaires, regex ----------
def jetons_js(code):
    """Renvoie une liste de (type, texte) : 'code', 'str', 'com'."""
    out, i, n, buf = [], 0, len(code), []
    def flush():
        if buf: out.append(('code', ''.join(buf))); buf.clear()
    prec = ''
    while i < n:
        c = code[i]
        if c == '/' and code[i+1:i+2] == '/':
            j = code.find('\n', i); j = n if j < 0 else j
            flush(); out.append(('com', code[i:j])); i = j; continue
        if c == '/' and code[i+1:i+2] == '*':
            j = code.index('*/', i) + 2
            flush(); out.append(('com', code[i:j])); i = j; continue
        if c in '\'"`':
            j = i + 1
            while code[j] != c:
                j += 2 if code[j] == '\\' else 1
            flush(); out.append(('str', code[i:j+1])); i = j + 1; prec = 'x'; continue
        if c == '/' and (prec == '' or prec in '(,=:[!&|?{};+'):
            j = i + 1; dans_classe = False
            while True:
                if code[j] == '\\': j += 2; continue
                if code[j] == '[': dans_classe = True
                elif code[j] == ']': dans_classe = False
                elif code[j] == '/' and not dans_classe: break
                j += 1
            j += 1
            while j < n and code[j].isalpha(): j += 1
            buf.append(code[i:j]); i = j; prec = 'x'; continue
        buf.append(c)
        if not c.isspace(): prec = c
        i += 1
    flush()
    return out


def squelette(code):
    return ''.join(t if k != 'str' else t[0] + t[-1] for k, t in jetons_js(code))


def typo_js_chaine(s):
    """Typographie d'une chaîne JS affichée (guillemets conservés aux extrémités)."""
    q, corps = s[0], s[1:-1]
    corps = corps.replace("\\'", '’')
    corps = re.sub(r' ([?!;»])', NNBSP + r'\1', corps)
    corps = re.sub(r' :', NBSP + ':', corps)
    corps = corps.replace('« ', '«' + NNBSP)
    corps = re.sub(r'(\d) (\d{3})(?!\d)', '\\1' + NNBSP + '\\2', corps)
    corps = re.sub(r'(\d) (F|€|ans|jours|heures|minutes|semaines)(?!\w)', '\\1' + NBSP + '\\2', corps)
    return q + corps + q


def lignes_tracking(code):
    return collections.Counter(l for l in code.split('\n') if any(t in l for t in JETONS_TRACKING))


def retoucher_script_principal(js, paires=None):
    nouveau = js
    for avant, apres, nb in (textes.JS if paires is None else paires):
        c = nouveau.count(avant)
        assert c == nb, f'JS : {nb} attendu(s), {c} trouvé(s) : {avant!r}'
        nouveau = nouveau.replace(avant, apres)
    # typographie dans les chaînes affichées (jamais sur une ligne de tracking)
    sortie, ligne_courante = [], ''
    toks = jetons_js(nouveau)
    pos = 0
    for k, t in toks:
        debut = nouveau.rfind('\n', 0, pos) + 1
        fin = nouveau.find('\n', pos); fin = len(nouveau) if fin < 0 else fin
        ligne = nouveau[debut:fin]
        if k == 'str' and t[0] == "'" and re.search(r'[a-zà-ÿ]', t) and not any(j in ligne for j in JETONS_TRACKING):
            sortie.append(typo_js_chaine(t))
        else:
            sortie.append(t)
        pos += len(t)
    nouveau = ''.join(sortie)
    assert squelette(nouveau) == squelette(js), 'le code (hors chaînes) a changé'
    assert lignes_tracking(nouveau) == lignes_tracking(js), 'une ligne de tracking a changé'
    return nouveau


def typo_texte(t):
    t = t.replace("'", '’')
    t = re.sub(r' ([?!;»])', NNBSP + r'\1', t)
    t = re.sub(r' :', NBSP + ':', t)
    t = re.sub(r'(\d) (\d{3})(?!\d)', '\\1' + NNBSP + '\\2', t)
    t = re.sub(r'(\d) (F|€|CAD|\$|ans|jours|heures|minutes|min|semaines|leçons|modules|bonus)(?!\w)', '\\1' + NBSP + '\\2', t)
    t = re.sub(r' ·', NBSP + '·', t)
    t = re.sub(r'(\d) %', '\\1' + NNBSP + '%', t)
    return t.replace('« ', '«' + NNBSP)


def liens_pied(html):
    """Pied de page : les séparateurs « · » entre liens disparaissent, l'espacement est fait en CSS (jamais orphelin)."""
    return re.sub(r'<p style="margin-top:8px">((?:<a [^>]*>[^<]*</a>(?: · )?)+)</p>',
                  lambda m: '<p class="liens-pied">' + m.group(1).replace('</a> · <a', '</a><a') + '</p>', html)


def typo(html, pied=True):
    if pied:
        html = liens_pied(html)
    morceaux = re.split(r'(<style\b.*?</style>|<!--.*?-->|<[^>]+>)', html, flags=re.S)
    return ''.join(m if (m.startswith('<') or not m) else typo_texte(m) for m in morceaux)


APPLIQUES = collections.Counter()


def appliquer_html(h, paires):
    for a, b in paires:
        if a in h:
            APPLIQUES[a] += h.count(a)
            h = h.replace(a, b)
    return h


def html_index(h, U):
    h = appliquer_html(h, textes.HTML)
    # ---- accueil : deux chemins clairs ----
    if '<div id="welcomeScreen">' in h:
        ancien = re.search(r'  <div class="welcome-content">.*?\n  </div>\n</div>', h, re.S).group(0)
        h = h.replace(ancien, f'''  <div class="welcome-content">
    <div class="welcome-icon" aria-hidden="true">{ic('sparkles', U)}</div>
    <h1 class="welcome-title">3 minutes pour te connaître</h1>
    <p class="welcome-sub">Et concevoir un programme sur mesure adapté à ton profil.</p>
    <div class="welcome-paths">
      <button class="welcome-btn" onclick="startQuizFromWelcome()">Faire mon bilan personnalisé {ic('arrow-right', U)}</button>
      <p class="welcome-footnote">Aucune bonne ou mauvaise réponse. Juste toi.</p>
      <div class="welcome-or">ou</div>
      <button type="button" class="welcome-alt" onclick="voirOffreDirectement()">Voir l'offre de lancement {ic('arrow-right', U)}</button>
      <p class="welcome-alt-note">Tu connais déjà la formation ? Le tarif de lancement t'attend.</p>
    </div>
  </div>
</div>''')
    # ---- icônes ----
    def sub(balise, classe, table=EMOJI_ICONE):
        nonlocal h
        def f(m):
            assert m.group(2) in table, f'emoji sans icône : {m.group(2)!r}'
            return f'{m.group(1)}{ic(table[m.group(2)], U)}</{balise}>'
        h = re.sub(rf'(<{balise} class="{re.escape(classe)}"[^>]*>)([^<]+)</{balise}>', f, h)
    for c in ['option-emoji', 'module-icon', 'lesson-icon icon-video', 'lesson-icon icon-eval']:
        sub('span', c)
    for c in ['result-summary-emoji', 'outcome-emoji', 'compare-avatar', 'guarantee-emoji']:
        sub('div', c)
    sub('div', 'bonus-emoji', {**EMOJI_ICONE, **BONUS_ICONE})
    h = re.sub(r'<div class="item"><span>[^<]+</span><span>', lambda m: f'<div class="item">{ic("check", U)}<span>', h)
    autres = [
        ('<span class="unlock-pill">🎁 Débloqué</span>', f'<span class="unlock-pill">{ic("gift", U)}<span data-direct="Lancement">Débloqué</span></span>'),
        ('<span id="unlockText">Offre de lancement activée suite à ton bilan</span>', '<span id="unlockText">Offre de lancement activée suite à ton bilan</span>'),
        ('onclick="switchProfile(\'salarie\')">💼 Salarié</button>', f'onclick="switchProfile(\'salarie\')">{ic("briefcase", U)}Salarié</button>'),
        ('onclick="switchProfile(\'freelance\')">💻 Freelance</button>', f'onclick="switchProfile(\'freelance\')">{ic("laptop", U)}Freelance</button>'),
        ('onclick="switchProfile(\'entrepreneur\')">🚀 Entrepreneur</button>', f'onclick="switchProfile(\'entrepreneur\')">{ic("rocket", U)}Entrepreneur</button>'),
        ('<div class="bonus-flash"><span>🎁 5 bonus débloqués par ton bilan</span></div>', f'<div class="bonus-flash">{ic("gift", U)}<span data-direct="5 bonus offerts avec l’offre de lancement">5 bonus débloqués par ton bilan</span></div>'),
        ('<div class="section-kicker">💬 Ils l\'ont déjà fait</div>', f'<div class="section-kicker">{ic("message-circle", U)}Ils l\'ont déjà fait</div>'),
        ('<div class="price-differentiator">🔒 Un seul paiement', f'<div class="price-differentiator">{ic("lock", U)}Un seul paiement'),
        ('<div class="price-unlock-tag">🎁 Offre débloquée par ton bilan</div>', f'<div class="price-unlock-tag">{ic("gift", U)}<span data-direct="Offre de lancement">Offre débloquée par ton bilan</span></div>'),
        ('<div class="price-forever">Tarif de lancement', f'<div class="price-forever">{ic("sparkles", U)}Tarif de lancement'),
        ('<p style="text-align:center;margin-top:24px;font-size:13px;color:var(--muted)">📩 Si l\'email', f'<p class="note-centre">{ic("mail", U)}<span>Si l\'email'),
        ('vérifie tes spams ou écris-nous.</p>', 'vérifie tes spams ou écris-nous.</span></p>'),
        ('<p style="font-size:12.5px;color:var(--muted);margin-top:14px;line-height:1.55;font-weight:500">🔒 Zéro spam', f'<p class="note-discrete">{ic("lock", U)}<span>Zéro spam'),
        ('Tu peux te désinscrire en un clic.</p>', 'Tu peux te désinscrire en un clic.</span></p>'),
        ('title="WhatsApp" aria-label="Contacter par WhatsApp">💬</a>', f'title="WhatsApp" aria-label="Contacter par WhatsApp">{ic("message-circle", U)}</a>'),
        ('title="Email" aria-label="Contacter par email">✉️</a>', f'title="Email" aria-label="Contacter par email">{ic("mail", U)}</a>'),
        ('<div class="section-eyebrow">◆ ', '<div class="section-eyebrow">'),
        ('>Découvrir mon plan</button>', f'>Découvrir mon plan {ic("arrow-right", U)}</button>'),
        ('>Voir mon programme</button>', f'>Voir mon programme {ic("arrow-right", U)}</button>'),
        ('class="product-nav-cta">Voir mon offre →</a>', 'class="product-nav-cta">Voir mon offre</a>'),
        ('style="max-width:360px;margin:0 auto">Je décroche ma certification →</a>', f'style="max-width:400px;margin:0 auto">Je décroche ma certification {ic("arrow-right", U)}</a>'),
        ('<div class="product-hero-name" id="heroName">', '<div class="product-hero-name" id="heroName">'),
    ]
    h = appliquer_html(h, autres)
    a = '<div class="price-payment">💳 Carte bancaire &nbsp;·&nbsp; 📱 Mobile Money &nbsp;·&nbsp; 100% sécurisé</div>'
    if a in h:
        APPLIQUES[a] += 1
        logos = ''.join(f'<li><img src="assets/paiement/{f}" alt="{alt}" width="{w}" height="{hh}" loading="lazy" decoding="async"></li>'
                        for f, alt, w, hh in [('mtn-momo.webp', 'MTN MoMo', 24, 24), ('moov-money.webp', 'Moov Money', 27, 24),
                                              ('orange-money.svg', 'Orange Money', 67, 18), ('wave.webp', 'Wave', 55, 24),
                                              ('visa.svg', 'Visa', 55, 18), ('mastercard.svg', 'Mastercard', 36, 22)])
        h = h.replace(a, f'<ul class="moyens" aria-label="Moyens de paiement acceptés">{logos}</ul>\n'
                         f'        <div class="price-payment">{ic("lock", U)}<span>Carte bancaire ou Mobile Money, paiement 100 % sécurisé</span></div>')
    a = '      <div class="price-nono">'
    if a in h:
        APPLIQUES[a] += 1
        h = h.replace(a, f'''      <div class="garantie-simple">
        <div class="gs-tete"><span class="gs-ic">{ic("shield-check", U)}</span><h3>La garantie 7 jours, simplement</h3></div>
        <ol>
          <li><span><b>Tu as 7 jours pour essayer,</b> comptés à partir du jour de ton achat. Suis le premier module, teste la méthode.</span></li>
          <li><span><b>Ça ne te convient pas ?</b> Écris à <a href="mailto:contact@emkbluediamond.online?subject=Demande%20de%20remboursement">contact@emkbluediamond.online</a> avec pour objet « Demande de remboursement » et l'email utilisé pour l'achat.</span></li>
          <li><span><b>Tu es remboursé en entier,</b> sans avoir à te justifier, sous 3 à 5 jours ouvrables, sur le moyen de paiement que tu as utilisé.</span></li>
        </ol>
      </div>

''' + a)
    bloc = re.search(r'\n      <div class="guarantee">.*?\n      </div>\n', h, re.S)
    if bloc and '7 jours pour changer' in bloc.group(0):
        APPLIQUES['guarantee'] += 1
        h = h.replace(bloc.group(0), '\n')
    for lib in ['Je continue', 'Continuer', 'Montre-moi ça', 'Je veux être du bon côté']:
        h = h.replace(f'<button class="continue-btn" onclick="next()">{lib}</button>',
                      f'<button class="continue-btn" onclick="next()">{lib} {ic("arrow-right", U)}</button>')
    h = h.replace('<button class="continue-btn" id="nameBtn" onclick="next()" disabled>C\'est parti</button>',
                  f'<button class="continue-btn" id="nameBtn" onclick="next()" disabled>C\'est parti {ic("arrow-right", U)}</button>')
    return typo(h)


def construire_index():
    src = (SRC / 'index.html').read_text(encoding='utf-8')
    U, out = set(), []
    parts = decouper(src)
    for k, p in parts:
        if k == 'js':
            out.append(retoucher_script_principal(p) if 'const screens=' in p else p)
            continue
        if FONTS_OLD in p:
            i = p.index('</style>') + len('</style>')
            p = p[:i] + '\n<!-- Retouches v3.1 (présentation seulement) -->\n<style>\n' + (ICI / 'retouches.css').read_text() + '</style>' + p[i:]
        out.append(html_index(p, U))
    html = ''.join(out)
    html = html.replace('<body>\n', '<body>\n' + sprite(U) + '\n', 1)
    html = html.replace('\n</body>', '\n<script>\n' + (ICI / 'raccourci.js').read_text() + '</script>\n\n</body>', 1)
    # contrôles
    tous = textes.HTML + [(a, None) for a in []]
    assert APPLIQUES['guarantee'] == 1, 'encadré garantie non trouvé'
    manquants = [a for a, _ in textes.HTML if not APPLIQUES[a]]
    assert not manquants, f'textes non trouvés : {manquants}'
    o = [p for k, p in decouper(src) if k == 'js']
    n = [p for k, p in decouper(html) if k == 'js']
    assert len(n) == len(o) + 1
    for a, b in zip(o, n):
        if 'const screens=' not in a:
            assert a == b, 'un script secondaire a changé'
    return html


def construire_merci():
    src = (SRC / 'merci.html').read_text(encoding='utf-8')
    U, out = set(), []
    for k, p in decouper(src):
        if k == 'js':
            out.append(retoucher_script_principal(p, textes.MERCI_JS if 'leadData' in p and 'getElementById(\'lede\')' in p else [])); continue
        if '</style>' in p:
            i = p.index('</style>') + len('</style>')
            p = p[:i] + '\n<style>\n' + (ICI / 'merci-retouches.css').read_text() + '</style>' + p[i:]
        for a, b in textes.MERCI:
            if a in p:
                APPLIQUES['merci:' + a] += 1
                p = p.replace(a, b)
        p = p.replace('ICONE:message-circle', ic('message-circle', U))
        p = p.replace('<div class="kicker">Paiement confirmé</div>', f'<div class="kicker">{ic("badge-check", U)}Paiement confirmé</div>')
        p = p.replace('\n      Mon espace apprenant\n', f'\n      Mon espace apprenant {ic("arrow-right", U)}\n')
        out.append(typo(p, pied=False))
    html = ''.join(out).replace('<body>\n', '<body>\n' + sprite(U) + '\n', 1)
    html = html.replace('\n</body>', '\n<script>\n' + (ICI / 'merci-texte.js').read_text() + '</script>\n</body>', 1)
    manquants = [a for a, _ in textes.MERCI if not APPLIQUES['merci:' + a]]
    assert not manquants, f'merci : textes non trouvés {manquants}'
    o = [p for k, p in decouper(src) if k == 'js']; n = [p for k, p in decouper(html) if k == 'js']
    assert len(n) == len(o) + 1 and all(squelette(a) == squelette(b) and lignes_tracking(a) == lignes_tracking(b) for a, b in zip(o, n)), 'merci.html : code ou tracking modifié'
    return html


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'index.html').write_text(construire_index(), encoding='utf-8')
    (OUT / 'merci.html').write_text(construire_merci(), encoding='utf-8')
    print('ok')
