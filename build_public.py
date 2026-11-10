#!/usr/bin/env python3
"""Génère l'édition PUBLIQUE (fictive, sans marque) à partir de ../cdl-manager.html
Usage : python3 build_public.py
Sortie : ./public/  (à déposer tel quel sur Cloudflare Pages / Netlify / GitHub Pages)
Le script ÉCHOUE si un terme de marque réel subsiste dans les fichiers produits."""
import re, os, sys, json, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'cdl-manager.html')
OUT = os.path.join(HERE, 'public')
SITE = {
    'name': 'CALLMAN',
    'tagline': "Jeu de management esport FPS : dirige une franchise ou deviens le joueur que toute la ligue redoute.",
    'domain': 'https://VOTRE-PSEUDO.github.io/callman',   # à remplacer (adresse GitHub Pages ou domaine perso)
    'editeur': "[NOM PRÉNOM ou RAISON SOCIALE]",
    'adresse': "[ADRESSE POSTALE]",
    'email': "[EMAIL DE CONTACT]",
    'siret': "[SIRET]",
    'hebergeur': "[NOM DE L'HÉBERGEUR, ADRESSE, SITE]",
}
# termes qui ne doivent JAMAIS apparaître dans l'édition publique (insensible à la casse)
BANNED = ['cdl', 'call of duty', 'activision', 'hardpoint', 'overload', 'search & destroy', 'recherche & destruction',
          'search &amp; destroy', 'recherche &amp; destruction', 'optic', 'faze', 'thieves', 'cloud9', 'gentle mates',
          'heretics', 'royal ravens', 'vancouver', 'warzone', 'black ops', 'treyarch', 'infinity ward', 'modern warfare']
BANNED_WORD = [r'\bG2\b', r'\bUltra\b', r'\bBreach\b', r'\bSurge\b', r'\bFalcons\b']

src = open(SRC, encoding='utf-8').read()

# 1. édition
assert "const EDITION='fan';" in src, "ligne EDITION introuvable"
html = src.replace("const EDITION='fan';", "const EDITION='public';")

# 2. suppression des blocs réservés à l'édition fan
html, n = re.subn(r"/\*FAN-START\*/.*?/\*FAN-END\*/", "", html, flags=re.S)
print(f"blocs fan supprimés : {n}")

# 3. commentaire d'en-tête
html = re.sub(r"/\* =+\n\s+CDL MANAGER.*?=+ \*/", "/* CALLMAN — jeu indépendant (noms fictifs) */", html, flags=re.S)

# 4. clés de stockage et nom d'export sans référence à la marque d'origine
for a, b in [('cdl_manager_save_v1', 'cc_m_v1'), ('cdl_player_save_v1', 'cc_p_v1'), ('cdl_hof_v1', 'cc_h_v1'),
             ('cdl_nameset', 'cc_ns'), ('cdl-manager-S', 'clutch-circuit-S')]:
    html = html.replace(a, b)

# 5. <head> : titre, méta, manifest, icône, sans Google Fonts (pas d'appel tiers avant consentement)
head_new = f'''<title>{SITE['name']} — Jeu de management esport FPS</title>
<meta name="description" content="{SITE['tagline']}">
<meta name="theme-color" content="#07090c">
<meta property="og:type" content="website"><meta property="og:title" content="{SITE['name']}">
<meta property="og:description" content="{SITE['tagline']}"><meta property="og:url" content="{SITE['domain']}/">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{SITE['domain']}/">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">'''
html = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*<link href="https://fonts\.googleapis\.com[^>]*>', '', html)
html = html.replace('<title>CDL Manager</title>', head_new)
html = html.replace('<div id="app" class="app"></div>', '<noscript>Ce jeu nécessite JavaScript.</noscript><div id="app" class="app"></div>')
# service worker (cache hors ligne)
html = html.replace('</script>\n</body>', "if('serviceWorker' in navigator&&location.protocol.startsWith('http'))navigator.serviceWorker.register('sw.js').catch(()=>{});\n</script>\n</body>")

# 6. contrôle des termes interdits
def check(text, label):
    low = text.lower()
    bad = [t for t in BANNED if t in low]
    bad += [p for p in BANNED_WORD if re.search(p, text)]
    if bad:
        print(f"❌ {label} : termes interdits trouvés : {bad}")
        for t in bad:
            i = low.find(t.lower()) if t in BANNED else re.search(t, text).start()
            print('   …', text[max(0, i-60): i+80].replace('\n', ' '), '…')
        sys.exit(1)
check(html, 'index.html')

# 7. sortie
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#07090c"/><path d="M14 44 L26 28 L36 36 L50 16" fill="none" stroke="#b8ff2c" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="50" cy="16" r="4" fill="#ff7a1a"/></svg>'''
open(os.path.join(OUT, 'icon.svg'), 'w').write(icon)
open(os.path.join(OUT, 'manifest.webmanifest'), 'w').write(json.dumps({
    'name': SITE['name'], 'short_name': SITE['name'], 'start_url': './', 'display': 'standalone',
    'background_color': '#07090c', 'theme_color': '#07090c', 'lang': 'fr',
    'icons': [{'src': 'icon.svg', 'sizes': 'any', 'type': 'image/svg+xml', 'purpose': 'any'}]}, indent=2))
open(os.path.join(OUT, 'sw.js'), 'w').write('''const C='cc-v1';
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','icon.svg'])));self.skipWaiting()});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin)return;
 e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request)))});
''')
open(os.path.join(OUT, 'robots.txt'), 'w').write(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
today = datetime.date.today().isoformat()
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
 <url><loc>{SITE['domain']}/</loc><lastmod>{today}</lastmod></url>
 <url><loc>{SITE['domain']}/privacy.html</loc><lastmod>{today}</lastmod></url>
 <url><loc>{SITE['domain']}/mentions-legales.html</loc><lastmod>{today}</lastmod></url>
 <url><loc>{SITE['domain']}/cgv.html</loc><lastmod>{today}</lastmod></url>
</urlset>
''')
open(os.path.join(OUT, 'ads.txt'), 'w').write("# Remplacer par la ligne fournie par AdSense, par exemple :\n# google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0\n")
open(os.path.join(OUT, '_headers'), 'w').write('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  X-Frame-Options: SAMEORIGIN
  # CSP de départ SANS publicité. Quand vous activez AdSense/une CMP, ajoutez leurs domaines
  # (pagead2.googlesyndication.com, fundingchoicesmessages.google.com, *.doubleclick.net, *.google.com…)
  # dans script-src, frame-src, img-src et connect-src.
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self'
''')

# 8. pages légales (MODÈLES à faire valider)
def page(title, body):
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — {SITE['name']}</title><meta name="robots" content="noindex">
<style>body{{font:16px/1.6 system-ui,Segoe UI,sans-serif;background:#07090c;color:#e7edf4;max-width:820px;margin:0 auto;padding:24px 18px 60px}}a{{color:#b8ff2c}}h1,h2{{font-family:system-ui;letter-spacing:.02em}}h2{{margin-top:28px;border-bottom:1px solid #222d3b;padding-bottom:6px}}.warn{{background:#2a1f0a;border:1px solid #7a4a14;color:#ffb35c;padding:10px 14px;border-radius:6px}}code{{background:#111821;padding:1px 5px;border-radius:3px}}</style></head><body>
<p><a href="./">← Retour au jeu</a></p><h1>{title}</h1>
<p class="warn"><b>Modèle à compléter et à faire relire</b> par un professionnel avant mise en ligne : remplacez tout ce qui est entre crochets.</p>{body}</body></html>'''
open(os.path.join(OUT, 'mentions-legales.html'), 'w', encoding='utf-8').write(page('Mentions légales', f'''
<h2>Éditeur</h2><p>{SITE['name']} est édité par {SITE['editeur']}, {SITE['adresse']}. SIRET : {SITE['siret']}. Contact : {SITE['email']}.</p>
<p>Directeur de la publication : {SITE['editeur']}.</p>
<h2>Hébergeur</h2><p>{SITE['hebergeur']}.</p>
<h2>Propriété intellectuelle</h2><p>Le code, les illustrations (dessinées en SVG) et les sons (synthétisés dans le navigateur) sont originaux. Tous les noms d'équipes, de joueurs et de modes de jeu sont fictifs ; toute ressemblance avec des personnes ou organisations existantes serait fortuite.</p>
<h2>Signalement</h2><p>Pour tout signalement de contenu, écrivez à {SITE['email']}.</p>'''))
open(os.path.join(OUT, 'privacy.html'), 'w', encoding='utf-8').write(page('Politique de confidentialité', f'''
<h2>Responsable du traitement</h2><p>{SITE['editeur']} — {SITE['email']}.</p>
<h2>Données traitées</h2><ul>
<li><b>Sauvegardes et préférences du jeu</b> (progression, son, choix de consentement) : stockées uniquement dans votre navigateur (<code>localStorage</code>). Elles ne sont pas transmises à nos serveurs. Base : exécution du service.</li>
<li><b>Mesure d'audience</b> : [aucune / outil respectueux de la vie privée — à préciser].</li>
<li><b>Publicité</b> : uniquement si vous l'acceptez via la bannière. Des cookies et identifiants peuvent alors être déposés par nos partenaires publicitaires [nom de la régie / de la CMP]. Base : consentement, retirable à tout moment (lien « Cookies » en bas de page d'accueil).</li>
<li><b>Abonnement Premium</b> : le paiement est géré par [prestataire de paiement] ; nous ne conservons ni vos données bancaires ni vos données de carte. Une clé de licence est vérifiée auprès de notre service de licences.</li></ul>
<h2>Durées</h2><p>Les données locales restent sur votre appareil jusqu'à ce que vous les supprimiez. Les choix de consentement sont conservés [6 mois — à ajuster].</p>
<h2>Vos droits</h2><p>Accès, rectification, effacement, opposition, limitation, portabilité : {SITE['email']}. Réclamation possible auprès de la CNIL (cnil.fr).</p>
<h2>Mineurs</h2><p>Le jeu ne s'adresse pas aux moins de [16] ans et n'affiche pas de publicité personnalisée aux mineurs.</p>'''))
open(os.path.join(OUT, 'cgv.html'), 'w', encoding='utf-8').write(page('Conditions générales de vente (Premium)', f'''
<h2>Offre</h2><p>L'offre « Circuit Pass » supprime la publicité et débloque des options cosmétiques et sonores. Prix TTC affichés au moment de l'achat : [2,99 €/mois, 24,99 €/an ou 39 € en paiement unique — à confirmer].</p>
<h2>Vendeur et paiement</h2><p>Le paiement est traité par [prestataire, agissant comme vendeur officiel ou non — à préciser], qui émet la facture.</p>
<h2>Droit de rétractation</h2><p>Vous disposez de 14 jours pour vous rétracter, sauf si vous demandez l'accès immédiat au contenu numérique et reconnaissez perdre votre droit de rétractation une fois le contenu fourni. [Texte à valider.]</p>
<h2>Résiliation</h2><p>L'abonnement se résilie en ligne à tout moment depuis [lien du portail client du prestataire]. L'accès reste actif jusqu'à la fin de la période payée.</p>
<h2>Licence</h2><p>La clé de licence est personnelle. Contact et réclamations : {SITE['email']}. Médiateur de la consommation : [nom et coordonnées].</p>'''))

# 9. contrôle final de tous les fichiers texte produits
for f in os.listdir(OUT):
    if f.endswith(('.html', '.js', '.json', '.webmanifest', '.txt', '.xml')):
        check(open(os.path.join(OUT, f), encoding='utf-8').read(), f)
print('✅ édition publique générée dans', OUT, '—', round(os.path.getsize(os.path.join(OUT, 'index.html'))/1024), 'Ko')
