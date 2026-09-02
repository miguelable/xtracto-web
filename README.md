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
| `formato.html`, `format.html` | Formulario de envío sin cuenta de GitHub, en español y en inglés |
| `formato.css`, `formato.js` | Los comparten las dos. Fuera de la página para poder prohibir el código en línea |
| `404.html` | Página de dirección inexistente. GitHub Pages la sirve sola |
| `estilo.css` | Los mismos tokens de diseño que la app |
| `fuentes/bajar.py` | Trae Manrope e IBM Plex Mono para servirlas desde aquí |
| `robots.txt` | Abre todo el sitio a los buscadores |
| `sitemap.py` | Regenera `sitemap.xml` leyendo las páginas y preguntándole las fechas a git |
| `construir.py` | Regenera `privacidad.html` desde el `PRIVACY.md` del repo de la app |
| `marca/generar.py` | Regenera la marca en todos sus tamaños — **el único sitio donde se edita** |
| `marca/tarjeta.py` | Regenera `og.png` y `og-en.png`, las tarjetas de los enlaces compartidos |
| `marca/`, `favicon.*`, `apple-touch-icon.png`, `og*.png` | Piezas generadas. No tocar a mano |

La política de privacidad tiene un solo original, el `PRIVACY.md` del proyecto de la app, para que
lo que dice el repositorio y lo que lee Google no puedan divergir. Tras editarlo:

```bash
python3 construir.py ../xtracto/PRIVACY.md
```

## La marca

La marca vive en `marca/generar.py` como geometría, no como imagen: cuatro cuadrados girados 45º
cuyas aristas interiores dejan justo el hueco del rombo central, más el destello. De ahí salen
todas las piezas, y por eso da igual el tamaño al que se pidan.

```bash
python3 marca/generar.py     # SVG siempre; los PNG y el .ico si hay cairosvg y pillow
```

| Pieza | Para qué |
|---|---|
| `marca/logo.svg` | La marca en la web, a 56 px en la portada |
| `favicon.svg` + `favicon.ico` | Pestaña del navegador. El `.ico` lleva 16, 32 y 48 dentro |
| `apple-touch-icon.png` | Cuando alguien añade la web a la pantalla de inicio en iOS |
| `marca/icono-app-frente.svg` + `marca/icono-app-fondo.svg` | Icono adaptativo de Android. Se importan con *Import Vector Asset* de Android Studio |
| `marca/icono-play-512.png` | El icono de 512×512 de la ficha de Google Play |
| `marca/icono-app-432.png` | Repuesto rasterizado por si el conversor a VectorDrawable se atraganta |
| `marca/original.png` | El diseño de partida, del que se midió la geometría. No se usa |

El icono de app va más pequeño dentro de su lienzo (65 %) porque Android recorta el icono adaptativo
con una máscara distinta según el lanzador y solo garantiza los 66 dp centrales de 108.

## Cuando alguien comparte un enlace

`og.png` y `og-en.png` son lo que se ve al pegar una dirección de xtracto.app en WhatsApp, Slack,
Mastodon o X. Se generan con la marca y la tipografía reales del sitio:

```bash
python3 marca/tarjeta.py     # se baja Manrope de Google Fonts a marca/.fuentes/ la primera vez
```

Las dos tarjetas llevan escrito **«En desarrollo»**. Un enlace compartido es lo primero que ve
mucha gente, y no queremos que lleguen a la web esperando un botón de descarga que aún no existe.

El sitemap tampoco se escribe a mano:

```bash
python3 sitemap.py
```

Entra toda página `.html` de la raíz **salvo** las que lleven `noindex`, y el `<lastmod>` sale de la
fecha del último commit que tocó cada fichero. Así marcar una página como no indexable la saca del
sitemap sin tocar nada más, y ninguna fecha se queda mintiendo por olvido.

Cada portada declara su `canonical`, sus `hreflang` y su tarjeta. Ojo con dos cosas al tocarlas:

- **`en.html` tiene que canonicalizar a sí misma**, no a `/`. Si apunta a la portada española,
  Google entiende que la inglesa es un duplicado y la deja fuera del índice.
- **`formato.html` no se bloquea en `robots.txt`** aunque no queramos que salga en buscadores.
  Lleva su propio `noindex`, y para leerlo un buscador tiene que poder entrar en la página.

## Nada sale de xtracto.app

La portada dice que la app no puede enviar tus datos a ningún sitio. La web tiene que poder decir lo
mismo de sí misma, y no podía: cargaba las tipografías de `fonts.gstatic.com`, que ve la IP de todo
el que abre la página. Era lo primero que iba a señalar cualquiera que se pusiese a auditarla.

```bash
python3 fuentes/bajar.py      # Manrope + IBM Plex Mono, subconjunto latin, 53 KB
```

Ahora **el único origen externo de todo el sitio es el captcha de Turnstile**, y solo en las dos
páginas del formulario. Cada página lo declara en su propia `Content-Security-Policy`, que en las
que no llevan formulario es tan estrecha como suena:

```
default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline';
font-src 'self'; base-uri 'none'; form-action 'none'
```

`'unsafe-inline'` en `style-src` está porque las páginas usan atributos `style=` a mano; el código
en línea sí está prohibido del todo, y por eso `formato.js` y `formato.css` viven fuera de la
página. GitHub Pages no deja poner cabeceras, así que la política va en un `<meta http-equiv>`: eso
descarta `frame-ancestors`, que solo funciona como cabecera de verdad.

> Lo único de todo esto que no he podido comprobar en un navegador es que Turnstile funcione bajo su
> CSP. La política sigue lo que Cloudflare documenta —`script-src` y `frame-src` hacia
> `challenges.cloudflare.com`— pero **conviene abrir el formulario con la consola delante la primera
> vez** y mirar que no salte ninguna violación.

### Accesibilidad

- `--text-3` era `#646A6E`: 3,53:1 sobre el fondo, cuando WCAG AA pide 4,5:1 para texto pequeño. Lo
  usaban los `h2` de sección, las etiquetas del formulario, las ayudas, el pie y el selector de
  idioma, o sea casi todo el texto pequeño. Ahora es `#7A8084`, 4,85:1.
- El foco de teclado se ve: un anillo de 2px con `:focus-visible`. Antes los campos hacían
  `outline:none` y solo cambiaba un borde de 1px que sobre fondo oscuro no se distingue.

## Recepción de formatos

Cuando la app no reconoce el aviso de un banco, ofrece compartir **la plantilla** del formato, ya sin
importes, fechas, comercios ni números. Esos envíos llegan aquí como *issues* con la plantilla de
`.github/ISSUE_TEMPLATE/formato-no-reconocido.yml`.

`.github/workflows/revisar-formato.yml` revisa cada uno automáticamente: **si detecta cualquier cifra
en la plantilla**, lo etiqueta como `revisar-datos` y pide a la persona que lo edite. Si está limpio,
lo etiqueta `formato-limpio` y da las gracias. Pedimos formas de frase, no gastos de nadie, y el
robot está para que eso se cumpla aunque alguien pegue el aviso en crudo por descuido.

## Formulario de envío sin registro

`formato.html` y `format.html` dejan enviar la plantilla de un aviso **sin cuenta de GitHub**.

> En la página inglesa, el `value` de cada tipo de operación **va en español**. El Worker valida
> contra una lista cerrada de valores en español y es el que acaba escribiendo el issue: traducir
> los `value` haría que se rechazara todo envío desde esa página.
 El formulario llama a
`https://api.xtracto.app/formato`, un Cloudflare Worker (`worker/`) que valida, filtra y crea el
issue con un token propio.

> **Por qué un subdominio y no `xtracto.app/api/`:** las rutas de Workers solo interceptan tráfico
> que pasa por el proxy de Cloudflare, y el dominio raíz está en «DNS only» para que GitHub Pages
> pueda emitir y renovar su certificado. `api.xtracto.app` se declara como `custom_domain` en
> `wrangler.toml` y Cloudflare le crea su propio registro proxificado y su certificado, sin tocar el
> DNS del sitio. Quien envía no ve GitHub en ningún momento.

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
