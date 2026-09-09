# Xtracto — web

Sitio público de **Xtracto**, la app de gastos que lee los avisos del banco y no sale del móvil, y
punto de entrada de los formatos de aviso que envía la gente. Se publica en <https://xtracto.app>.

**El código de la app no está aquí.** Vive en el repositorio privado de al lado, `../xtracto`, y es
la fuente de verdad de tres cosas que esta web solo copia: la lista de bancos que el parser
interpreta, el `PRIVACY.md` y la hoja de ruta. Los hitos numerados del proyecto también son de allí
(`../xtracto/README.md` → *Plan de hitos*, y los 9 y 10 en `../xtracto/CLAUDE.md`).

## Empieza leyendo NOTAS-INTERNAS.md

Es el manual de operaciones y **lo primero que hay que abrir**: en qué estado está el sitio, los
hitos de la web, lo que está pendiente y de quién depende cada cosa, y el por qué de las decisiones
que no se adivinan leyendo el HTML.

**No está en git**, a propósito (`.gitignore`). Dos consecuencias: no se publica, y **un clon nuevo
no lo trae**. Si no está en el directorio, no lo reconstruyas de memoria: pídelo.

## Lo que no se edita a mano

Estas páginas son generadas. Editarlas directamente funciona hasta la próxima regeneración, que se
lo lleva todo sin avisar:

| Fichero | Lo genera | Con qué |
|---|---|---|
| `privacidad.html` | `construir.py` | el `PRIVACY.md` de `../xtracto` |
| `bancos.html`, `banks.html` | `bancos.py` | su lista `SOPORTADOS` |
| `novedades.html`, `roadmap.html` | `novedades.py` | sus listas `BLOQUES` y `VERSIONES` |
| `sitemap.xml` | `sitemap.py` | las páginas sin `noindex` |

**La barra de navegación está copiada en todas las páginas y dentro de esos tres generadores.** Si
la tocas, tócala en los tres y regenera. `verificar.py` comprueba que ninguna se quede atrás,
que es la única razón de que no se desincronicen.

**La hoja de ruta se traduce a mano desde `../xtracto`** (`README.md` → *Plan de hitos*, y
`CLAUDE.md`). Es la tercera cosa que esta web copia del repositorio de al lado, y como las otras
dos, allí manda. Las reglas para editarla —qué significa «Terminado», por qué no hay fechas— están
escritas en la cabecera de `novedades.py`.

## Antes de empujar

```bash
node worker/pruebas.mjs     # el Worker, con un KV y un GitHub de mentira
python3 verificar.py        # las invariantes del sitio
```

Las dos corren también en cada push (`.github/workflows/pruebas.yml`). **Cada comprobación de las
dos es un fallo que hemos tenido de verdad, no una manía**; si añades una, que sea por el mismo
motivo, y documenta cuál era el fallo.

## Publicar

**Empujar a `main` publica**, sin build y sin revisión: GitHub Pages sirve la rama. No hay otro
momento en el que alguien mire si el sitio sigue en pie, que es de donde viene lo de arriba.

```bash
python3 sitemap.py     # si han entrado o salido páginas
git push               # esto ya es publicar
python3 indexnow.py    # y ahora sí: valida la clave pidiéndola al dominio, así que nunca antes
```

**Google no participa en IndexNow** y no hay equivalente: se hace a mano en Search Console, URL por
URL, con «Solicitar indexación».

## Dos reglas de fondo

**Nada sale de xtracto.app.** Las tipografías se sirven desde aquí y no desde Google, la CSP de las
páginas de contenido es `default-src 'none'` sin `script-src`, y no hay analítica. No es una manía:
la portada afirma que la app no puede enviar tus datos a ningún sitio, y una web que pide las
tipografías a `fonts.gstatic.com` es la primera incoherencia que señalaría cualquiera que audite.
Eso también significa **cero JavaScript** en esas páginas; lo que parezca necesitarlo, se resuelve
con CSS o no se hace.

**No pedimos datos personales.** Antes de construir algo que recoja un dato, busca el diseño que no
lo recoja: por eso el alta de testers acabó siendo un `mailto:` que compone el mensaje en el
programa de correo de quien lo pulsa, en vez de un formulario que guardase su dirección aquí.
