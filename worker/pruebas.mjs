/**
 * Pruebas del Worker de recepción de formatos.
 *
 *     node worker/pruebas.mjs        (o `npm test` dentro de worker/)
 *
 * No hacen falta ni Cloudflare ni red: el KV y la API de GitHub van de mentira, así que se pueden
 * ejercitar los caminos que en producción no se pueden provocar a mano — GitHub caído, el captcha
 * rechazando, el límite por IP agotándose.
 *
 * Cada caso de aquí es un fallo que hemos tenido de verdad o que estuvo a punto de pasar, no una
 * comprobación de adorno. Si añades uno, que sea por el mismo motivo.
 */
import worker from './src/index.js';

// --- KV de mentira -----------------------------------------------------------------------------
function kvFalso() {
  const m = new Map();
  return {
    _m: m,
    async get(k) { return m.has(k) ? m.get(k) : null; },
    async put(k, v) { m.set(k, v); },
    async delete(k) { m.delete(k); },
    async list({ prefix = '', limit = 1000 } = {}) {
      return { keys: [...m.keys()].filter((k) => k.startsWith(prefix)).slice(0, limit).map((name) => ({ name })) };
    },
  };
}

// --- fetch de mentira: siteverify y la API de GitHub --------------------------------------------
let githubOk = true, issuesCreados = 0, siteverifyOk = true;
globalThis.fetch = async (url, opciones) => {
  if (String(url).includes('siteverify')) {
    return new Response(JSON.stringify(siteverifyOk ? { success: true } : { success: false, 'error-codes': ['invalid-input-secret'] }));
  }
  if (String(url).includes('api.github.com')) {
    if (!githubOk) return new Response('{"message":"Bad credentials"}', { status: 401 });
    issuesCreados++;
    return new Response(JSON.stringify({ number: 100 + issuesCreados }), { status: 201 });
  }
  throw new Error('petición inesperada a ' + url);
};

const env = () => ({ LIMITES: kvFalso(), TURNSTILE_SECRET: 's', GITHUB_TOKEN: 'g', SAL_IP: 'sal' });
const VALIDO = { entidad: 'BBVA', paquete: 'com.bbva.app', tipo: 'Bizum',
                 plantilla: 'texto: Bizum de <importe> a <comercio>', turnstile: 'x'.repeat(20) };

const pedir = (e, cuerpo, cab = {}) => worker.fetch(new Request('https://api.xtracto.app/formato', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Origin: 'https://xtracto.app', 'CF-Connecting-IP': '1.2.3.4', ...cab },
  body: JSON.stringify(cuerpo),
}), e);

let fallos = 0;
const comprobar = async (nombre, fn) => {
  try { await fn(); console.log(`  ✓ ${nombre}`); }
  catch (e) { fallos++; console.log(`  ✗ ${nombre}\n      ${e.message}`); }
};
const igual = (a, b, q) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${q}: esperaba ${JSON.stringify(b)}, salió ${JSON.stringify(a)}`); };

await comprobar('envío válido crea el issue', async () => {
  githubOk = true; const e = env();
  const r = await pedir(e, VALIDO); const j = await r.json();
  igual([r.status, j.ok, j.estado], [200, true, 'creado'], 'respuesta');
  igual([...e.LIMITES._m.keys()].filter(k => k.startsWith('ip:')).length, 1, 'contador');
});

await comprobar('GitHub caído: se guarda en espera, no se pierde', async () => {
  githubOk = false; const e = env();
  const r = await pedir(e, VALIDO); const j = await r.json();
  igual([r.status, j.ok, j.estado], [200, true, 'en_espera'], 'respuesta');
  const pend = [...e.LIMITES._m.keys()].filter(k => k.startsWith('pendiente:'));
  igual(pend.length, 1, 'guardados');
  igual(JSON.parse(e.LIMITES._m.get(pend[0])).entidad, 'BBVA', 'contenido');
});

await comprobar('el disparo programado lo publica y lo borra', async () => {
  githubOk = false; const e = env();
  await pedir(e, VALIDO);
  githubOk = true;
  const tareas = []; await worker.scheduled({}, e, { waitUntil: (p) => tareas.push(p) });
  await Promise.all(tareas);
  igual([...e.LIMITES._m.keys()].filter(k => k.startsWith('pendiente:')).length, 0, 'quedan pendientes');
});

await comprobar('si GitHub sigue caído, el pendiente se conserva', async () => {
  githubOk = false; const e = env();
  await pedir(e, VALIDO);
  const tareas = []; await worker.scheduled({}, e, { waitUntil: (p) => tareas.push(p) });
  await Promise.all(tareas);
  igual([...e.LIMITES._m.keys()].filter(k => k.startsWith('pendiente:')).length, 1, 'se ha perdido');
});

await comprobar('captcha rechazado no gasta cuota', async () => {
  siteverifyOk = false; githubOk = true; const e = env();
  for (let i = 0; i < 8; i++) await pedir(e, VALIDO);
  siteverifyOk = true;
  igual([...e.LIMITES._m.keys()].filter(k => k.startsWith('ip:')).length, 0, 'contador tocado');
  const r = await pedir(e, VALIDO);
  igual((await r.json()).estado, 'creado', 'debería poder enviar');
});

await comprobar('sin token: motivo captcha_sin_token', async () => {
  const r = await pedir(env(), { ...VALIDO, turnstile: '' });
  igual([r.status, (await r.json()).motivo], [403, 'captcha_sin_token'], 'respuesta');
});

await comprobar('plantilla con cifras: rechazada y sin gastar cuota', async () => {
  const e = env();
  const r = await pedir(e, { ...VALIDO, plantilla: 'Compra de 41,52 EUR en MERCADONA' });
  igual([r.status, (await r.json()).motivo], [400, 'plantilla_con_cifras'], 'respuesta');
  igual([...e.LIMITES._m.keys()].length, 0, 'no debía apuntar nada');
});

await comprobar('el límite corta al sexto', async () => {
  githubOk = true; const e = env();
  for (let i = 0; i < 5; i++) igual((await (await pedir(e, VALIDO)).json()).estado, 'creado', `envío ${i + 1}`);
  const r = await pedir(e, VALIDO);
  igual([r.status, (await r.json()).motivo], [429, 'limite'], 'sexto');
});

await comprobar('campo trampa: se descarta fingiendo que fue bien', async () => {
  const e = env();
  const j = await (await pedir(e, { ...VALIDO, web: 'robot' })).json();
  igual([j.ok, j.estado], [true, 'descartado'], 'respuesta');
  igual([...e.LIMITES._m.keys()].length, 0, 'no debía tocar el KV');
});

await comprobar('origen ajeno: 403', async () => {
  const r = await pedir(env(), VALIDO, { Origin: 'https://malo.example' });
  igual([r.status, (await r.json()).motivo], [403, 'origen'], 'respuesta');
});

await comprobar('acentos graves y arrobas saneados en el issue', async () => {
  githubOk = true; let visto = null;
  const antes = globalThis.fetch;
  globalThis.fetch = async (u, o) => { if (String(u).includes('api.github')) { visto = JSON.parse(o.body).body; } return antes(u, o); };
  await pedir(env(), { ...VALIDO, plantilla: 'texto: ```escapa``` y @miguelable' });
  globalThis.fetch = antes;
  if (visto.includes('```escapa```')) throw new Error('los acentos graves no se sanearon');
  if (visto.includes('@miguelable')) throw new Error('la arroba no se saneó');
});

await comprobar('las respuestas declaran Vary: Origin', async () => {
  const buena = await pedir(env(), VALIDO);
  const mala = await pedir(env(), VALIDO, { Origin: 'https://malo.example' });
  igual([buena.headers.get('Vary'), mala.headers.get('Vary')], ['Origin', 'Origin'], 'cabecera');
});

console.log(fallos ? `\n${fallos} FALLOS` : '\nlas 12 pruebas pasan');
process.exit(fallos ? 1 : 0);
