# Mise en ligne — mode d'emploi rapide

1. Placer `cdl-manager.html` (édition « fan », privée) à côté du dossier `mise-en-ligne/`.
2. Ouvrir `build_public.py`, remplacer le bloc `SITE` (nom, domaine, éditeur, e-mail…).
3. `python3 build_public.py` → génère `public/` (jeu + pages légales + robots/sitemap + manifest + service worker).
   Le script s'arrête avec une erreur si un nom de marque, d'équipe réelle ou de mode d'une licence existante subsiste.
4. Compléter les pages légales modèles (`public/mentions-legales.html`, `privacy.html`, `cgv.html`).
5. Déposer le contenu de `public/` sur Cloudflare Pages, Netlify ou GitHub Pages, puis brancher le domaine (HTTPS automatique).
6. Pour la pub / Premium : dans `public/index.html`, section `const MONET={…}`, renseigner `adsClient`, `slots`, `verifyUrl`, `buyUrl`
   (voir le document « Plan de mise en ligne et de monétisation »). Mettre à jour `ads.txt` et la CSP dans `_headers`.
   Ne jamais activer la pub avant d'avoir une CMP certifiée et une politique de confidentialité complétée.
7. `worker-licence.js` = exemple de service de licences à adapter (non prêt pour la production).

Test local sans réseau : dans la console du navigateur, `MONET.demo=true` active des emplacements pub factices, un bonus récompensé simulé
et la clé de démonstration `DEMO-PREMIUM`.
