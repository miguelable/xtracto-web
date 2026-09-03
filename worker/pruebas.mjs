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

const pedirA = (ruta, e, cuerpo, cab = {}) => worker.fetch(new Request('https://api.xtracto.app' + ruta, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Origin: 'https://xtracto.app', 'CF-Connecting-IP': '1.2.3.4', ...cab },
  body: JSON.stringify(cuerpo),
}), e);
const pedir = (e, cuerpo, cab = {}) => pedirA('/formato', e, cuerpo, cab);

/** Alta de banco: ni plantilla ni tipo, que es justo el punto. */
const BANCO = { entidad: 'Kutxabank', pais: 'España', paquete: 'com.kutxabank.android',
                turnstile: 'x'.repeat(20) };
const pedirBanco = (e, cuerpo, cab = {}) => pedirA('/banco', e, cuerpo, cab);

/** Devuelve el JSON que se le mandó a GitHub, para poder mirar título, cuerpo y etiquetas. */
const espiarIssue = async (fn) => {
  let visto = null;
  const antes = globalThis.fetch;
  globalThis.fetch = async (u, o) => {
    if (String(u).includes('api.github')) visto = JSON.parse(o.body);
    return antes(u, o);
  };
  try { await fn(); } finally { globalThis.fetch = antes; }
  return visto;
};

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

// --- Alta de banco (/banco) --------------------------------------------------------------------
// Existe porque quien tiene un banco fuera del catálogo NO puede usar /formato: la app no archiva
// nada de una app que no reconoce, así que no tiene plantilla que pegar.

await comprobar('alta de banco válida crea el issue con su etiqueta', async () => {
  githubOk = true;
  const issue = await espiarIssue(async () => {
    const r = await pedirBanco(env(), BANCO);
    igual([r.status, (await r.json()).estado], [200, 'creado'], 'respuesta');
  });
  igual(issue.labels, ['banco', 'via-web'], 'etiquetas');
  if (!issue.title.startsWith('[banco] Kutxabank')) throw new Error('título: ' + issue.title);
  if (!issue.body.includes('España')) throw new Error('el país no aparece en el cuerpo');
});

await comprobar('el paquete es opcional: casi nadie lo sabe', async () => {
  githubOk = true;
  const issue = await espiarIssue(async () => {
    const { paquete, ...sinPaquete } = BANCO;
    const r = await pedirBanco(env(), sinPaquete);
    igual([r.status, (await r.json()).ok], [200, true], 'respuesta');
  });
  if (!issue.body.includes('(no lo sabe)')) throw new Error('debería decir que no lo sabe');
});

await comprobar('un paquete con forma inválida sí se rechaza', async () => {
  const r = await pedirBanco(env(), { ...BANCO, paquete: 'mira https://spam.example' });
  igual([r.status, (await r.json()).motivo], [400, 'paquete'], 'respuesta');
});

await comprobar('el país es obligatorio: hay varios bancos con el mismo nombre', async () => {
  const { pais, ...sinPais } = BANCO;
  const r = await pedirBanco(env(), sinPais);
  igual([r.status, (await r.json()).motivo], [400, 'pais'], 'respuesta');
});

await comprobar('el país no admite cifras ni signos: no cabe una URL ni un teléfono', async () => {
  for (const malo of ['España 28001', 'http://spam.example', 'a@b.c']) {
    const r = await pedirBanco(env(), { ...BANCO, pais: malo });
    igual([r.status, (await r.json()).motivo], [400, 'pais'], 'país «' + malo + '»');
  }
});

await comprobar('un alta que queda en espera se republica como alta, no como formato', async () => {
  // El fallo que esto persigue: los envíos que GitHub rechaza se guardan en el KV y los republica
  // el disparo programado. Si `modo` no viajara con los campos, el alta volvería a salir como un
  // issue de formato, con la plantilla y el tipo a `undefined`.
  githubOk = false;
  const e = env();
  await pedirBanco(e, BANCO);
  githubOk = true;
  // `scheduled` no espera a `waitUntil`: hay que recoger las promesas y esperarlas DENTRO del
  // espía, o el fetch a GitHub ocurre cuando ya se ha restaurado y no se ve nada.
  const issue = await espiarIssue(async () => {
    const tareas = [];
    await worker.scheduled({}, e, { waitUntil: (t) => tareas.push(t) });
    await Promise.all(tareas);
  });
  igual(issue.labels, ['banco', 'via-web'], 'etiquetas del republicado');
  if (issue.body.includes('undefined')) throw new Error('el cuerpo republicado lleva undefined');
});

await comprobar('una ruta que no existe es 404', async () => {
  for (const ruta of ['/', '/formatos', '/banco/x', '/.env']) {
    const r = await pedirA(ruta, env(), VALIDO);
    igual([r.status, (await r.json()).motivo], [404, 'ruta'], 'ruta ' + ruta);
  }
});

console.log(fallos ? `\n${fallos} FALLOS` : '\nlas 19 pruebas pasan');
process.exit(fallos ? 1 : 0);
