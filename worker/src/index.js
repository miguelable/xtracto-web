/**
 * Recepción de formatos de notificación enviados desde https://xtracto.app/formato.html
 *
 * El objetivo es que cualquiera pueda mandar la plantilla de un aviso que la app no reconoce **sin
 * registrarse en ningún sitio**. El Worker valida, filtra y crea un issue en el repositorio con un
 * token propio, así que quien envía no necesita cuenta de GitHub.
 *
 * Todo lo que llega de fuera se considera hostil. Las defensas, por orden de aplicación:
 *
 *  1. Método, origen y tipo de contenido: solo POST, JSON y desde el propio dominio.
 *  2. Tamaño: el cuerpo se lee como texto y se descarta por longitud ANTES de parsearlo, para no
 *     darle a JSON.parse un megabyte de basura.
 *  3. Turnstile: el captcha de Cloudflare, verificado en el servidor. Sin token válido no se sigue.
 *  4. Límite por IP: cinco envíos por hora. La IP no se guarda: se guarda su hash con sal.
 *  5. Validación estricta campo a campo, con longitudes máximas y juegos de caracteres cerrados.
 *  6. **Ningún dígito en la plantilla.** Es la regla de privacidad del proyecto y de paso corta el
 *     spam, que casi siempre lleva números (teléfonos, precios, URLs).
 *  7. Saneado antes de componer el issue: fuera caracteres de control y acentos graves, para que
 *     nadie pueda escaparse del bloque de código y escribir markdown, enlaces o menciones.
 *
 * El token de GitHub va como secreto del Worker y debe ser un token de acceso preciso con permiso
 * de **Issues: write sobre este único repositorio**. Nada más.
 */

const REPO = 'miguelable/xtracto-web';
const ORIGEN = 'https://xtracto.app';
const MAX_CUERPO = 8 * 1024;
const LIMITE_POR_HORA = 5;

const LIMITES = { entidad: 60, paquete: 100, plantilla: 2000, tipo: 40 };

const TIPOS = new Set([
  'Compra con tarjeta',
  'Recibo domiciliado',
  'Transferencia enviada',
  'Ingreso o abono',
  'Bizum',
  'Otra',
]);

/** Identificador de app Android: minúsculas, puntos y guiones bajos. Nada más. */
const PAQUETE = /^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$/;

/** Caracteres de control, que no pintan nada en un texto pegado por una persona. */
const CONTROL = /[\u0000-\u0008\u000B-\u001F\u007F]/g;

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return preflight();
    if (request.method !== 'POST') return error(405, 'metodo');
    if (request.headers.get('Origin') !== ORIGEN) return error(403, 'origen');

    const tipoContenido = request.headers.get('Content-Type') || '';
    if (!tipoContenido.includes('application/json')) return error(415, 'contenido');

    const crudo = await request.text();
    if (crudo.length > MAX_CUERPO) return error(413, 'tamano');

    let datos;
    try {
      datos = JSON.parse(crudo);
    } catch {
      return error(400, 'json');
    }

    // Trampa para robots: un campo oculto que una persona nunca rellena. Se responde que todo fue
    // bien a propósito, para no enseñarle al robot que lo hemos detectado.
    if (datos.web) return exito('descartado');

    const ip = request.headers.get('CF-Connecting-IP') || '';
    if (await superaLimite(env, ip)) return error(429, 'limite');
    if (!(await turnstileValido(env, datos.turnstile, ip))) return error(403, 'captcha');

    const campos = validar(datos);
    if (campos.error) return error(400, campos.error);

    const numero = await crearIssue(env, campos);
    if (!numero) return error(502, 'github');

    return exito('creado', numero);
  },
};

function validar(datos) {
  const texto = (valor, limite) =>
    typeof valor === 'string' ? valor.normalize('NFC').trim().slice(0, limite) : '';

  const entidad = texto(datos.entidad, LIMITES.entidad);
  const paquete = texto(datos.paquete, LIMITES.paquete);
  const plantilla = texto(datos.plantilla, LIMITES.plantilla);
  const tipo = texto(datos.tipo, LIMITES.tipo);

  if (entidad.length < 2) return { error: 'entidad' };
  if (!PAQUETE.test(paquete)) return { error: 'paquete' };
  if (plantilla.length < 10) return { error: 'plantilla_corta' };
  if (!TIPOS.has(tipo)) return { error: 'tipo' };

  // La regla de oro: si hay un número, puede ser un dato de alguien. No entra.
  if (/\d/.test(plantilla)) return { error: 'plantilla_con_cifras' };

  return { entidad: limpiar(entidad), paquete, plantilla: limpiar(plantilla), tipo };
}

/**
 * Deja el texto en algo que se puede meter dentro de un bloque de código de markdown sin que pueda
 * salirse de él: fuera caracteres de control, fuera acentos graves (que cerrarían el bloque) y
 * fuera arrobas, que en GitHub notifican a usuarios reales.
 */
function limpiar(valor) {
  return valor
    .replace(CONTROL, '')
    .replace(/`/g, "'")
    .replace(/@/g, '(at)')
    .replace(/\n{3,}/g, '\n\n');
}

async function superaLimite(env, ip) {
  if (!env.LIMITES || !ip) return false;
  const clave = 'ip:' + (await sha256(ip + (env.SAL_IP || '')));
  const actual = parseInt((await env.LIMITES.get(clave)) || '0', 10);
  if (actual >= LIMITE_POR_HORA) return true;
  // La IP nunca se almacena en claro: solo su hash con sal, y con caducidad de una hora.
  await env.LIMITES.put(clave, String(actual + 1), { expirationTtl: 3600 });
  return false;
}

async function sha256(valor) {
  const resumen = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(valor));
  return [...new Uint8Array(resumen)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

async function turnstileValido(env, token, ip) {
  if (typeof token !== 'string' || token.length < 10 || token.length > 2048) return false;

  const cuerpo = new FormData();
  cuerpo.append('secret', env.TURNSTILE_SECRET);
  cuerpo.append('response', token);
  if (ip) cuerpo.append('remoteip', ip);

  const respuesta = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST',
    body: cuerpo,
  });
  const resultado = await respuesta.json();
  return resultado.success === true;
}

async function crearIssue(env, campos) {
  const cuerpo = [
    '### Banco o aplicación',
    '',
    campos.entidad,
    '',
    '### Identificador de la app',
    '',
    '```text',
    campos.paquete,
    '```',
    '',
    '### Plantilla del aviso',
    '',
    '```text',
    campos.plantilla,
    '```',
    '',
    '### Qué operación es',
    '',
    campos.tipo,
    '',
    '---',
    '_Enviado desde el formulario de xtracto.app. Validado en el servidor: sin cifras._',
  ].join('\n');

  const respuesta = await fetch('https://api.github.com/repos/' + REPO + '/issues', {
    method: 'POST',
    headers: {
      Authorization: 'Bearer ' + env.GITHUB_TOKEN,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'xtracto-formato-worker',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: '[formato] ' + campos.entidad + ' · ' + campos.tipo,
      body: cuerpo,
      labels: ['formato', 'via-web'],
    }),
  });

  if (!respuesta.ok) return null;
  const issue = await respuesta.json();
  return issue.number || null;
}

// --- Respuestas -----------------------------------------------------------------------------
// Los errores devuelven un código corto, nunca un mensaje del sistema: quien sondee el endpoint no
// tiene por qué enterarse de en qué se atascó.

const CABECERAS = {
  'Access-Control-Allow-Origin': ORIGEN,
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
};

function preflight() {
  return new Response(null, {
    status: 204,
    headers: {
      ...CABECERAS,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    },
  });
}

function exito(estado, numero) {
  return new Response(JSON.stringify({ ok: true, estado, numero }), {
    status: 200,
    headers: CABECERAS,
  });
}

function error(codigo, motivo) {
  return new Response(JSON.stringify({ ok: false, motivo }), { status: codigo, headers: CABECERAS });
}
