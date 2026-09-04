/*
 * Petición de entrada en la prueba cerrada, en las dos lenguas.
 *
 * **No envía nada.** A diferencia de `formato.js` y de `banco.js`, aquí no hay `fetch`, ni captcha,
 * ni endpoint: el botón compone un `mailto:` y lo abre en el programa de correo de quien lo pulsa,
 * que es quien manda el mensaje. La razón es que el dato que hace falta —la dirección de la cuenta de
 * Google, sin la cual Play no puede dar de alta a un tester— es el único dato personal de todo el
 * proyecto, y recibirlo por correo en vez de por un formulario significa que este sitio no lo recoge,
 * no lo valida, no lo guarda y no tiene dónde perderlo. También deja estas dos páginas **sin un solo
 * origen externo**, ni siquiera el de Turnstile, que es lo que dice la portada del resto del sitio.
 *
 * La comprobación de la dirección de aquí es solo comodidad, y esta vez de verdad: no hay servidor
 * detrás que valide nada. Sirve para no abrir el correo con un campo a medias.
 */
(function () {
  var TEXTOS = {
    es: {
      marcador: '<tu dirección>',
      asunto: 'Alta en la prueba cerrada de Xtracto',
      cuerpo: function (correo) {
        return 'Hola: quiero entrar en la prueba cerrada de Xtracto.\n'
             + 'Mi cuenta de Google es: ' + correo + '\n';
      },
      abierto: 'Se ha abierto tu programa de correo con el mensaje escrito. Repásalo y mándalo: hasta '
             + 'que no lo mandes tú, aquí no ha salido nada.',
      correo: 'Eso no tiene forma de dirección de correo. Escribe una sola, sin nombre ni signos '
            + 'alrededor.'
    },
    en: {
      marcador: '<your address>',
      asunto: 'Xtracto closed test — please enrol me',
      cuerpo: function (correo) {
        return 'Hello: I would like to join the Xtracto closed test.\n'
             + 'My Google account is: ' + correo + '\n';
      },
      abierto: 'Your mail app has opened with the message written. Check it over and send it: until '
             + 'you send it yourself, nothing has left this page.',
      correo: 'That is not shaped like an email address. Write a single one, with no name or symbols '
            + 'around it.'
    }
  };

  // La misma forma que valida el Worker en los otros formularios: una sola dirección, sin espacios,
  // sin comas ni signos de cabecera, y con un dominio con al menos un punto.
  var FORMA = /^[^\s@,;:<>()[\]\\"]+@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+$/;

  var t = TEXTOS[document.documentElement.lang] || TEXTOS.es;
  var form = document.getElementById('formulario');
  var campo = document.getElementById('correo');
  var vista = document.getElementById('vista-correo');
  var resultado = document.getElementById('resultado');

  // La vista previa enseña lo que va a salir mientras se escribe, igual que hace la app antes de
  // compartir un formato. `textContent` y no `innerHTML`: lo que se teclea es texto, no marcado.
  campo.addEventListener('input', function () {
    var valor = campo.value.trim();
    vista.textContent = valor || t.marcador;
    vista.className = valor ? '' : 'marcador';
  });

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();
    var correo = campo.value.trim();

    if (!FORMA.test(correo)) {
      resultado.className = 'alerta mal';
      resultado.textContent = t.correo;
      campo.focus();
      return;
    }

    resultado.className = 'alerta bien';
    resultado.style.display = 'block';
    resultado.textContent = t.abierto;

    window.location.href = 'mailto:support@xtracto.app'
      + '?subject=' + encodeURIComponent(t.asunto)
      + '&body=' + encodeURIComponent(t.cuerpo(correo));
  });
})();
