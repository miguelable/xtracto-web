#!/usr/bin/env python3
"""
Trae las tipografías del sitio para servirlas desde aquí, no desde Google.

El motivo no es la velocidad, aunque también: es que la portada dice que la app no puede enviar tus
datos a ningún sitio, y la propia página que lo decía pedía las tipografías a fonts.gstatic.com,
que ve la IP de todo el que la abre. Es la primera incoherencia que iba a señalar cualquiera que se
pusiese a auditar la web, y con razón.

Se baja solo el subconjunto `latin`: el sitio está en español y en inglés. Los caracteres que no
estén en la fuente (✓, ✕, ←) caen a la del sistema, igual que ya hacían antes.

    python3 fuentes/bajar.py

Las dos son SIL Open Font License 1.1; la licencia de cada una queda al lado del .woff2.
"""
import re
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
# Sin un User-Agent moderno, Google Fonts devuelve TTF en vez de WOFF2.
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

FAMILIAS = {
    'manrope.woff2': ('Manrope:wght@200..800', None),
    'ibm-plex-mono-400.woff2': ('IBM+Plex+Mono:wght@400', '400'),
    'ibm-plex-mono-500.woff2': ('IBM+Plex+Mono:wght@500', '500'),
}

LICENCIAS = {
    'manrope-OFL.txt': 'https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/OFL.txt',
    'ibm-plex-mono-OFL.txt':
        'https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/OFL.txt',
}


def pedir(url, ua=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA} if ua else {})
    return urllib.request.urlopen(req).read()


def url_latin(consulta):
    """De la hoja que devuelve Google, el @font-face del subconjunto `latin` y nada más."""
    css = pedir(f'https://fonts.googleapis.com/css2?family={consulta}&display=swap', ua=True)
    bloques = css.decode().split('/* ')
    for b in bloques:
        if b.startswith('latin */'):
            return re.search(r'src: url\((https://[^)]+\.woff2)\)', b).group(1)
    raise SystemExit(f'no encuentro el subconjunto latin de {consulta}')


def main():
    for nombre, (consulta, _) in FAMILIAS.items():
        datos = pedir(url_latin(consulta))
        (AQUI / nombre).write_bytes(datos)
        print(f'  {nombre}  {len(datos)/1024:.1f} KB')
    for nombre, url in LICENCIAS.items():
        (AQUI / nombre).write_bytes(pedir(url))
        print(f'  {nombre}')


if __name__ == '__main__':
    main()
