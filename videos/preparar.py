#!/usr/bin/env python3
"""
Prepara para la web los vídeos de la app, y saca el cartel de cada uno.

    python3 videos/preparar.py [carpeta de origen]

**El original no vive aquí**, igual que con las capturas: se graba aparte y por defecto se queda en
`Documents/xtracto-video`. Este script trae los cuatro a la web, los escala, los recomprime y les
saca el fotograma que se ve antes de darle al play. Aquí no se retoca ninguno a mano.

Los originales son grabaciones de pantalla de Android: H.264, **sin pista de audio** —las otras dos
pistas del contenedor son metadatos de la grabadora— y de 7 a 12 MB por vídeo. Eso último es el
motivo entero de que este script exista: son ~100 veces el fichero más pesado que servía este sitio.

Cuatro decisiones que conviene no deshacer sin pensarlo:

  · **Los datos son inventados**, del mismo emulador y la misma sesión que las capturas: el resumen
    del vídeo dice 489,32 € en 23 gastos, que es exactamente lo que dice `capturas/resumen-es.webp`.
    No se graba sobre el teléfono del autor porque ahí hay dinero real, comercios de verdad y
    cuatro dígitos de tarjetas de verdad. Es la misma regla que en `capturas/preparar.py`, y aquí
    importa más: un vídeo enseña muchas más pantallas que una captura.
  · **Se escala a lo que se ve, no a lo que se grabó.** El vertical se sirve a 540 px de ancho para
    verse a ~300 css px en pantallas de densidad doble; el apaisado a 1280 para los 732 px que mide
    el cuerpo del sitio. Servir los 1080 y los 1920 originales sería pagar cuatro veces los píxeles
    para tirarlos en el navegador.
  · **`-map 0:v:0` y nada más.** Se queda solo la pista de vídeo: no hay audio que conservar y las
    pistas de metadatos de la grabadora no pintan nada en una página.
  · **`+faststart`.** Mueve el índice del MP4 al principio. Sin eso el navegador tiene que
    descargarse el fichero entero antes de pintar el primer fotograma, que con `preload="none"` es
    justo lo que se nota: el usuario pulsa play y no pasa nada durante segundos.

**El recorte está sin usar a propósito.** Los originales duran de 95 a 110 s, que es largo, pero
cortarlos requiere saber qué se enseña en cada tramo y eso no se puede decidir desde aquí. Si
quieres acortarlos, pon los segundos en `RECORTE` del vídeo que sea y vuelve a ejecutar.
"""
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ORIGEN = Path('/mnt/c/Users/ginar/Documents/xtracto-video')

# Calidad constante. 28 es el punto en el que una grabación de pantalla —colores planos, texto
# nítido, poco movimiento— deja de perder legibilidad en los importes, que es lo único que hay que
# poder leer. Bajarlo engorda el fichero sin que se note; subirlo emborrona las cifras.
CRF = 28
FPS = 30            # tope, no forzado hacia arriba: si el original va a 30 se queda como está.
# Más bajo que el 88 de las capturas, y con motivo: el cartel se ve **detrás de un botón de play** y
# encima escalado hacia abajo (el de tablet mide 1280 y se pinta a 732), así que no necesita calidad
# de captura. Medido sobre el fotograma con más texto pequeño —el top de comercios—: del 88 al 72 no
# se distingue ni ampliando al 200 %, y los dos carteles de un idioma bajan de 88 KB a 65. Por
# debajo de 72 se deja de ganar: el 64 solo quita otros 4 KB.
CALIDAD_CARTEL = 72

# (fichero de origen, nombre en la web, ancho, alto, segundo del que sale el cartel)
#
# Los tamaños son fracciones exactas del original —la mitad del vertical, dos tercios del
# apaisado— para que el escalado no invente píxeles intermedios en el texto.
#
# El segundo del cartel es el fotograma que se ve antes de pulsar play, así que tiene que ser una
# pantalla que se entienda sola: el resumen, no una transición a medias.
VIDEOS = [
    ('xtracto-movil-es.mp4',  'movil-es',   540, 1200, 2),
    ('xtracto-movil-en.mp4',  'movil-en',   540, 1200, 2),
    ('xtracto-tablet-es.mp4', 'tablet-es', 1280,  800, 2),
    ('xtracto-tablet-en.mp4', 'tablet-en', 1280,  800, 2),
]

# Segundos (desde, hasta) para acortar un vídeo. Ver la nota de la cabecera: vacío = entero.
RECORTE: dict[str, tuple[float, float]] = {}


# Donde winget deja el ffmpeg de Gyan. Se mira **después** del PATH, y está aquí escrito porque el
# PATH de WSL se hereda de Windows al arrancar la distribución: si instalas ffmpeg con winget
# mientras WSL ya está en marcha, aquí no aparece hasta un `wsl --shutdown`. Con esto no hace falta.
# Ojo: en esta máquina winget lo dejó bajo el usuario «ORDENADOR 19», no bajo «ginar», que es donde
# están los vídeos.
WINGET = (Path('/mnt/c/Users/ORDENADOR 19/AppData/Local/Microsoft/WinGet/Packages')
          / 'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe'
          / 'ffmpeg-9.0.1-full_build/bin/ffmpeg.exe')


def buscar_ffmpeg():
    """`ffmpeg` de Linux si está; si no, el de Windows, que es lo normal en esta máquina.

    Si acaba usándose el de Windows hay que darle rutas de Windows: un `/mnt/c/...` no lo entiende,
    y falla con un «No such file or directory» que no dice por qué.
    """
    for nombre in ('ffmpeg', 'ffmpeg.exe'):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta, nombre.endswith('.exe')
    if WINGET.exists():
        return str(WINGET), True
    # Por si la versión cambia con una actualización de winget: el nombre de la carpeta la lleva.
    for otro in sorted(WINGET.parent.parent.glob('Gyan.FFmpeg*/*/bin/ffmpeg.exe'), reverse=True):
        return str(otro), True
    return None, False


def ruta_para(p, es_windows):
    if not es_windows:
        return str(p)
    return subprocess.run(['wslpath', '-w', str(p)],
                          capture_output=True, text=True, check=True).stdout.strip()


def correr(orden):
    r = subprocess.run(orden, capture_output=True, text=True)
    if r.returncode:
        # ffmpeg cuenta el motivo real en las últimas líneas de stderr, no en la primera.
        sys.exit('ffmpeg falló:\n' + '\n'.join(r.stderr.strip().splitlines()[-6:]))


def main():
    ffmpeg, es_windows = buscar_ffmpeg()
    if not ffmpeg:
        print('No encuentro ffmpeg, y sin él esto no puede hacer nada.\n\n'
              'En Windows:  winget install Gyan.FFmpeg\n'
              'En WSL:      sudo apt install ffmpeg\n\n'
              'Los originales pesan de 7 a 12 MB y duran minuto y medio; publicarlos tal cual\n'
              'serían 38 MB metidos en git para siempre, así que este paso no es opcional.')
        return 1

    origen = Path(sys.argv[1]) if len(sys.argv) > 1 else ORIGEN
    if not origen.is_dir():
        return print(f'No existe la carpeta de origen: {origen}') or 1

    faltan = [v[0] for v in VIDEOS if not (origen / v[0]).exists()]
    if faltan:
        return print(f'Faltan en {origen}: {", ".join(faltan)}') or 1

    print(f'ffmpeg: {ffmpeg}\norigen: {origen}\n')
    for fuente, nombre, ancho, alto, segundo in VIDEOS:
        entrada = origen / fuente
        salida = AQUI / f'{nombre}.mp4'
        cartel = AQUI / f'cartel-{nombre}.webp'

        recorte = []
        if nombre in RECORTE:
            desde, hasta = RECORTE[nombre]
            recorte = ['-ss', str(desde), '-to', str(hasta)]

        correr([ffmpeg, '-y', '-loglevel', 'error', *recorte,
                '-i', ruta_para(entrada, es_windows),
                '-map', '0:v:0',                     # solo vídeo: ni audio ni metadatos
                '-vf', f'scale={ancho}:{alto}:flags=lanczos',
                '-r', str(FPS),
                '-c:v', 'libx264', '-preset', 'slow', '-crf', str(CRF),
                '-profile:v', 'high', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                ruta_para(salida, es_windows)])

        # El cartel sale del vídeo ya escalado, no del original: así es exactamente el fotograma
        # que el navegador va a pintar encima cuando arranque, y no se ve un salto al pulsar play.
        correr([ffmpeg, '-y', '-loglevel', 'error',
                '-ss', str(segundo), '-i', ruta_para(salida, es_windows),
                '-frames:v', '1', '-c:v', 'libwebp', '-quality', str(CALIDAD_CARTEL),
                ruta_para(cartel, es_windows)])

        antes = entrada.stat().st_size / 1048576
        print(f'  {salida.name:15} {ancho}×{alto}  '
              f'{antes:5.1f} MB → {salida.stat().st_size / 1048576:4.1f} MB   '
              f'cartel {cartel.stat().st_size / 1024:.0f} KB')

    total = sum((AQUI / f'{v[1]}.mp4').stat().st_size for v in VIDEOS) / 1048576
    print(f'\n{total:.1f} MB en total.\n\n'
          'Recuerda que las páginas que lleven vídeo necesitan `media-src \'self\'` en su CSP:\n'
          'sin eso el navegador lo bloquea sin decir nada visible.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
