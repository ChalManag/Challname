// EXEMPLE de service de licences (Cloudflare Worker + KV). À adapter et à sécuriser avant usage réel.
// Variables : KV namespace "LICENSES" ; secret "WEBHOOK_SECRET" (partagé avec le prestataire de paiement).
// Le jeu appelle POST /verify {key} et attend {ok:true, exp:<timestamp ms>}.
// Le prestataire de paiement appelle POST /webhook (à vérifier avec SA méthode de signature officielle).
const cors = { 'Access-Control-Allow-Origin': 'https://VOTRE-DOMAINE.example', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { 'Content-Type': 'application/json', ...cors } });
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (url.pathname === '/verify' && req.method === 'POST') {
      const { key } = await req.json().catch(() => ({}));
      if (!key || typeof key !== 'string') return json({ ok: false }, 400);
      const rec = await env.LICENSES.get('k:' + key, 'json');
      if (!rec || rec.exp < Date.now()) return json({ ok: false });
      return json({ ok: true, exp: rec.exp });
    }
    if (url.pathname === '/webhook' && req.method === 'POST') {
      // TODO : vérifier la signature du prestataire (Paddle / Lemon Squeezy / Stripe) avec WEBHOOK_SECRET.
      const evt = await req.json().catch(() => null);
      if (!evt) return json({ ok: false }, 400);
      const key = 'CC-' + crypto.randomUUID().toUpperCase();
      const days = evt.plan === 'year' ? 366 : evt.plan === 'lifetime' ? 36500 : 31;
      await env.LICENSES.put('k:' + key, JSON.stringify({ exp: Date.now() + days * 864e5, email: evt.email || '' }));
      // TODO : envoyer la clé par e-mail à l'acheteur.
      return json({ ok: true });
    }
    return json({ ok: false }, 404);
  }
};
