#!/usr/bin/env python3
"""
Genera las tarjetas que se ven cuando alguien pega un enlace de xtracto.app en WhatsApp, en Slack,
en Mastodon o en X.

Va aparte de `generar.py` porque necesita dos cosas que la marca no necesita: red, para bajarse
Manrope, y pillow. La fuente se guarda en `marca/.fuentes/`, que está en el .gitignore: es de
Google Fonts, no hace falta versionarla aquí.

    python3 marca/tarjeta.py

La tarjeta dice «En desarrollo» a propósito. Un enlace compartido es lo primero que ve mucha gente,
y no queremos que llegue a la web esperando un botón de descarga que todavía no existe.
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


def main():
    import io
    import cairosvg
    datos = cairosvg.svg2png(url=str(RAIZ / 'marca' / 'logo.svg'),
                             output_width=760, output_height=760)
    marca = Image.open(io.BytesIO(datos)).convert('RGBA')
    for nombre, kw in TARJETAS.items():
        tarjeta(marca=marca, **kw).save(RAIZ / nombre)
        print(f'  {nombre}')


if __name__ == '__main__':
    main()
