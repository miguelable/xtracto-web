#!/usr/bin/env python3
"""
Genera `sitemap.xml` mirando las páginas que hay y preguntándole a git cuándo cambió cada una.

Existe para no tener que acordarse de nada. Antes el `<lastmod>` estaba escrito a mano, y una fecha
escrita a mano en un sitemap solo tiene dos estados: recién puesta, o mintiendo.

Tres reglas, y las tres se deducen solas del propio sitio:

  · Entra toda página .html de la raíz **salvo** las que llevan `<meta name="robots" content=
    "noindex">`. Así, marcar una página como no indexable la saca del sitemap sin tocar este
    fichero: la decisión vive en un solo sitio, la página.
  · El `<lastmod>` sale de la fecha del último commit que tocó el fichero. Si el fichero tiene
    cambios sin commitear —que es lo normal, porque esto se ejecuta justo antes de commitear— se
    usa la fecha de hoy.
  · Las traducciones (`<xhtml:link hreflang=...>`) salen de **las que declara cada página en su
    propio `<head>`**, tal cual. Antes eran una lista escrita aquí a mano, y se quedó atrás: tenía
    dos parejas de las seis que hay, así que `bancos`/`banks`, `sin-conectar-el-banco`/
    `without-linking-your-bank`, `prueba-cerrada`/`closed-test` y `novedades`/`roadmap` salían en el
    sitemap como si fueran páginas sueltas sin versión en el otro idioma. Nada chillaba, porque las
    páginas sí declaraban su terna: solo el sitemap decía otra cosa. Leyéndola de la página no se
    puede volver a separar, y una pareja nueva entra sola. Que la terna esté completa —`es`, `en` y
    `x-default`, las tres o ninguna— ya lo comprueba `verificar.py`.

    python3 sitemap.py
"""
import datetime
import re
import subprocess
import sys
from pathlib import Path

BASE = 'https://xtracto.app/'
RAIZ = Path(__file__).resolve().parent

NOINDEX = re.compile(r'<meta\s+name="robots"\s+content="[^"]*noindex', re.I)
ALTERNATIVA = re.compile(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">')


def url(fichero):
    return BASE if fichero == 'index.html' else BASE + fichero


def git(*args):
    try:
        return subprocess.run(['git', *args], cwd=RAIZ, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ''


def ultima_fecha(fichero):
    hoy = datetime.date.today().isoformat()
    if git('status', '--porcelain', '--', fichero):
        return hoy                                    # sin commitear: se está tocando ahora
    return git('log', '-1', '--format=%cs', '--', fichero) or hoy


def paginas():
    # La portada primero, que es la que importa; el resto por orden alfabético.
    for f in sorted((p.name for p in RAIZ.glob('*.html')), key=lambda f: (f != 'index.html', f)):
        if NOINDEX.search((RAIZ / f).read_text(encoding='utf-8')):
            print(f'  - {f} (noindex, fuera)')
            continue
        yield f


def alternativas(fichero):
    """Las traducciones que la propia página declara en su `<head>`, en su mismo orden.

    Se copian tal cual, incluida la que apunta a la página misma: el sitemap las quiere todas en
    cada entrada, no solo las de los otros idiomas. Una página sin `hreflang` —`privacidad.html`,
    que es bilingüe en un solo fichero y se reparte con `#es` / `#en`— no declara ninguna y aquí no
    sale ninguna, que es lo correcto.
    """
    return [f'<xhtml:link rel="alternate" hreflang="{idioma}" href="{destino}"/>'
            for idioma, destino in ALTERNATIVA.findall((RAIZ / fichero).read_text(encoding='utf-8'))]


def main():
    lineas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<!-- Generado por sitemap.py. No editar a mano: se regenera y te lo pisa. -->',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
              '        xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for f in paginas():
        fecha = ultima_fecha(f)
        print(f'  + {f}  {fecha}')
        lineas.append('  <url>')
        lineas.append(f'    <loc>{url(f)}</loc>')
        lineas += ['    ' + a for a in alternativas(f)]
        lineas.append(f'    <lastmod>{fecha}</lastmod>')
        lineas.append('  </url>')
    lineas.append('</urlset>')
    (RAIZ / 'sitemap.xml').write_text('\n'.join(lineas) + '\n', encoding='utf-8')
    print('sitemap.xml generado')


if __name__ == '__main__':
    sys.exit(main())
