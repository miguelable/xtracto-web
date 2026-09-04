#!/usr/bin/env python3
"""
Prepara para la web las capturas de la app.

    python3 capturas/preparar.py [carpeta de origen]

**El original no vive aquí.** Las capturas se hacen para la ficha de Google Play, con el
procedimiento que documenta `PLAY.md` en el repositorio de la app, y por defecto se quedan en
`Documents/xtracto-capturas`. Este script solo trae a la web las de teléfono, las encoge y las pasa
a WebP. Si cambian las de Play, se vuelve a ejecutar y ya está: aquí no se retoca ninguna a mano.

Tres cosas que conviene saber antes de tocar esto:

  · **Los datos son inventados.** Salen de `tools/generar_demo.py` y se siembran en un emulador. No
    se hacen sobre el teléfono del autor porque ahí hay dinero real: comercios de verdad y los cuatro
    dígitos de tarjetas de verdad, que acabarían en una página pública.
  · **Solo las de teléfono.** Las de tablet existen, pero hoy el contenido va limitado a 640dp
    centrados y en una pantalla de 1280dp media captura sale vacía. Entran cuando el hito 10 llene
    ese hueco.
  · **WebP y no PNG.** La misma captura a 480 px de ancho ocupa 25 KB en WebP y 107 en PNG. Con
    cuatro por portada la diferencia es de 100 KB contra 430, y este sitio presume de ser ligero.
"""
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit('Hace falta Pillow: pip install pillow')

AQUI = Path(__file__).resolve().parent
ORIGEN = Path('/mnt/c/Users/ORDENADOR 19/Documents/xtracto-capturas')

# Se sirven al doble del tamaño al que se ven (~240 px), para que se vean nítidas en pantallas de
# densidad doble, que son todas las de un móvil.
ANCHO = 480
CALIDAD = 88

# (fichero de origen sin el idioma, nombre en la web)
PANTALLAS = [('1-resumen', 'resumen'), ('2-movimientos', 'movimientos'),
             ('3-capturas', 'capturas'), ('4-ajustes', 'ajustes')]
IDIOMAS = {'es-ES': 'es', 'en-US': 'en'}


def main():
    origen = Path(sys.argv[1]) if len(sys.argv) > 1 else ORIGEN
    if not origen.is_dir():
        sys.exit(f'No encuentro las capturas en {origen}.\n'
                 'Se hacen con el procedimiento de PLAY.md, en un emulador y con datos inventados.\n'
                 'Si están en otro sitio, pásame la carpeta como argumento.')

    faltan = []
    for sufijo, nombre in PANTALLAS:
        for locale, idioma in IDIOMAS.items():
            fuente = origen / f'telefono-{locale}-{sufijo}.png'
            if not fuente.exists():
                faltan.append(fuente.name)
                continue
            imagen = Image.open(fuente)
            alto = round(imagen.height * ANCHO / imagen.width)
            destino = AQUI / f'{nombre}-{idioma}.webp'
            imagen.resize((ANCHO, alto), Image.LANCZOS).save(
                destino, quality=CALIDAD, method=6)
            print(f'  {destino.name}  {ANCHO}×{alto}  {destino.stat().st_size // 1024} KB')

    if faltan:
        # No se para: lo que haya, se prepara. Pero que se vea qué falta, porque una portada con
        # tres capturas de cuatro no chilla sola.
        print('\nNo estaban: ' + ', '.join(faltan))
        return 1
    print(f'\nRecuerda el `alt` de cada una en las portadas: describe la pantalla, no la repitas.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
