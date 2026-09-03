#!/usr/bin/env python3
"""
Genera las imágenes promocionales de Xtracto:

  · Las tarjetas que se ven al pegar un enlace de xtracto.app en WhatsApp, Slack, Mastodon o X.
  · El **gráfico de la ficha de Google Play**, de 1024x500, en los dos idiomas.

Va aparte de `generar.py` porque necesita dos cosas que la marca no necesita: red, para bajarse
Manrope, y pillow. La fuente se guarda en `marca/.fuentes/`, que está en el .gitignore: es de
Google Fonts, no hace falta versionarla aquí.

    python3 marca/tarjeta.py

La tarjeta dice «En desarrollo» a propósito. Un enlace compartido es lo primero que ve mucha gente,
y no queremos que llegue a la web esperando un botón de descarga que todavía no existe. El gráfico
de Play **no** lo dice: ahí la app ya está publicada.
"""
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = Path(__file__).resolve().parent / '.fuentes'
URL_MANROPE = ('https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/'
               'Manrope%5Bwght%5D.ttf')

ANCHO, ALTO, MARGEN = 1200, 630, 76
FONDO, TEXTO_1, TEXTO_2, TEXTO_3 = '#0A0E10', '#ECEFF1', '#999FA4', '#646A6E'
ACENTO, AVISO = '#3FB4DD', '#E6AC3D'
TRACK = 1.1              # el mismo espaciado de letra que las mayúsculas del sitio

TARJETAS = {
    'og.png': dict(
        estado='EN DESARROLLO',
        titular=['Tus gastos se apuntan solos.', 'Y no salen del móvil.'],
        pie='Sin permiso de acceso a internet. No es una política, es una limitación técnica.'),
    'og-en.png': dict(
        estado='IN DEVELOPMENT',
        titular=['Your spending records itself.', 'And never leaves your phone.'],
        pie='No internet permission. Not a policy — a technical limitation.'),
}


def manrope(tam, peso=800):
    FUENTES.mkdir(exist_ok=True)
    ttf = FUENTES / 'Manrope.ttf'
    if not ttf.exists():
        print('  bajando Manrope de Google Fonts…')
        ttf.write_bytes(urllib.request.urlopen(URL_MANROPE).read())
    f = ImageFont.truetype(str(ttf), tam)
    f.set_variation_by_axes([peso])
    return f


def ancho(d, texto, fuente, track=0):
    if track:
        return sum(d.textbbox((0, 0), c, font=fuente)[2] + track for c in texto) - track
    return d.textbbox((0, 0), texto, font=fuente)[2]


def texto_track(d, xy, texto, fuente, fill, track):
    """Pillow no sabe de letter-spacing, y el sitio escribe las mayúsculas espaciadas. Se dibuja
    letra a letra."""
    x, y = xy
    for c in texto:
        d.text((x, y), c, font=fuente, fill=fill)
        x += d.textbbox((0, 0), c, font=fuente)[2] + track


def ajustar(d, lineas, limite, tam, peso=800):
    """Baja el cuerpo hasta que la línea más larga entra. Más fiable que calcularlo a ojo: si
    mañana cambia el titular, la tarjeta sigue saliendo bien sin tocar nada."""
    while tam > 24:
        f = manrope(tam, peso)
        if max(ancho(d, l, f) for l in lineas) <= limite:
            return f, tam
        tam -= 2
    return manrope(tam, peso), tam


def tarjeta(estado, titular, pie, marca):
    im = Image.new('RGB', (ANCHO, ALTO), FONDO)
    d = ImageDraw.Draw(im)

    # La marca entera a la derecha, sin sangrar: hay clientes que recortan la tarjeta y no
    # conviene que se lleven por delante un pétalo.
    lado = 340
    m = marca.resize((lado, lado), Image.LANCZOS)
    im.paste(m, (ANCHO - MARGEN - lado, (ALTO - lado) // 2), m)

    columna = ANCHO - MARGEN - lado - 56
    y = MARGEN

    f = manrope(38)
    d.text((MARGEN, y), 'Xtracto', font=f, fill=TEXTO_1)
    y += 62

    # Chip de estado, igual que el de la portada.
    f = manrope(17, 700)
    tw = ancho(d, estado, f, TRACK)
    d.rounded_rectangle([MARGEN, y, MARGEN + tw + 44, y + 34], radius=17,
                        fill='#1C1810', outline='#5C4A22')
    d.ellipse([MARGEN + 15, y + 14, MARGEN + 22, y + 21], fill=AVISO)
    texto_track(d, (MARGEN + 30, y + 8), estado, f, AVISO, TRACK)
    tope = y + 34

    # El titular se centra en la banda que queda entre el chip y el pie, no cuelga del chip: si no,
    # la tarjeta sale con toda la tinta arriba y un hueco muerto abajo.
    f, tam = ajustar(d, titular, columna - MARGEN, 60)
    alto_bloque = int(tam * 1.22) * len(titular)
    y = tope + (ALTO - MARGEN - 60 - tope - alto_bloque) // 2
    for i, linea in enumerate(titular):
        d.text((MARGEN, y), linea, font=f, fill=TEXTO_1 if i == 0 else ACENTO)
        y += int(tam * 1.22)

    f = manrope(21, 500)
    d.text((MARGEN, ALTO - MARGEN - 26), pie, font=f, fill=TEXTO_2)
    return im


# --- Gráfico de la ficha de Google Play --------------------------------------------------------

# 1024x500 exactos, y sin canal alfa: Play rechaza el PNG con transparencia.
ANCHO_PLAY, ALTO_PLAY = 1024, 500

# Play recorta este gráfico a proporciones distintas según dónde lo enseñe, así que la composición
# va agrupada y centrada en vez de repartida a los lados: un recorte por los bordes no se lleva
# nada que haga falta leer. Por lo mismo no hay texto pequeño — a tamaño de miniatura no se lee—,
# ni marco de teléfono ni insignias de tienda, que además Play prohíbe.
MARGEN_PLAY = 64

# El texto se limita a una banda MÁS estrecha que el margen del lienzo, y esto es lo que evita el
# problema de verdad: si se le deja los 896 px disponibles, `ajustar` los llena hasta el borde y el
# primer recorte lateral se lleva la primera y la última palabra. Con 700 el titular baja de cuerpo
# y queda con margen real a los lados.
BANDA_TEXTO = 700

FICHAS_PLAY = {
    'marca/ficha-play-1024x500.png': dict(
        titular='Tus gastos se apuntan solos',
        pie='Sin internet. Nada sale del móvil.'),
    'marca/ficha-play-1024x500-en.png': dict(
        titular='Your spending records itself',
        pie='No internet. Nothing leaves your phone.'),
}


def ficha_play(titular, pie, marca):
    """El gráfico de cabecera de la ficha de Play."""
    im = Image.new('RGB', (ANCHO_PLAY, ALTO_PLAY), FONDO)
    d = ImageDraw.Draw(im)

    lado = 168
    m = marca.resize((lado, lado), Image.LANCZOS)

    # El bloque entero (marca + Xtracto + titular + pie) se mide primero y se centra después. Es la
    # única forma de que cambiar un texto no descuadre la imagen y haya que recolocarla a mano.
    f_marca = manrope(60)
    f_tit, tam_tit = ajustar(d, [titular], BANDA_TEXTO, 62, peso=800)
    f_pie = manrope(30, 500)

    alto_cabecera = max(lado, 70)
    alto_tit = int(tam_tit * 1.2)
    alto_pie = 40
    total = alto_cabecera + 34 + alto_tit + 20 + alto_pie
    y = (ALTO_PLAY - total) // 2

    # Fila de arriba: la marca y el nombre, juntos y centrados.
    ancho_nombre = ancho(d, 'Xtracto', f_marca)
    fila = lado + 24 + ancho_nombre
    x = (ANCHO_PLAY - fila) // 2
    im.paste(m, (x, y + (alto_cabecera - lado) // 2), m)
    caja = d.textbbox((0, 0), 'Xtracto', font=f_marca)
    d.text((x + lado + 24, y + (alto_cabecera - caja[3]) // 2 - caja[1]),
           'Xtracto', font=f_marca, fill=TEXTO_1)
    y += alto_cabecera + 34

    d.text(((ANCHO_PLAY - ancho(d, titular, f_tit)) // 2, y), titular, font=f_tit, fill=ACENTO)
    y += alto_tit + 20

    d.text(((ANCHO_PLAY - ancho(d, pie, f_pie)) // 2, y), pie, font=f_pie, fill=TEXTO_2)
    return im


def main():
    import io
    import cairosvg
    datos = cairosvg.svg2png(url=str(RAIZ / 'marca' / 'logo.svg'),
                             output_width=760, output_height=760)
    marca = Image.open(io.BytesIO(datos)).convert('RGBA')
    for nombre, kw in TARJETAS.items():
        tarjeta(marca=marca, **kw).save(RAIZ / nombre)
        print(f'  {nombre}')
    for nombre, kw in FICHAS_PLAY.items():
        im = ficha_play(marca=marca, **kw)
        assert im.size == (ANCHO_PLAY, ALTO_PLAY) and im.mode == 'RGB'
        im.save(RAIZ / nombre)
        print(f'  {nombre}  {im.size[0]}x{im.size[1]} {im.mode}')


if __name__ == '__main__':
    main()
