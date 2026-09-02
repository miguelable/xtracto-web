#!/usr/bin/env python3
"""
Genera la marca de Xtracto en todos los tamaños que hacen falta, desde una sola definición.

La marca original venía en un PNG de 520x479 con el dibujo ocupando 218 px y los bordes ya blandos
por el reescalado. En vez de recortarle el fondo, aquí está medida y rehecha en vector, así que da
igual el tamaño al que se pida.

Lo que hay detrás del dibujo, una vez medido:

  · Cuatro pétalos: cuadrados girados 45º, con el centro sobre las diagonales a distancia OFF del
    centro de la marca y semidiagonal H.
  · Las cuatro aristas interiores de los pétalos caen sobre las rectas |x|+|y| = 2·OFF - H. El
    rombo central no es un adorno puesto encima: es exactamente el hueco que dejan los pétalos.
  · Los pétalos solo se tocan por cuatro cuellos estrechos, a media altura de cada lado. Ese
    estrechamiento es lo que hace que se lea una X y no un aspa maciza.

El único número que me he separado del original es ese cuello: en el PNG mide 11 px de 216 y se
sostenía solo por el desenfoque. En vector, a 16 px, se rompería. Aquí va algo más ancho.

    python3 marca/generar.py          # SVG siempre; PNG e ICO si hay cairosvg y pillow

Todo se dibuja con <path> y con degradados en userSpaceOnUse, no con <rect transform>: así lo
importa sin quejarse tanto el conversor a VectorDrawable de Android Studio.
"""
import math
import sys
from pathlib import Path

# --- Geometría, en un lienzo de 96x96 con el centro en (48,48) --------------------------------
C = 48.0
EXTENSION = 45.0          # media anchura de la marca ya redondeada: deja 3 de margen
CUELLO = 4.2              # anchura del estrechamiento donde se tocan dos pétalos
RADIO = 3.6               # radio de las esquinas del pétalo

_CORTE = RADIO * (math.sqrt(2) - 1)                  # lo que el redondeo se come de cada punta
H = (EXTENSION + 2 * _CORTE + CUELLO / 2) / 2        # semidiagonal del pétalo
OFF = H - CUELLO / 2 - _CORTE                        # centro del pétalo sobre la diagonal
LADO = H * math.sqrt(2)                              # lado del cuadrado antes de girarlo
NUCLEO = (2 * OFF - H) * math.sqrt(2)                # lado del rombo central
NUCLEO_R = 18.5                                      # radio del degradado del núcleo

EST_RX, EST_RY, PINZA = 12.2, 13.5, 0.36             # el destello de cuatro puntas
HALO = 20.0                                          # desborda un poco sobre los pétalos

# De más oscuro a más claro: la luz entra por arriba a la derecha. La rampa va comprimida a
# propósito. Si el pétalo NE se acerca al brillo del núcleo los dos se funden en una mancha y la
# marca se ve descentrada aunque no lo esté.
PETALOS = [
    (-1,  1, '#0E7099'),   # SO, el más oscuro
    ( 1,  1, '#1787B5'),   # SE
    (-1, -1, '#1D96C6'),   # NO
    ( 1, -1, '#3FB4DD'),   # NE, el más claro
]

FONDO_APP = '#0A0E10'      # el mismo negro azulado que el fondo de la app y de la web


def _giro45(x, y):
    k = math.sqrt(2) / 2
    return (x - y) * k, (x + y) * k


def _petalo(cx, cy, lado, r):
    """Cuadrado redondeado girado 45º, como trazado absoluto."""
    m = lado / 2
    pasos = [('M', -m + r, -m), ('L', m - r, -m), ('A', m, -m + r), ('L', m, m - r),
             ('A', m - r, m), ('L', -m + r, m), ('A', -m, m - r), ('L', -m, -m + r),
             ('A', -m + r, -m)]
    d = []
    for paso in pasos:
        x, y = _giro45(paso[1], paso[2])
        x, y = cx + x, cy + y
        d.append(f'{paso[0]} {x:.2f} {y:.2f}' if paso[0] != 'A'
                 else f'A {r:.2f} {r:.2f} 0 0 1 {x:.2f} {y:.2f}')
    return ' '.join(d) + ' Z'


def _estrella(rx, ry, p):
    """Destello de cuatro puntas: los dos tirantes de cada tramo apuntan al centro, y eso es lo
    que hunde los lados hacia dentro y afila las puntas."""
    V = [(0, -ry), (rx, 0), (0, ry), (-rx, 0)]
    d = [f'M {C + V[0][0]:.2f} {C + V[0][1]:.2f}']
    for i in range(4):
        ax, ay = V[i]
        bx, by = V[(i + 1) % 4]
        d.append(f'C {C+ax*p:.2f} {C+ay*p:.2f} {C+bx*p:.2f} {C+by*p:.2f} {C+bx:.2f} {C+by:.2f}')
    return ' '.join(d) + ' Z'


def svg(escala=1.0, fondo=None, con_destello=True, pref='x', etiqueta='Xtracto'):
    k = escala
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" role="img" '
         f'aria-label="{etiqueta}">',
         f'<defs>'
         f'<radialGradient id="{pref}n" gradientUnits="userSpaceOnUse" '
         f'cx="{C}" cy="{C}" r="{NUCLEO_R*k:.2f}">'
         '<stop offset="0" stop-color="#F4FCFF"/>'
         '<stop offset=".5" stop-color="#B9E7F8"/>'
         '<stop offset="1" stop-color="#63BEE2"/></radialGradient>'
         f'<radialGradient id="{pref}h" gradientUnits="userSpaceOnUse" '
         f'cx="{C}" cy="{C}" r="{HALO*k:.2f}">'
         '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".38"/>'
         '<stop offset=".5" stop-color="#EAF9FF" stop-opacity=".15"/>'
         '<stop offset="1" stop-color="#EAF9FF" stop-opacity="0"/>'
         '</radialGradient></defs>']
    if fondo:
        p.append(f'<path fill="{fondo}" d="M0 0h96v96H0z"/>')
    for sx, sy, color in PETALOS:
        p.append(f'<path fill="{color}" d="'
                 + _petalo(C + sx*OFF*k, C + sy*OFF*k, LADO*k, RADIO*k) + '"/>')
    p.append(f'<path fill="url(#{pref}n)" d="' + _petalo(C, C, NUCLEO*k, 1.2*k) + '"/>')
    if con_destello:
        p.append(f'<circle cx="{C}" cy="{C}" r="{HALO*k:.2f}" fill="url(#{pref}h)"/>')
        p.append('<path fill="#FFFFFF" d="' + _estrella(EST_RX*k, EST_RY*k, PINZA) + '"/>')
    p.append('</svg>')
    return '\n'.join(p) + '\n'


# --- Salida ------------------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent

# La marca del icono de app va más pequeña dentro de su lienzo: Android recorta el icono adaptativo
# con máscaras distintas según el lanzador, y solo garantiza los 66 dp centrales de 108.
ESCALA_APP = 0.65
ESCALA_TILE = 0.75          # para los iconos con fondo propio (Apple, ficha de Play)

ARCHIVOS_SVG = {
    'marca/logo.svg':               dict(),
    'favicon.svg':                  dict(pref='f'),
    'marca/icono-app-frente.svg':   dict(escala=ESCALA_APP, pref='a'),
    'marca/icono-app-fondo.svg':    dict(escala=0, fondo=FONDO_APP, con_destello=False, pref='b'),
}

PNG = {   # ruta: (lado, escala, fondo)
    'apple-touch-icon.png':        (180, ESCALA_TILE, FONDO_APP),
    'marca/icono-play-512.png':    (512, ESCALA_TILE, FONDO_APP),
    'marca/icono-app-432.png':     (432, ESCALA_APP,  FONDO_APP),
}
ICO = [16, 32, 48]


def main():
    for ruta, kw in ARCHIVOS_SVG.items():
        if kw.get('escala') == 0:                    # capa de fondo: solo el color
            texto = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96">'
                     f'<path fill="{FONDO_APP}" d="M0 0h96v96H0z"/></svg>\n')
        else:
            texto = svg(**kw)
        (RAIZ / ruta).write_text(texto, encoding='utf-8')
        print(f'  {ruta}')

    try:
        import cairosvg
        from PIL import Image
    except ImportError:
        print('\nSin cairosvg/pillow: los PNG y el .ico no se han regenerado.')
        return

    import io
    def rasterizar(lado, escala, fondo):
        datos = cairosvg.svg2png(bytestring=svg(escala=escala, fondo=fondo).encode(),
                                 output_width=lado, output_height=lado)
        return Image.open(io.BytesIO(datos)).convert('RGBA' if fondo is None else 'RGB')

    for ruta, (lado, escala, fondo) in PNG.items():
        rasterizar(lado, escala, fondo).save(RAIZ / ruta)
        print(f'  {ruta}')

    # El .ico lleva varios tamaños dentro; el de 16 se dibuja aparte para que no salga de reducir
    # el de 48, que a ese tamaño se emborrona.
    capas = [rasterizar(s, 1.0, None) for s in ICO]
    capas[-1].save(RAIZ / 'favicon.ico', sizes=[(s, s) for s in ICO],
                   append_images=capas[:-1])
    print('  favicon.ico')


if __name__ == '__main__':
    sys.exit(main())
