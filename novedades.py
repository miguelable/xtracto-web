#!/usr/bin/env python3
"""
Genera `novedades.html` y `roadmap.html`: en qué punto está Xtracto y hacia dónde va.

    python3 novedades.py

**Es una página generada por el mismo motivo que `bancos.html`**: son dos idiomas contando lo mismo
y esto se toca a menudo —cada vez que se cierra algo—, que es exactamente la situación en la que dos
ficheros paralelos se separan. Aquí no pueden: los dos salen de las listas de abajo, así que una
entrada nueva o una que cambia de cajón entra en las dos páginas o no entra en ninguna.

**La fuente de verdad es el repositorio de la app**, `../xtracto` → `README.md` (*Plan de hitos*) y
`CLAUDE.md`. Esto es su traducción a lo que le importa a quien va a usar la app, y hay que traerla a
mano cuando el plan se mueva.

Tres reglas para editar esto, y las tres tienen motivo:

  · **«Terminado» quiere decir verificado en un teléfono, no publicado.** Es la distinción que hace
    honesta la página: mezclarlas la convierte en un folleto. Lo publicado va en VERSIONES.
  · **Sin fechas para lo que falta.** El camino crítico de hoy son doce testers, y dos cosas de la
    lista esperan a que ocurran en el mundo. Una fecha aquí sería una promesa que no controlamos.
  · **Cada cosa que falta dice por qué falta.** Un plan sin motivos es una carta a los Reyes; los
    motivos son justamente lo que hace que la página se pueda enlazar.

Y una que no es de estilo: **no repitas aquí el número de aplicaciones del catálogo**. Ya está
escrito cuatro veces en cada portada y nadie lo vigila —`verificar.py` no puede leer el repositorio
de la app—, así que la quinta copia sería la que se quede vieja. Se enlaza a la portada y ya.
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# El contenido. Cada bloque es un cajón de la hoja de ruta, y cada entrada un (título, explicación)
# con sus dos idiomas juntos para que no se pueda añadir uno sin el otro.
# ─────────────────────────────────────────────────────────────────────────────────────────────────

BLOQUES = [
    {
        'id': {'es': 'terminado', 'en': 'done'},
        'titulo': {'es': 'Terminado', 'en': 'Done'},
        'marca': '✓', 'color': 'var(--success)',
        'intro': {
            'es': '<strong>«Terminado» quiere decir escrito, probado y verificado en un teléfono de '
                  'verdad.</strong> No quiere decir que esté ya en la versión que tienes instalada. '
                  'La que hay hoy en la prueba cerrada es la <strong>1.0</strong>, y de todo esto '
                  'lleva cuatro cosas: leer los avisos, apuntar a mano, elegir a qué apps hace caso '
                  'y el total con su desglose —que allí es solo el del mes, sin los demás '
                  'periodos—. <strong>El resto de este cajón espera a la siguiente versión</strong>, '
                  'y al final de la página está el historial, que dice qué llevaba cada una.',
            'en': '<strong>“Done” means written, tested and verified on a real phone.</strong> It '
                  'does not mean it is already in the version you have installed. The one in the '
                  'closed test today is <strong>1.0</strong>, and out of all this it carries four '
                  'things: reading the alerts, entering by hand, choosing which apps it listens to, '
                  'and the total with its breakdown —which there is the month’s only, without the '
                  'other periods—. <strong>The rest of this box is waiting for the next '
                  'version</strong>, and the release history at the end of the page says what each '
                  'one carried.'},
        'items': [
            ({'es': 'Leer los avisos del banco',
              'en': 'Reading your bank’s alerts'},
             {'es': 'Cuando el banco avisa de una compra o de un recibo, Xtracto lee ese aviso y lo '
                    'convierte en un movimiento, con su importe, su comercio y su tarjeta. Sin '
                    'teclear nada y sin hablar con ningún servidor.',
              'en': 'When your bank tells you about a card payment or a direct debit, Xtracto reads '
                    'that alert and turns it into a transaction, with its amount, its merchant and '
                    'its card. Without typing anything and without talking to any server.'}),
            ({'es': 'Apuntar un gasto a mano',
              'en': 'Entering an expense by hand'},
             {'es': 'Para lo que el banco no avisa: el efectivo, una tarjeta de tienda, un pago que '
                    'hizo otro. Y si más adelante llega el aviso de ese mismo pago, '
                    '<strong>sustituye a tu apunte en vez de contarlo dos veces</strong>.',
              'en': 'For what the bank never announces: cash, a store card, a payment someone else '
                    'made. And if the alert for that same payment arrives later, <strong>it '
                    'replaces your entry instead of counting it twice</strong>.'}),
            ({'es': 'Decidir a qué apps hace caso',
              'en': 'Deciding which apps it listens to'},
             {'es': 'El catálogo es una <a href="index.html#el-permiso">lista cerrada de '
                    'aplicaciones financieras</a>, y dentro de ella eliges una a una. Apagar una no '
                    'es dejar de mostrarla: el servicio ni siquiera abre sus notificaciones.',
              'en': 'The catalogue is a <a href="en.html#the-permission">closed list of finance '
                    'applications</a>, and within it you choose one by one. Turning one off is not '
                    'hiding it: the service does not even open its notifications.'}),
            ({'es': 'El total del periodo, y con qué comparar',
              'en': 'The period total, and something to compare it with'},
             {'es': 'Día, semana, mes, año o todo el histórico. La comparación con el periodo '
                    'anterior va <strong>recortada al mismo punto</strong>: enfrentar un mes a '
                    'medias contra uno entero no dice nada.',
              'en': 'Day, week, month, year or the whole history. The comparison with the previous '
                    'period is <strong>trimmed to the same point</strong>: setting half a month '
                    'against a whole one tells you nothing.'}),
            ({'es': 'Poner nombre a tus tarjetas y cuentas',
              'en': 'Naming your cards and accounts'},
             {'es': '«••0634» no le dice nada a nadie y «Trade Republic» sí. El nombre es solo '
                    'presentación: <strong>los cuatro dígitos siguen a la vista</strong>, porque son '
                    'lo que te deja cuadrar el desglose contra el extracto del banco.',
              'en': '“••0634” means nothing to anybody and “Trade Republic” does. The name is '
                    'presentation only: <strong>the four digits stay visible</strong>, because they '
                    'are what lets you reconcile the breakdown against your bank statement.'}),
            ({'es': 'Categorías de gasto',
              'en': 'Spending categories'},
             {'es': 'Una lista cerrada de catorce, y se clasifica <strong>el comercio, no el '
                    'movimiento</strong>: clasificas el supermercado una vez y quedan clasificadas '
                    'todas sus compras, las de antes y las que lleguen.',
              'en': 'A closed list of fourteen, and what gets classified is <strong>the merchant, '
                    'not the transaction</strong>: you classify the supermarket once and every '
                    'purchase there is classified, the past ones and the ones still to come.'}),
            ({'es': 'Un resumen que se lee de un vistazo',
              'en': 'A summary you can read at a glance'},
             {'es': 'El total dice <em>cuánto</em>, el mapa de calor <em>cuándo</em>, el anillo de '
                    'categorías <em>en qué</em> y el top de comercios <em>dónde</em>. Está dibujado '
                    'a mano, <strong>sin ninguna librería de gráficas</strong>: cada dependencia es '
                    'peso, superficie que auditar y una cosa más que podría querer tocar la red.',
              'en': 'The total says <em>how much</em>, the heatmap <em>when</em>, the category ring '
                    '<em>on what</em> and the merchant top <em>where</em>. It is drawn by hand, '
                    '<strong>with no charting library</strong>: every dependency is weight, surface '
                    'to audit and one more thing that might want to touch the network.'}),
            ({'es': 'Presupuesto mensual',
              'en': 'A monthly budget'},
             {'es': 'Con marca de ritmo, porque llevar gastado el 60 % el día 5 y llevarlo el día 25 '
                    'no son la misma noticia, y una barra a secas las pinta igual.',
              'en': 'With a pace marker, because having spent 60 % on the 5th and having spent it '
                    'on the 25th are not the same news, and a plain bar paints them identically.'}),
            ({'es': 'Elegir qué gráficas se ven',
              'en': 'Choosing which charts you see'},
             {'es': 'Cada gráfica nueva alarga el resumen. Las que no te interesen se apagan '
                    '<strong>desde el propio resumen</strong>, que es donde se ve lo que sobra, y no '
                    'desde una pantalla de ajustes.',
              'en': 'Every new chart makes the summary longer. The ones you do not care about are '
                    'turned off <strong>from the summary itself</strong>, which is where you can see '
                    'what is in the way, and not from a settings screen.'}),
            ({'es': 'Entradas y traspasos, distinguidos',
              'en': 'Money in and transfers, told apart'},
             {'es': 'Una entrada va en verde y con un «+»; un traspaso, apagado y sin signo, porque '
                    'mover dinero de un bolsillo tuyo a otro no es ni gasto ni ingreso. '
                    '<strong>Los totales siguen contando solo salidas</strong>, para que el día que '
                    'entre el primer ingreso el mes no se infle.',
              'en': 'Money in shows green with a “+”; a transfer shows muted and unsigned, because '
                    'moving money from one of your pockets to another is neither spending nor '
                    'income. <strong>Totals still count outgoings only</strong>, so that the day the '
                    'first credit lands the month does not inflate.'}),
            ({'es': 'Tablet',
              'en': 'Tablet'},
             {'es': 'El resumen en tres columnas, y las listas con el detalle al lado en vez de una '
                    'columna estrecha en medio de una pantalla vacía.',
              'en': 'The summary in three columns, and the lists with the detail beside them instead '
                    'of one narrow column in the middle of an empty screen.'}),
        ],
    },
    {
        'id': {'es': 'en-marcha', 'en': 'in-progress'},
        'titulo': {'es': 'En marcha ahora', 'en': 'In progress now'},
        'marca': '●', 'color': 'var(--warn)',
        'intro': {
            'es': 'Lo que se está tocando estos días. Va por orden de lo que más cuesta tenerlo sin '
                  'terminar.',
            'en': 'What is being worked on these days, ordered by what it costs most to leave '
                  'unfinished.'},
        'items': [
            ({'es': 'Los cargos que no dicen de quién son',
              'en': 'Charges that do not say who they are from'},
             {'es': 'Hay avisos que solo dicen que se ha cargado un importe en la cuenta, sin '
                    'comercio. <strong>La misma frase, palabra por palabra, sirve para un Bizum '
                    'enviado y para la liquidación mensual de una tarjeta de crédito</strong>, y '
                    'nada del texto los distingue. Añadir la regla a ciegas contaría dos veces las '
                    'compras de esa tarjeta: primero cada compra y después el recibo que las cobra '
                    'todas juntas. La salida es que declares en Ajustes qué tarjeta es de crédito y '
                    'contra qué cuenta liquida, y cuadrar por importe exacto. '
                    '<strong>Es lo único de toda la página que hoy se cuenta mal</strong>, y por eso '
                    'va primero.',
              'en': 'Some alerts only say that an amount was charged to the account, with no '
                    'merchant. <strong>The same sentence, word for word, covers an instant transfer '
                    'you sent and the monthly settlement of a credit card</strong>, and nothing in '
                    'the text tells them apart. Adding the rule blindly would count that card’s '
                    'purchases twice: each purchase first, and then the receipt that charges them '
                    'all together. The way out is for you to declare in Settings which card is a '
                    'credit card and which account it settles against, then reconcile by exact '
                    'amount. <strong>It is the only thing on this page that is counted wrong '
                    'today</strong>, which is why it comes first.'}),
            ({'es': 'Que las entradas se lean solas',
              'en': 'Getting money in to read itself'},
             {'es': 'Las reglas para los ingresos ya están escritas —transferencia recibida, '
                    'intereses, nómina— y lo que falta es comprobarlas contra avisos de verdad. '
                    '<strong>Escrito no es verificado</strong>, y una nómina aparece una vez al mes: '
                    'esto avanza al ritmo del calendario, no al del teclado.',
              'en': 'The rules for incoming money are already written —transfer received, interest, '
                    'salary— and what is missing is checking them against real alerts. '
                    '<strong>Written is not verified</strong>, and a salary shows up once a month: '
                    'this moves at the pace of the calendar, not of the keyboard.'}),
            ({'es': 'Más bancos',
              'en': 'More banks'},
             {'es': 'La <a href="bancos.html">lista de entidades reconocidas</a> crece con los '
                    'formatos que envía la gente. Cuando un aviso no se entiende, se puede mandar '
                    '<strong>sin mandar ni un dato</strong>: la app sustituye importes, fechas, '
                    'comercios y números por marcadores y te enseña el texto exacto antes de que '
                    'salga.',
              'en': 'The <a href="banks.html">list of recognised banks</a> grows with the formats '
                    'people send in. When an alert is not understood, it can be sent <strong>without '
                    'sending any of your data</strong>: the app replaces amounts, dates, merchants '
                    'and numbers with placeholders and shows you the exact text before it goes.'}),
        ],
    },
    {
        'id': {'es': 'lo-siguiente', 'en': 'next'},
        'titulo': {'es': 'Lo siguiente', 'en': 'Next'},
        'marca': '○', 'color': 'var(--text-3)',
        'intro': {
            'es': 'Está decidido y no está empezado. Casi todo espera a lo mismo: que la app vea '
                  'también el dinero que entra.',
            'en': 'Decided and not started. Nearly all of it waits on the same thing: the app seeing '
                  'the money that comes in as well.'},
        'items': [
            ({'es': 'Entradas contra salidas, en barras',
              'en': 'Money in against money out, in bars'},
             {'es': 'Qué entró y qué salió en cada periodo, de un vistazo. Espera a que las entradas '
                    'se lean solas.',
              'en': 'What came in and what went out in each period, at a glance. Waiting on incoming '
                    'money reading itself.'}),
            ({'es': 'Balance neto y tasa de ahorro',
              'en': 'Net balance and savings rate'},
             {'es': 'Calcularlos es trivial, y por eso mismo <strong>no están</strong>. Mientras la '
                    'app no vea todas las entradas, el neto de un mes en el que entró un sueldo '
                    'saldría en rojo y parecería que alguien está quemando ahorros. <strong>Una '
                    'cifra exacta y falsa es peor que ninguna cifra.</strong>',
              'en': 'Computing them is trivial, which is exactly why <strong>they are not '
                    'there</strong>. Until the app sees every credit, the net figure for a month in '
                    'which a salary landed would come out red, as if somebody were burning through '
                    'savings. <strong>An exact, false number is worse than no number.</strong>'}),
            ({'es': 'Tendencia',
              'en': 'Trend'},
             {'es': 'Cómo va el gasto respecto a los periodos anteriores. Misma espera.',
              'en': 'How spending is going against previous periods. Same wait.'}),
            ({'es': 'Elegir un rango de fechas a medida',
              'en': 'Picking a custom date range'},
             {'es': 'Por dentro funciona desde el principio; falta la pantalla para elegir las dos '
                    'fechas. No sale como opción hasta que la haya: una opción que no puede hacer '
                    'nada es peor que no tenerla.',
              'en': 'Under the hood it has worked from the start; what is missing is the screen to '
                    'pick the two dates. It does not appear as an option until then: an option that '
                    'cannot do anything is worse than no option.'}),
        ],
    },
    {
        'id': {'es': 'mas-adelante', 'en': 'later'},
        'titulo': {'es': 'Más adelante', 'en': 'Later on'},
        'marca': '○', 'color': 'var(--text-3)',
        'intro': {
            'es': 'Hacia dónde va la app cuando lo de arriba esté cerrado.',
            'en': 'Where the app is heading once the above is closed.'},
        'items': [
            ({'es': 'Detectar lo que se repite',
              'en': 'Spotting what repeats'},
             {'es': 'Suscripciones y recibos deducidos del propio historial, sin que los teclees: '
                    'mismo comercio, importe parecido, cadencia mensual o anual. <strong>No se puede '
                    'hacer todavía, y no por falta de ganas:</strong> para deducir una cadencia '
                    'hacen falta unos tres meses de historial, y una app recién instalada no los '
                    'tiene. Escribirlo hoy sería calibrarlo contra casos inventados.',
              'en': 'Subscriptions and recurring bills deduced from your own history, without typing '
                    'them in: same merchant, similar amount, monthly or yearly cadence. <strong>It '
                    'cannot be done yet, and not for lack of wanting to:</strong> deducing a cadence '
                    'needs roughly three months of history, and a freshly installed app does not '
                    'have them. Writing it today would mean calibrating it against invented cases.'}),
            ({'es': 'Avisos, sin salir del móvil',
              'en': 'Alerts, without leaving the phone'},
             {'es': '«Vas por el 90 % del presupuesto», una suscripción que sube de precio. Lo normal '
                    'es hacer esto con notificaciones push desde un servidor; aquí <strong>no hay '
                    'servidor ni permiso de red</strong>, así que lo lanza el propio Android en '
                    'local. Cambia el carácter de la app —de observar a interrumpir—, así que se '
                    'decidirá con calma.',
              'en': '“You are at 90 % of your budget”, a subscription that went up in price. The '
                    'usual way to do this is push notifications from a server; here there is '
                    '<strong>no server and no network permission</strong>, so Android itself fires '
                    'them locally. It changes the character of the app —from watching to '
                    'interrupting— so it will be decided slowly.'}),
            ({'es': 'Un panel de conclusiones',
              'en': 'A findings panel'},
             {'es': 'El mayor gasto del mes, el comercio más frecuente, la variación contra el mes '
                    'anterior. Es <strong>el sustituto honesto de un asistente de inteligencia '
                    'artificial</strong>: «¿cuánto gasté en ocio?» no es inteligencia, es una '
                    'consulta.',
              'en': 'The biggest expense of the month, the most frequent merchant, the change '
                    'against last month. It is <strong>the honest substitute for an AI '
                    'assistant</strong>: “how much did I spend on going out?” is not intelligence, '
                    'it is a query.'}),
        ],
    },
    {
        'id': {'es': 'no-vamos-a-hacer', 'en': 'not-doing'},
        'titulo': {'es': 'Lo que no vamos a hacer', 'en': 'What we are not going to do'},
        'marca': '✕', 'color': 'var(--danger)',
        'intro': {
            'es': 'Un plan que solo dice lo que va a llegar no se puede juzgar. Esto es lo que se ha '
                  'descartado <strong>a propósito</strong>, y por qué: casi todo son cosas que las '
                  'apps de gastos hacen, y cada una costaría justo lo que hace distinta a esta.',
            'en': 'A plan that only says what is coming cannot be judged. This is what has been '
                  'ruled out <strong>on purpose</strong>, and why: nearly all of it is what expense '
                  'apps do, and each one would cost exactly what makes this one different.'},
        'items': [
            ({'es': 'Conectarse a tu banco',
              'en': 'Linking to your bank'},
             {'es': 'Ni credenciales ni Open Banking. Es la línea que define la app: sin ella '
                    'Xtracto sería una de las cien que ya existen, y con ella no puede consultar tu '
                    'saldo real ni mover un euro. Las tres formas que hay de apuntar gastos, y qué '
                    've cada una, están <a href="sin-conectar-el-banco.html">comparadas aquí</a>.',
              'en': 'No credentials and no Open Banking. It is the line that defines the app: '
                    'without it Xtracto would be one of the hundred that already exist, and with it '
                    'the app cannot read your real balance or move a euro. The three ways of '
                    'recording expenses, and what each one sees, are <a '
                    'href="without-linking-your-bank.html">compared here</a>.'}),
            ({'es': 'Un asistente de IA en la nube',
              'en': 'A cloud AI assistant'},
             {'es': 'Mandar tus gastos a la API de alguien para que te los resuma contradice todo lo '
                    'demás. Que el modelo corra <strong>dentro del propio teléfono</strong> sí es '
                    'una puerta abierta, pero solo el día que se pueda comprobar que ni siquiera '
                    'bajar el modelo rompe el «nada sale del móvil».',
              'en': 'Sending your spending to somebody’s API so it can summarise it contradicts '
                    'everything else. A model running <strong>inside the phone itself</strong> is an '
                    'open door, but only the day it can be shown that not even downloading the model '
                    'breaks the “nothing leaves the phone”.'}),
            ({'es': 'Leer tickets con la cámara',
              'en': 'Reading receipts with the camera'},
             {'es': 'Cubriría el efectivo, y técnicamente se puede hacer sin conexión. Pero cuesta '
                    '<strong>el permiso de cámara</strong>, y el argumento entero de esta app es que '
                    'pide lo mínimo y ni siquiera red.',
              'en': 'It would cover cash, and technically it can be done offline. But it costs '
                    '<strong>the camera permission</strong>, and this app’s whole argument is that '
                    'it asks for the minimum and not even network access.'}),
            ({'es': 'Saldos, deudas, objetivos y patrimonio',
              'en': 'Balances, debts, goals and net worth'},
             {'es': 'Contradice la premisa: <strong>Xtracto observa, no te pone a llevar la '
                    'contabilidad</strong>. El apunte manual existe para tapar los huecos que el '
                    'banco no avisa, no para que teclees tu vida.',
              'en': 'It contradicts the premise: <strong>Xtracto watches, it does not put you to '
                    'work doing bookkeeping</strong>. Entering by hand exists to cover the gaps the '
                    'bank never announces, not so that you type out your life.'}),
            ({'es': 'Gastos compartidos entre amigos',
              'en': 'Splitting expenses with friends'},
             {'es': 'Es otro producto, y ya hay unos cuantos buenos.',
              'en': 'That is another product, and there are already a few good ones.'}),
        ],
    },
]

# El historial. Se numera cuando llega a Google Play, no cuando se termina de escribir: por eso hay
# cosas en «Terminado» que todavía no salen aquí.
#
# **El corte de la 1.0 es el hito 8 de la app**, o sea el estado del código cuando salió el AAB que
# se mandó a revisión (04-09-2026). Todo lo cerrado después —los periodos que no son el mes, los
# nombres de las tarjetas, las categorías, las gráficas del resumen, el presupuesto, las entradas y
# el tablet— es de la siguiente. Al escribir una versión nueva, **el corte se mira en la fecha del
# AAB**, no en la del último commit.
#
# Cada entrada dice también **lo que no lleva**, y no es humildad: es lo que evita que alguien
# instale la 1.0 esperando lo que ha leído más arriba en «Terminado».
#
# (número, {'es': fecha, 'en': fecha}, {'es': qué llevaba, 'en': qué llevaba})
VERSIONES = [
    ('1.0',
     {'es': 'septiembre de 2026', 'en': 'September 2026'},
     {'es': 'Primera versión, en Google Play y en prueba cerrada. Lleva lo justo para que la app '
            'sirva sola: lee las compras y los recibos de las entidades reconocidas y los convierte '
            'en movimientos; deja <strong>apuntar a mano</strong> lo que el banco no avisa, y '
            'sustituye ese apunte si el aviso llega más tarde; y lo enseña todo en cuatro pestañas '
            '—el <strong>total del mes</strong> con su desglose por tarjeta, el historial con '
            'buscador, el archivo de los avisos en crudo y los ajustes del permiso—. Guarda el aviso '
            'original detrás de cada movimiento, exporta a CSV, se esconde de las capturas de '
            'pantalla y de la vista de Recientes, y va en español y en inglés. <strong>Sin permiso '
            'de acceso a internet</strong>, así que no puede enviar nada a ningún sitio.'
            '<span style="display:block;margin-top:12px;color:var(--text-3)"><strong>Lo que todavía '
            'no lleva:</strong> los periodos que no son el mes, los nombres de las tarjetas, las '
            'categorías, las gráficas del resumen, el presupuesto, las entradas y los traspasos, y '
            'el reparto para tablet. Está todo arriba, en «Terminado», esperando a la siguiente '
            'versión.</span>',
      'en': 'First version, on Google Play and in closed testing. It carries just enough for the app '
            'to stand on its own: it reads card payments and direct debits from the recognised banks '
            'and turns them into transactions; it lets you <strong>enter by hand</strong> what the '
            'bank never announces, and replaces that entry if the alert turns up later; and it shows '
            'all of it across four tabs —the <strong>month total</strong> with its breakdown by '
            'card, the searchable history, the archive of raw alerts and the permission settings—. '
            'It keeps the original alert behind every transaction, exports to CSV, hides itself from '
            'screenshots and the Recents view, and comes in Spanish and English. <strong>With no '
            'internet permission</strong>, so it cannot send anything anywhere.'
            '<span style="display:block;margin-top:12px;color:var(--text-3)"><strong>What it does '
            'not carry yet:</strong> periods other than the month, card names, categories, the '
            'summary charts, the budget, money in and transfers, and the tablet layout. It is all up '
            'above under “Done”, waiting for the next version.</span>'}),
]

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# La barra de navegación, copiada igual que en las páginas escritas a mano y en `bancos.py`.
# `verificar.py` comprueba que las de todas las páginas sean la misma; si tocas la barra, tócala
# también en `bancos.py` y en `construir.py`, y regenera las tres.
#
# Esta página **no está en la barra**, a propósito: con cinco enlaces la barra en español no entra
# en una pantalla de portátil y saltaría al desplegable a 1024px. Se llega desde el pie de todas
# las páginas y desde la sección «Disponibilidad» de las dos portadas.
# ─────────────────────────────────────────────────────────────────────────────────────────────────

BARRA_ES = '''<nav class="navegacion" aria-label="Secciones del sitio">
  <div class="envoltorio">
    <a class="marca-nav" href="index.html"><img src="marca/logo.svg" width="26" height="26" alt=""><span>Xtracto</span></a>
    <input class="interruptor" id="menu" type="checkbox" aria-label="Menú">
    <label class="hamburguesa" for="menu" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M2 5h16M2 10h16M2 15h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></label>
    <div class="panel">
      <ul>
        <li><a href="sin-conectar-el-banco.html">Sin conectar el banco</a></li>
        <li><a href="bancos.html">Bancos</a></li>
        <li><a href="verificar-permisos.html">Verifícalo</a></li>
        <li><a href="privacidad.html">Privacidad</a></li>
      </ul>
      <div class="idiomas-nav"><a href="novedades.html" hreflang="es" lang="es" title="Español" class="activo">ES</a><span aria-hidden="true">·</span><a href="roadmap.html" hreflang="en" lang="en" title="English">EN</a></div>
    </div>
    <a class="boton compacto" href="prueba-cerrada.html">Probar la app</a>
  </div>
</nav>
'''
BARRA_EN = '''<nav class="navegacion" aria-label="Site sections">
  <div class="envoltorio">
    <a class="marca-nav" href="en.html"><img src="marca/logo.svg" width="26" height="26" alt=""><span>Xtracto</span></a>
    <input class="interruptor" id="menu" type="checkbox" aria-label="Menu">
    <label class="hamburguesa" for="menu" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M2 5h16M2 10h16M2 15h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></label>
    <div class="panel">
      <ul>
        <li><a href="without-linking-your-bank.html">Without linking</a></li>
        <li><a href="banks.html">Banks</a></li>
        <li><a href="check-permissions.html">Check it</a></li>
        <li><a href="privacidad.html#en">Privacy</a></li>
      </ul>
      <div class="idiomas-nav"><a href="novedades.html" hreflang="es" lang="es" title="Español">ES</a><span aria-hidden="true">·</span><a href="roadmap.html" hreflang="en" lang="en" title="English" class="activo">EN</a></div>
    </div>
    <a class="boton compacto" href="closed-test.html">Try the app</a>
  </div>
</nav>
'''

TEXTOS = {
    'es': dict(
        fichero='novedades.html', lang='es', og='og.png', barra=BARRA_ES,
        titulo='Novedades y hoja de ruta de Xtracto',
        desc='En qué punto está Xtracto: lo que la app ya hace, lo que se está probando ahora, lo '
             'que viene después y lo que no vamos a hacer nunca.',
        h1='Novedades y hoja de ruta',
        chip='En prueba cerrada · versión 1.0',
        entradilla='Dónde está Xtracto hoy, qué llevaba cada versión y hacia dónde va. Sin fechas, y '
                   'más abajo está el motivo.',
        h2_hoy='Dónde está hoy',
        hoy=['Xtracto <strong>ya está en Google Play, pero en prueba cerrada</strong>: hoy solo la '
             'pueden instalar las cuentas dadas de alta como testers. Lo que falta para abrirla a '
             'todo el mundo no es programar nada, es una condición de Google: <strong>doce personas '
             'dentro de la prueba durante catorce días seguidos</strong>, y usándola.',
             'Así que el camino crítico de este proyecto, hoy, no pasa por el código. '
             '<a href="prueba-cerrada.html">Entrar en la prueba</a> es lo que más lo acelera.'],
        h2_fechas='Por qué aquí no hay fechas',
        fechas=['Porque las que pudiera escribir serían mentira. Lo que hoy bloquea la publicación '
                'son doce personas y catorce días, no una función. Y dos de las cosas de arriba '
                '<strong>esperan a que ocurran en el mundo</strong> —que llegue una nómina, que '
                'llegue la liquidación mensual de una tarjeta—, que pasa cuando pasa y no se puede '
                'forzar.',
                'Lo que sí se puede decir es <strong>el orden y los motivos</strong>. Eso es todo lo '
                'de arriba, y se actualiza cada vez que algo cambia de cajón.'],
        h2_versiones='Historial de versiones',
        versiones_intro='Las versiones se numeran <strong>cuando llegan a Google Play</strong>, no '
                        'cuando se terminan de escribir. Por eso hay cosas en «Terminado» que '
                        'todavía no salen aquí abajo.',
        h2_ayuda='Lo que más acelera todo esto',
        ayuda=['<strong>Entrar en la prueba cerrada.</strong> Es el camino crítico, y la página no '
               'te pide ni un dato: el botón abre tu programa de correo con el mensaje escrito y lo '
               'mandas tú.',
               '<strong>Pedir tu banco.</strong> Con el nombre basta. Cada uno que llega es una '
               'entidad más reconocida el día que se publique.',
               '<strong>Enviar el formato de un aviso que no se entiende.</strong> Sin importes, '
               'fechas, comercios ni números: solo la forma de la frase.'],
        boton_prueba='Entrar en la prueba cerrada', destino_prueba='prueba-cerrada.html',
        boton_banco='Pedir mi banco', destino_banco='pide-tu-banco.html',
        nota='Esta página se escribe a mano desde el plan de la app, así que puede ir un poco por '
             'detrás de lo que hay dentro. <strong>Si algo de aquí no coincide con la app, manda la '
             'app.</strong>',
        pie='Xtracto · Hecha para funcionar sin conexión · <a href="privacidad.html">Privacidad</a> · <a href="mailto:support@xtracto.app">support@xtracto.app</a>'),
    'en': dict(
        fichero='roadmap.html', lang='en', og='og-en.png', barra=BARRA_EN,
        titulo='Xtracto roadmap and release notes',
        desc='Where Xtracto stands: what the app already does, what is being worked on now, what '
             'comes next, and what we are never going to do.',
        h1='Roadmap and release notes',
        chip='In closed testing · version 1.0',
        entradilla='Where Xtracto stands today, what each version carried and where it is heading. '
                   'No dates, and the reason is further down.',
        h2_hoy='Where it stands today',
        hoy=['Xtracto is <strong>already on Google Play, but in closed testing</strong>: today only '
             'accounts enrolled as testers can install it. What is missing before it opens to '
             'everybody is not code, it is a Google condition: <strong>twelve people inside the test '
             'for fourteen days in a row</strong>, and using it.',
             'So this project’s critical path, today, does not go through the code. '
             '<a href="closed-test.html">Joining the test</a> is what speeds it up most.'],
        h2_fechas='Why there are no dates here',
        fechas=['Because any I could write would be a lie. What blocks release today is twelve '
                'people and fourteen days, not a feature. And two of the things above <strong>are '
                'waiting on the real world</strong> —a salary payment arriving, a card’s monthly '
                'settlement arriving— which happens when it happens and cannot be forced.',
                'What can be said is <strong>the order and the reasons</strong>. That is everything '
                'above, and it is updated whenever something moves from one box to another.'],
        h2_versiones='Release history',
        versiones_intro='Versions are numbered <strong>when they reach Google Play</strong>, not '
                        'when they are finished. That is why there are things under “Done” that do '
                        'not appear down here yet.',
        h2_ayuda='What speeds all of this up most',
        ayuda=['<strong>Joining the closed test.</strong> It is the critical path, and the page asks '
               'you for nothing: the button opens your own mail app with the message written and you '
               'send it yourself.',
               '<strong>Asking for your bank.</strong> The name is enough. Every one that arrives is '
               'one more bank recognised the day it ships.',
               '<strong>Sending the format of an alert that is not understood.</strong> With no '
               'amounts, dates, merchants or numbers: only the shape of the sentence.'],
        boton_prueba='Join the closed test', destino_prueba='closed-test.html',
        boton_banco='Ask for my bank', destino_banco='request-a-bank.html',
        nota='This page is written by hand from the app’s plan, so it can lag a little behind what '
             'is actually inside. <strong>If anything here disagrees with the app, the app '
             'wins.</strong>',
        pie='Xtracto · Built to work offline · <a href="privacidad.html#en">Privacy</a> · <a href="mailto:support@xtracto.app">support@xtracto.app</a>'),
}

PLANTILLA = '''<!doctype html>
<!-- Generado por novedades.py. No editar a mano: se regenera y te lo pisa. -->
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; base-uri 'none'; form-action 'none'">
<link rel="canonical" href="https://xtracto.app/{fichero}">
<link rel="alternate" hreflang="es" href="https://xtracto.app/novedades.html">
<link rel="alternate" hreflang="en" href="https://xtracto.app/roadmap.html">
<link rel="alternate" hreflang="x-default" href="https://xtracto.app/novedades.html">
<meta property="og:type" content="article">
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

{barra}
<header class="principal" style="padding:40px 0 48px;text-align:left">
  <div class="envoltorio">
    <p class="chip" style="margin-left:0"><span class="punto"></span>{chip}</p>
    <h1 style="font-size:clamp(28px,5vw,40px);margin-top:18px">{h1}</h1>
    <p class="entradilla" style="margin:0">{entradilla}</p>
    <nav class="indice" aria-label="{en_esta_pagina}">
      <ul>
{pastillas}
      </ul>
    </nav>
  </div>
</header>

<section>
  <div class="envoltorio">
    <h2>{h2_hoy}</h2>
{hoy}
  </div>
</section>

{bloques}
<section>
  <div class="envoltorio">
    <h2>{h2_fechas}</h2>
{fechas}
  </div>
</section>

<section id="{id_versiones}">
  <div class="envoltorio">
    <h2>{h2_versiones}</h2>
    <p>{versiones_intro}</p>
{versiones}
  </div>
</section>

<section>
  <div class="envoltorio">
    <h2>{h2_ayuda}</h2>
    <ul class="limpia">
{ayuda}
    </ul>
    <p style="margin-top:26px">
      <a class="boton" href="{destino_prueba}">{boton_prueba}</a>
      <a class="boton secundario" href="{destino_banco}">{boton_banco}</a>
    </p>
    <div class="aviso" style="margin-top:26px"><p style="margin:0">{nota}</p></div>
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

# «En esta página» es el `aria-label` del índice de pastillas, y es lo único de la plantilla que no
# viene de TEXTOS porque no se ve: lo lee el lector de pantalla y nada más.
INDICE = {'es': 'En esta página', 'en': 'On this page'}
ID_VERSIONES = {'es': 'versiones', 'en': 'releases'}


def bloque(b, idioma):
    """Un cajón de la hoja de ruta: título, intro y su lista de entradas con la marca de estado.

    La marca va en un `<span aria-hidden="true">` y el estado se dice también con palabras en el
    `h2`, porque un símbolo de color es lo único que un lector de pantalla no puede contar.
    """
    filas = []
    for titulo, texto in b['items']:
        # El cuerpo **no** lleva `.apunte`: aquí la explicación es el contenido de la página, y
        # `.apunte` es 13,5px en el gris de las notas al pie. Hereda el color de `ul.limpia li`,
        # que ya es `--text-2`, y el título va en `--text-1` por la regla de `li strong`.
        filas.append(
            f'        <li><span class="marca-item" aria-hidden="true" style="color:{b["color"]}">'
            f'{b["marca"]}</span><span><strong>{html.escape(titulo[idioma])}</strong>'
            f'<span style="display:block;margin-top:5px">{texto[idioma]}</span></span></li>')
    return (f'<section id="{b["id"][idioma]}">\n'
            f'  <div class="envoltorio">\n'
            f'    <h2>{html.escape(b["titulo"][idioma])}</h2>\n'
            f'    <p>{b["intro"][idioma]}</p>\n'
            # 20px y no los 12 de `ul.limpia`: sus entradas son de una línea y estas son de cinco,
            # y con 12 las de un bloque se leían como un solo párrafo largo.
            f'    <ul class="limpia" style="margin-top:22px;gap:20px">\n'
            + '\n'.join(filas) + '\n'
            f'    </ul>\n'
            f'  </div>\n'
            f'</section>\n')


def pagina(t):
    idioma = t['lang']
    pastillas = '\n'.join(
        f'        <li><a href="#{b["id"][idioma]}">{html.escape(b["titulo"][idioma])}</a></li>'
        for b in BLOQUES)
    pastillas += (f'\n        <li><a href="#{ID_VERSIONES[idioma]}">'
                  f'{html.escape(t["h2_versiones"])}</a></li>')

    versiones = '\n'.join(
        f'    <div class="tarjeta" style="margin-top:16px">\n'
        f'      <h3>{html.escape(numero)} <span class="apunte" style="margin:0 0 0 6px">'
        f'{html.escape(fecha[idioma])}</span></h3>\n'
        f'      <p style="margin:0">{texto[idioma]}</p>\n'
        f'    </div>'
        for numero, fecha, texto in VERSIONES)

    # Las claves calculadas pisan a las de TEXTOS que tienen el mismo nombre (`hoy`, `fechas`,
    # `ayuda`), que ahí son listas de párrafos y aquí ya son HTML.
    datos = dict(t)
    datos.update(
        pastillas=pastillas,
        en_esta_pagina=INDICE[idioma],
        id_versiones=ID_VERSIONES[idioma],
        hoy='\n'.join(f'    <p>{p}</p>' for p in t['hoy']),
        bloques='\n'.join(bloque(b, idioma) for b in BLOQUES),
        fechas='\n'.join(f'    <p>{p}</p>' for p in t['fechas']),
        versiones=versiones,
        ayuda='\n'.join(
            f'      <li><span class="marca-item" aria-hidden="true" style="color:var(--accent)">'
            f'→</span><span>{p}</span></li>' for p in t['ayuda']))
    return PLANTILLA.format(**datos)


def main():
    # Mismo criterio que `bancos.py`: una página que promete el estado del proyecto y llega vacía
    # es peor que no tenerla, porque es justo lo que se viene a mirar.
    if not BLOQUES or not VERSIONES:
        print('BLOQUES o VERSIONES está vacío, así que no escribo nada.')
        return 1
    for t in TEXTOS.values():
        (RAIZ / t['fichero']).write_text(pagina(t), encoding='utf-8')
        entradas = sum(len(b['items']) for b in BLOQUES)
        print(f"  {t['fichero']}  ({entradas} entradas en {len(BLOQUES)} bloques, "
              f'{len(VERSIONES)} versión/es)')
    print('\nAcuérdate de `python3 sitemap.py` y, después de empujar, `python3 indexnow.py`.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
