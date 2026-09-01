# xtracto-web

Sitio público de **Xtracto** (la app de gastos que no sale del móvil) y punto de entrada de los
formatos de aviso que envía la gente.

El código de la aplicación **no está aquí**: vive en un repositorio privado. Este repo contiene solo
la web y la automatización de los envíos.

## Publicar en GitHub Pages

1. Ajustes del repositorio → **Pages** → *Source*: `Deploy from a branch`, rama `main`, carpeta `/`.
2. La web queda en **https://xtracto.app** (el fichero `CNAME` de la raíz fija el dominio;
   en Cloudflare hay que apuntar el DNS a las IPs de GitHub Pages **con el proxy desactivado**).
3. **https://xtracto.app/privacidad.html** es la URL de política de privacidad que va en Play Console.

## Ficheros

| Fichero | Qué es |
|---|---|
| `index.html` | Portada en español |
| `en.html` | Portada en inglés |
| `privacidad.html` | Política de privacidad — **generada**, no editar a mano |
| `estilo.css` | Los mismos tokens de diseño que la app |
| `construir.py` | Regenera `privacidad.html` desde el `PRIVACY.md` del repo de la app |

La política de privacidad tiene un solo original, el `PRIVACY.md` del proyecto de la app, para que
lo que dice el repositorio y lo que lee Google no puedan divergir. Tras editarlo:

```bash
python3 construir.py ../xtracto/PRIVACY.md
```

## Recepción de formatos

Cuando la app no reconoce el aviso de un banco, ofrece compartir **la plantilla** del formato, ya sin
importes, fechas, comercios ni números. Esos envíos llegan aquí como *issues* con la plantilla de
`.github/ISSUE_TEMPLATE/formato-no-reconocido.yml`.

`.github/workflows/revisar-formato.yml` revisa cada uno automáticamente: **si detecta cualquier cifra
en la plantilla**, lo etiqueta como `revisar-datos` y pide a la persona que lo edite. Si está limpio,
lo etiqueta `formato-limpio` y da las gracias. Pedimos formas de frase, no gastos de nadie, y el
robot está para que eso se cumpla aunque alguien pegue el aviso en crudo por descuido.

## Formulario de envío sin registro

`formato.html` deja enviar la plantilla de un aviso **sin cuenta de GitHub**. El formulario llama a
`https://xtracto.app/api/formato`, un Cloudflare Worker (`worker/`) que valida, filtra y crea el
issue con un token propio. Quien envía no ve GitHub en ningún momento.

### Defensas del endpoint

| Capa | Qué para |
|---|---|
| Solo POST + JSON + `Origin: https://xtracto.app` | Peticiones desde otros sitios y sondas |
| Corte por tamaño antes de `JSON.parse` | Cuerpos enormes contra el parser |
| Turnstile verificado en el servidor | Robots |
| Campo trampa oculto | Rellenadores automáticos |
| 5 envíos/hora por IP (hash con sal, caduca en 1 h) | Inundación |
| Validación estricta y longitudes máximas | Basura y campos inesperados |
| **Rechazo de cualquier dígito en la plantilla** | Datos personales, y de paso casi todo el spam |
| Saneado de acentos graves, arrobas y controles | Escapar del bloque de código, markdown, menciones |

La comprobación de cifras del navegador es solo comodidad: **la que cuenta es la del Worker**,
porque el JavaScript de una página lo puede saltar cualquiera.

### Desplegarlo

```bash
cd worker
npx wrangler kv namespace create LIMITES     # pega el id en wrangler.toml
npx wrangler secret put GITHUB_TOKEN         # token preciso: solo Issues:write en este repo
npx wrangler secret put TURNSTILE_SECRET     # clave secreta del widget
npx wrangler secret put SAL_IP               # cadena larga al azar
npx wrangler deploy
```

Y en `formato.html`, sustituir `PENDIENTE_CLAVE_PUBLICA_TURNSTILE` por la clave **pública** del
widget. Los secretos quedan cifrados en Cloudflare y nunca en el repositorio.
