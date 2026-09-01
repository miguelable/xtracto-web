# xtracto-web

Sitio público de **Xtracto** (la app de gastos que no sale del móvil) y punto de entrada de los
formatos de aviso que envía la gente.

El código de la aplicación **no está aquí**: vive en un repositorio privado. Este repo contiene solo
la web y la automatización de los envíos.

## Publicar en GitHub Pages

1. Ajustes del repositorio → **Pages** → *Source*: `Deploy from a branch`, rama `main`, carpeta `/`.
2. La web queda en `https://miguelable.github.io/xtracto-web/`.
3. Esa dirección, con `/privacidad.html` al final, es la **URL de política de privacidad** que hay
   que meter en Play Console.

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
