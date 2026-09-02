#!/usr/bin/env python3
"""
Genera `privacidad.html` a partir del PRIVACY.md del proyecto de la app.

La política de privacidad tiene que decir exactamente lo mismo en el repositorio del código y en la
web que Google Play va a mirar. Manteniendo un solo original y generando la página, no pueden
divergir. Ejecuta esto cada vez que cambies PRIVACY.md.

    python3 construir.py ../xtracto/PRIVACY.md
"""
import html
import re
import sys
from pathlib import Path

CABECERA = """<!doctype html>
<!-- Generado por construir.py desde el PRIVACY.md del repositorio de la app.
     No editar a mano: al regenerarlo se pierde lo que cambies aquí. -->
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; base-uri 'none'; form-action 'none'">
<title>Política de privacidad — Xtracto</title>
<meta name="robots" content="index">
<link rel="canonical" href="https://xtracto.app/privacidad.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Xtracto">
<meta property="og:url" content="https://xtracto.app/privacidad.html">
<meta property="og:title" content="Política de privacidad — Xtracto">
<meta property="og:description" content="Xtracto no recoge, no transmite y no comparte ningún dato personal. Todo se queda en el teléfono.">
<meta property="og:image" content="https://xtracto.app/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preload" href="fuentes/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<div class="envoltorio" style="padding-top:40px;padding-bottom:64px">
<div class="idiomas" style="padding-top:0"><a href="#es">Español</a> · <a href="#en">English</a></div>
<p><a href="index.html">&larr; Xtracto</a></p>
"""

PIE = """</div>
</body>
</html>
"""


def en_linea(texto: str) -> str:
    texto = html.escape(texto)
    # El código se aparta antes que nada: si no, un identificador como
    # BIND_NOTIFICATION_LISTENER_SERVICE se convierte en cursivas por sus guiones bajos.
    codigos: list[str] = []

    def apartar(match: re.Match) -> str:
        codigos.append(match.group(1))
        return f"\x00{len(codigos) - 1}\x00"

    texto = re.sub(r"`([^`]+)`", apartar, texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"_([^_]+)_", r"<em>\1</em>", texto)
    for i, codigo in enumerate(codigos):
        texto = texto.replace(f"\x00{i}\x00", f"<code>{codigo}</code>")
    return texto


# La política lleva la versión española y a continuación la inglesa, cada una bajo su propio `# `.
# Numerar los <h1> en ese orden da un ancla estable a la que enlazar desde las páginas en inglés,
# sin depender de cómo esté redactado el titular.
IDIOMAS = ["es", "en"]


def convertir(markdown: str) -> str:
    salida, tabla, parrafo, lista, cita = [], [], [], False, False
    titulos = 0

    def volcar_parrafo():
        # El markdown va con saltos de línea duros a los 100 caracteres. Sin unirlos, cada línea
        # saldría como un párrafo suelto y las negritas partidas en dos líneas no cerrarían.
        if parrafo:
            salida.append(f"<p>{en_linea(' '.join(parrafo))}</p>")
            parrafo.clear()

    def cerrar():
        nonlocal lista, cita
        volcar_parrafo()
        if lista:
            salida.append("</ul>")
            lista = False
        if cita:
            salida.append("</blockquote>")
            cita = False

    def volcar_tabla():
        if not tabla:
            return
        salida.append('<table style="width:100%;border-collapse:collapse">')
        for i, fila in enumerate(tabla):
            if set(fila.replace("|", "").strip()) <= set("-: "):
                continue
            celdas = [c.strip() for c in fila.strip().strip("|").split("|")]
            etiqueta = "th" if i == 0 else "td"
            estilo = 'style="text-align:left;padding:8px 10px;border-bottom:1px solid var(--border)"'
            salida.append("<tr>" + "".join(
                f"<{etiqueta} {estilo}>{en_linea(c)}</{etiqueta}>" for c in celdas) + "</tr>")
        salida.append("</table>")
        tabla.clear()

    for linea in markdown.splitlines():
        cruda = linea.rstrip()
        if cruda.startswith("|"):
            volcar_parrafo()
            tabla.append(cruda)
            continue
        volcar_tabla()

        if not cruda.strip():
            cerrar()
        elif cruda.startswith("# "):
            cerrar()
            ancla = IDIOMAS[titulos] if titulos < len(IDIOMAS) else f"parte-{titulos + 1}"
            titulos += 1
            salida.append(f"<h1 id='{ancla}' style='font-size:32px'>{en_linea(cruda[2:])}</h1>")
        elif cruda.startswith("## "):
            cerrar()
            salida.append(f"<h3 style='margin-top:34px'>{en_linea(cruda[3:])}</h3>")
        elif cruda.startswith("- "):
            volcar_parrafo()
            if not lista:
                salida.append('<ul style="color:var(--text-2)">')
                lista = True
            salida.append(f"<li>{en_linea(cruda[2:])}</li>")
        elif cruda.startswith("> "):
            volcar_parrafo()
            if not cita:
                salida.append('<blockquote style="border-left:3px solid var(--accent);'
                              'margin:0;padding:4px 16px;color:var(--text-2)">')
                cita = True
            salida.append(f"<p>{en_linea(cruda[2:])}</p>")
        elif cruda.startswith("---"):
            cerrar()
            salida.append('<hr style="border:0;border-top:1px solid var(--border);margin:48px 0">')
        else:
            if lista or cita:
                cerrar()
            parrafo.append(cruda.strip())

    volcar_tabla()
    cerrar()
    return "\n".join(salida)


if __name__ == "__main__":
    origen = Path(sys.argv[1] if len(sys.argv) > 1 else "../xtracto/PRIVACY.md")
    destino = Path("privacidad.html")
    destino.write_text(CABECERA + convertir(origen.read_text(encoding="utf-8")) + PIE,
                       encoding="utf-8")
    print(f"{destino} generado desde {origen}")
