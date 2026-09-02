#!/usr/bin/env python3
"""
Genera `bancos.html` y `banks.html`, la lista de entidades cuyos avisos reconoce Xtracto.

Es la única pregunta que trae a casi todo el mundo —«¿está mi banco?»— y la respuesta no está en
ninguna parte del sitio. Además es el mejor contenido que puede tener esta web para los buscadores:
quien escribe «app gastos BBVA» busca exactamente esto.

    python3 bancos.py

**La lista de abajo es la fuente.** Sale del parser de la app, que vive en el repositorio privado,
así que hay que traerla a mano cada vez que se añada una entidad. Mientras esté vacía el script no
escribe nada: una página que promete una lista y no la trae es peor que no tenerla.
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Los nombres de las operaciones, para no escribirlos dos veces ni desincronizar los idiomas.
OPERACIONES = {
    'compra':     {'es': 'Compra con tarjeta', 'en': 'Card payment'},
    'recibo':     {'es': 'Recibo domiciliado', 'en': 'Direct debit'},
    'devolucion': {'es': 'Pago cancelado', 'en': 'Cancelled payment'},
}

# ('Nombre comercial', 'identificador.de.la.app', [operaciones], {'es': nota, 'en': nota})
#
# **Aquí va solo lo que el parser interpreta de verdad**, no lo que archiva. La app guarda también
# los avisos en crudo de otras aplicaciones financieras para poder añadir sus gramáticas más
# adelante, pero esa lista no se publica por dos motivos: quien viera su banco ahí creería que ya
# funciona, y son las apps instaladas en un teléfono concreto, así que decían de su dueño más de lo
# que nadie necesita saber.
#
# El nombre es el que la gente teclea al buscar, no el legal. El identificador es el del paquete de
# Android, que es lo que de verdad distingue una app de otra.
SOPORTADOS: list[tuple[str, str, list[str], dict[str, str]]] = [
    ('Caja Rural · Ruralvía', 'com.rsi.nba', ['compra', 'recibo'], {
        'es': 'Las cajas rurales que operan con Ruralvía comparten esta aplicación, así que sirve '
              'para todas ellas.',
        'en': 'The Spanish rural banks that operate through Ruralvía share this application, so it '
              'covers all of them.'}),
    ('Google Wallet', 'com.google.android.apps.walletnfcrel', ['compra'], {
        'es': 'Los pagos con el móvil, sea cual sea la tarjeta que tengas dentro.',
        'en': 'Phone payments, whichever card you have inside.'}),
    ('Trade Republic', 'de.traderepublic.app', ['compra', 'devolucion'], {
        'es': 'Reconoce también el aviso de que un cobro se anula, para tachar el movimiento ya '
              'registrado.',
        'en': 'It also recognises the alert that a charge has been cancelled, to strike through the '
              'movement already recorded.'}),
]

TEXTOS = {
    'es': dict(
        fichero='bancos.html', otro='banks.html', lang='es', og='og.png',
        titulo='Bancos y apps que Xtracto reconoce',
        desc='Lista de entidades cuyos avisos entiende Xtracto, con el identificador de cada app. '
             'Si el tuyo no está, puedes enviarnos el formato sin enviarnos tus datos.',
        volver='index.html', volver_txt='Xtracto',
        h1='Bancos y apps que Xtracto reconoce',
        entradilla='Xtracto lee los avisos que estas aplicaciones te mandan al móvil y los convierte '
                   'en movimientos. La lista crece con los formatos que envía la gente.',
        h2_lista='La lista', h2_falta='¿No está el tuyo?',
        col=('Entidad', 'Identificador de la app', 'Qué avisos reconoce'),
        falta='Si tu banco usa otro formato, la app te lo dirá: guardará el aviso sin interpretarlo y '
              'podrás mandarnos la plantilla del mensaje <strong>sin mandarnos ni un dato tuyo</strong>. '
              'Antes de compartir nada, sustituye importes, fechas, comercios y números por marcadores '
              'y te enseña exactamente el texto que va a salir.',
        boton='Enviar el formato de mi banco', destino='formato.html',
        pie='Xtracto · Hecha para funcionar sin conexión · <a href="privacidad.html">Privacidad</a>',
        nota='Reconocer un aviso no es conectarse al banco. Xtracto no pide credenciales, no usa Open '
             'Banking y no puede consultar tu saldo real: solo lee las notificaciones que ya recibes.'),
    'en': dict(
        fichero='banks.html', otro='bancos.html', lang='en', og='og-en.png',
        titulo='Banks and apps Xtracto recognises',
        desc='The banks whose alerts Xtracto understands, with each app identifier. If yours is not '
             'there, you can send us the format without sending us your data.',
        volver='en.html', volver_txt='Xtracto',
        h1='Banks and apps Xtracto recognises',
        entradilla='Xtracto reads the alerts these applications send to your phone and turns them into '
                   'transactions. The list grows with the formats people send in.',
        h2_lista='The list', h2_falta='Yours is not there?',
        col=('Bank', 'Application id', 'Which alerts it recognises'),
        falta='If your bank uses another format, the app will tell you: it stores the alert without '
              'interpreting it and you can send us the message template <strong>without sending us any '
              'of your data</strong>. Before anything is shared, it replaces amounts, dates, merchants '
              'and numbers with placeholders and shows you exactly what will go out.',
        boton="Send my bank's format", destino='format.html',
        pie='Xtracto · Built to work offline · <a href="privacidad.html#en">Privacy</a>',
        nota='Recognising an alert is not connecting to a bank. Xtracto asks for no credentials, does '
             'not use Open Banking and cannot read your real balance: it only reads notifications you '
             'already receive.'),
}

PLANTILLA = '''<!doctype html>
<!-- Generado por bancos.py. No editar a mano: se regenera y te lo pisa. -->
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; base-uri 'none'; form-action 'none'">
<link rel="canonical" href="https://xtracto.app/{fichero}">
<link rel="alternate" hreflang="es" href="https://xtracto.app/bancos.html">
<link rel="alternate" hreflang="en" href="https://xtracto.app/banks.html">
<link rel="alternate" hreflang="x-default" href="https://xtracto.app/bancos.html">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Xtracto">
<meta property="og:url" content="https://xtracto.app/{fichero}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://xtracto.app/{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preload" href="fuentes/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="estilo.css">
</head>
<body>

<div class="envoltorio">
  <div class="idiomas"><a href="bancos.html"{act_es}>Español</a> · <a href="banks.html"{act_en}>English</a></div>
</div>

<header class="principal" style="padding:40px 0 48px;text-align:left">
  <div class="envoltorio">
    <p><a href="{volver}">&larr; {volver_txt}</a></p>
    <h1 style="font-size:clamp(28px,5vw,40px);margin-top:18px">{h1}</h1>
    <p class="entradilla" style="margin:0">{entradilla}</p>
  </div>
</header>

<section>
  <div class="envoltorio">
    <h2>{h2_lista}</h2>
    <div style="overflow-x:auto">
      <table style="width:100%;border-collapse:collapse;min-width:520px">
        <tr>{cabeceras}</tr>
{filas}
      </table>
    </div>
    <div class="aviso" style="margin-top:26px"><p style="margin:0">{nota}</p></div>
  </div>
</section>

<section>
  <div class="envoltorio">
    <h2>{h2_falta}</h2>
    <p>{falta}</p>
    <p style="margin-top:22px"><a class="boton" href="{destino}">{boton}</a></p>
  </div>
</section>

<footer>
  <div class="envoltorio">
    <p>{pie}</p>
  </div>
</footer>

</body>
</html>
'''

CELDA = 'style="text-align:left;padding:10px 12px;border-bottom:1px solid var(--border)"'


def pagina(t):
    cabeceras = ''.join(f'<th {CELDA}>{html.escape(c)}</th>' for c in t['col'])
    filas = []
    idioma = t['lang']
    for nombre, paquete, operaciones, nota in sorted(SOPORTADOS, key=lambda b: b[0].lower()):
        ops = ', '.join(OPERACIONES[o][idioma] for o in operaciones)
        # La nota va como segunda línea de la celda y no como cuarta columna: con cuatro, las tres
        # primeras se estrangulaban y el nombre del banco salía partido en dos renglones.
        apunte = f'<br><span class="apunte">{html.escape(nota[idioma])}</span>' if nota.get(idioma) else ''
        filas.append(
            f'        <tr><td {CELDA} class="entidad"><strong>{html.escape(nombre)}</strong></td>'
            f'<td {CELDA}><code>{html.escape(paquete)}</code></td>'
            f'<td {CELDA}>{html.escape(ops)}{apunte}</td></tr>')
    return PLANTILLA.format(cabeceras=cabeceras, filas='\n'.join(filas),
                            act_es=' class="activo"' if t['lang'] == 'es' else '',
                            act_en=' class="activo"' if t['lang'] == 'en' else '', **t)


def main():
    if not SOPORTADOS:
        print('La lista SOPORTADOS está vacía, así que no escribo nada.\n\n'
              'Sácala del parser de la app y pégala arriba, con este formato:\n'
              "    ('CaixaBank', 'com.caixabank.wallet', ['Compra con tarjeta', 'Bizum']),\n\n"
              'Publicar una página que promete la lista de bancos y llega vacía es peor que no\n'
              'tenerla: es justo la pregunta que trae a la gente, y se van con la respuesta a medias.')
        return 1
    for t in TEXTOS.values():
        (RAIZ / t['fichero']).write_text(pagina(t), encoding='utf-8')
        print(f"  {t['fichero']}  ({len(SOPORTADOS)} entidades)")
    print('\nAcuérdate de `python3 sitemap.py` para que entren en el sitemap.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
