#!/usr/bin/env python3
"""
Comprueba las invariantes del sitio.

    python3 verificar.py

Cada comprobación de aquí es un fallo que hemos tenido de verdad, no una manía. En orden de lo caro
que salió cada uno:

  · `en.html` canonicalizaba a la portada española. Google entiende con eso que la inglesa es un
    duplicado y la deja fuera del índice: la página existía y no la encontraba nadie.
  · `privacidad.html` se genera desde `construir.py`, y la cabecera de las dos puede separarse sin
    que nada chille. Cuando pasa, la política publicada pierde iconos, CSP o metadatos.
  · Las tipografías se sirven desde el propio sitio. Que vuelva a colarse una llamada a Google
    contradice lo que la portada afirma sobre la app.
  · Un enlace o una imagen rotos no rompen nada visiblemente, y por eso duran meses.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BASE = 'https://xtracto.app/'
NOINDEX = re.compile(r'<meta\s+name="robots"\s+content="[^"]*noindex', re.I)

fallos = []


def mal(comprobacion, detalle):
    fallos.append(f'{comprobacion}: {detalle}')


def paginas():
    return sorted(p.name for p in RAIZ.glob('*.html'))


def texto(nombre):
    return (RAIZ / nombre).read_text(encoding='utf-8')


def referencias_resuelven():
    for f in paginas() + ['estilo.css', 'formato.css']:
        t = texto(f)
        patron = r'(?:href|src)="([^"]+)"' if f.endswith('.html') else r"url\('([^']+)'\)"
        for r in re.findall(patron, t):
            if r.startswith(('http', '#', 'mailto', 'data:')):
                continue
            destino = r.split('#')[0].split('?')[0]
            if destino and not (RAIZ / destino).exists():
                mal('referencia rota', f'{f} apunta a {destino}, que no existe')


def canonicals_y_alternativas():
    """Toda página indexable tiene que canonicalizarse a sí misma. `en.html` apuntaba a la portada
    española y Google la tomaba por duplicada: la página existía y no la encontraba nadie."""
    for f in paginas():
        t = texto(f)
        if NOINDEX.search(t):
            continue
        suya = BASE if f == 'index.html' else BASE + f
        m = re.search(r'<link rel="canonical" href="([^"]+)"', t)
        if not m:
            mal('canonical', f'{f} no declara ninguno')
        elif m.group(1) != suya:
            mal('canonical', f'{f} apunta a {m.group(1)} y debería apuntar a sí misma, {suya}')

        # Si declara traducciones, que las declare completas: las tres o ninguna.
        idiomas = set(re.findall(r'<link rel="alternate" hreflang="([^"]+)"', t))
        if idiomas and idiomas != {'es', 'en', 'x-default'}:
            mal('hreflang', f'{f} declara {sorted(idiomas)} y faltan las demás')


def cabecera_de_la_politica():
    """La política es generada; su cabecera y la de su generador tienen que ser la misma."""
    fuente = re.search(r'CABECERA = """(.*?)"""', texto('construir.py'), re.S)
    if not fuente:
        return mal('política', 'no encuentro la CABECERA en construir.py')
    a = fuente.group(1).split('<h1')[0].strip()
    b = texto('privacidad.html').split('<h1')[0].strip()
    if a != b:
        mal('política', 'la cabecera de construir.py y la de privacidad.html han divergido; '
                        'regenérala con `python3 construir.py ../xtracto/PRIVACY.md`')


def sin_comentarios(t, css):
    """Los comentarios explican por qué NO usamos Google, y nombrarlo ahí no es una petición."""
    return re.sub(r'/\*.*?\*/', '', t, flags=re.S) if css else re.sub(r'<!--.*?-->', '', t, flags=re.S)


def nada_de_google():
    for f in paginas() + ['estilo.css', 'formato.css']:
        limpio = sin_comentarios(texto(f), f.endswith('.css'))
        if re.search(r'gstatic\.com|fonts\.googleapis\.com', limpio):
            mal('tipografías', f'{f} vuelve a pedirle algo a Google')


def todas_con_csp():
    for f in paginas():
        if 'http-equiv="Content-Security-Policy"' not in texto(f):
            mal('CSP', f'{f} no declara ninguna')


def json_ld_valido():
    for f in paginas():
        for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                 texto(f), re.S):
            try:
                json.loads(bloque)
            except json.JSONDecodeError as e:
                mal('JSON-LD', f'{f}: {e}')


def faq_coincide_con_la_pagina():
    """Declararle a Google preguntas que no están en la página es exactamente lo que trata como
    engaño. Se generan desde la misma fuente, pero nada impide que alguien edite solo una."""
    for f in paginas():
        t = texto(f)
        for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            try:
                grafo = json.loads(bloque).get('@graph', [])
            except json.JSONDecodeError:
                continue                      # ya lo canta json_ld_valido
            for nodo in grafo:
                if nodo.get('@type') != 'FAQPage':
                    continue
                visibles = set(re.findall(r'<h3>([^<]+\?)</h3>', t))
                for pregunta in (q['name'] for q in nodo['mainEntity']):
                    if pregunta not in visibles:
                        mal('FAQ', f'{f} declara «{pregunta}» y no está escrita en la página')


def sitemap_coherente():
    ruta = RAIZ / 'sitemap.xml'
    if not ruta.exists():
        return mal('sitemap', 'no existe; genéralo con `python3 sitemap.py`')
    try:
        arbol = ET.parse(ruta)
    except ET.ParseError as e:
        return mal('sitemap', f'XML inválido: {e}')

    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    listadas = {u.findtext(ns + 'loc') for u in arbol.getroot()}
    deberian = {BASE if f == 'index.html' else BASE + f
                for f in paginas() if not NOINDEX.search(texto(f))}
    if listadas != deberian:
        if deberian - listadas:
            mal('sitemap', f'faltan {sorted(deberian - listadas)}')
        if listadas - deberian:
            mal('sitemap', f'sobran (¿noindex?) {sorted(listadas - deberian)}')


def main():
    for comprobacion in (referencias_resuelven, canonicals_y_alternativas, cabecera_de_la_politica,
                         nada_de_google, todas_con_csp, json_ld_valido,
                         faq_coincide_con_la_pagina, sitemap_coherente):
        comprobacion()
        print(f'  · {comprobacion.__name__.replace("_", " ")}')
    if fallos:
        print('\n' + '\n'.join('  ✗ ' + f for f in fallos))
        print(f'\n{len(fallos)} problema(s)')
        return 1
    print('\ntodo en orden')
    return 0


if __name__ == '__main__':
    sys.exit(main())
