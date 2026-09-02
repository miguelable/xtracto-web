#!/usr/bin/env python3
"""
Avisa a los buscadores de que hay páginas nuevas o cambiadas, sin esperar a que pasen a mirar.

Bing decía «Discovered but not crawled»: conocía las URLs por el sitemap pero no había ido a por
ellas. En un dominio nuevo y sin enlaces que apunten a él eso es normal —es la cola de rastreo, no
un error—, y IndexNow es el canal por el que Bing acepta que le avises tú. Lo comparten Bing,
Yandex, Naver y Seznam; **Google no participa**, y para Google no hay atajo equivalente: se hace en
Search Console, a mano, con «Solicitar indexación».

    python3 indexnow.py

Las URLs salen de sitemap.xml, así que primero genera el sitemap y publica los cambios: IndexNow
comprueba la clave pidiendo https://xtracto.app/<clave>.txt, y avisar de una página que todavía no
está publicada es peor que no avisar.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DOMINIO = 'xtracto.app'
CLAVE = '3a7eeee427302c904f5ea9bc83ebc4a9'
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def main():
    fichero = RAIZ / f'{CLAVE}.txt'
    if not fichero.exists():
        print(f'Falta {fichero.name}. IndexNow no acepta un aviso si no puede leer esa clave '
              f'en https://{DOMINIO}/{CLAVE}.txt')
        return 1

    urls = [u.findtext(NS + 'loc') for u in ET.parse(RAIZ / 'sitemap.xml').getroot()]
    cuerpo = json.dumps({
        'host': DOMINIO,
        'key': CLAVE,
        'keyLocation': f'https://{DOMINIO}/{CLAVE}.txt',
        'urlList': urls,
    }).encode()

    peticion = urllib.request.Request('https://api.indexnow.org/indexnow', data=cuerpo,
                                      headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(peticion) as respuesta:
        codigo = respuesta.status
    # 200 es aceptado; 202 es aceptado y pendiente de comprobar la clave. Los dos están bien.
    print(f'{codigo} · avisadas {len(urls)} URL:')
    for u in urls:
        print(f'  {u}')
    return 0 if codigo in (200, 202) else 1


if __name__ == '__main__':
    sys.exit(main())
