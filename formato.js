/*
 * Formulario de envío de formatos, en las dos lenguas.
 *
 * Los textos se eligen por el `lang` del documento en vez de venir en un bloque incrustado en cada
 * página: así el fichero es uno solo, y la CSP puede prohibir el script en línea sin excepciones.
 *
 * Ojo con una cosa: el `value` de cada tipo de operación va en español también en la página
 * inglesa. El Worker valida contra una lista cerrada de valores en español y es el que acaba
 * escribiendo el issue, así que traducir el `value` haría que todo envío en inglés se rechazara.
 */
(function () {
  var TEXTOS = {
    es: {
      cifras: function (n) {
        return 'Hay ' + n + ' cifra(s) en el texto. Sustitúyelas por marcadores antes de enviarlo.';
      },
      enviando: 'Enviando…',
      enviar: 'Enviar el formato',
      gracias: '¡Recibido, gracias! Si tu banco acaba soportado, podrás recuperar los avisos que ya '
             + 'tengas guardados con el botón «Reprocesar» de Ajustes.',
      sinRed: 'No se pudo conectar. Revisa tu conexión e inténtalo otra vez.',
      generico: 'No se pudo enviar. Inténtalo más tarde.',
      captcha: 'No se pudo verificar que no eres un robot. Recarga la página e inténtalo otra vez.',
      captcha_sin_token: 'Marca antes la casilla de verificación.',
      limite: 'Has enviado varios formatos en poco tiempo. Prueba dentro de un rato.',
      plantilla_con_cifras: 'La plantilla lleva números. Sustitúyelos por marcadores.',
      plantilla_corta: 'La plantilla es demasiado corta.',
      paquete: 'El identificador de la app no tiene la forma esperada (algo como com.ejemplo.banca).',
      entidad: 'Falta el nombre del banco o de la aplicación.',
      tipo: 'Elige qué tipo de operación es.'
    },
    en: {
      cifras: function (n) {
        return 'There are ' + n + ' digit(s) in the text. Replace them with placeholders before sending.';
      },
      enviando: 'Sending…',
      enviar: 'Send the format',
      gracias: 'Got it, thank you! If your bank ends up supported, you will be able to recover the '
             + 'alerts you already have stored with the "Reprocess" button in Settings.',
      sinRed: 'Could not connect. Check your connection and try again.',
      generico: 'Could not send it. Please try again later.',
      captcha: 'We could not verify that you are not a robot. Reload the page and try again.',
      captcha_sin_token: 'Tick the verification box first.',
      limite: 'You have sent several formats in a short time. Try again in a while.',
      plantilla_con_cifras: 'The template contains numbers. Replace them with placeholders.',
      plantilla_corta: 'The template is too short.',
      paquete: 'The application id is not in the expected shape (something like com.example.bank).',
      entidad: 'The bank or application name is missing.',
      tipo: 'Choose which kind of operation it is.'
    }
  };

  var t = TEXTOS[document.documentElement.lang] || TEXTOS.es;
  var form = document.getElementById('formulario');
  var plantilla = document.getElementById('plantilla');
  var avisoCifras = document.getElementById('avisoCifras');
  var resultado = document.getElementById('resultado');
  var boton = document.getElementById('enviar');

  // Prellenado desde la app: xtracto.app/formato.html?paquete=...&plantilla=...
  var params = new URLSearchParams(location.search);
  ['entidad', 'paquete', 'plantilla'].forEach(function (campo) {
    var valor = params.get(campo);
    if (valor) document.getElementById(campo).value = valor;
  });

  // Aviso en vivo. Esto es comodidad para quien escribe, NO la defensa: la comprobación que manda
  // es la del servidor, porque cualquiera puede saltarse el JavaScript de una página.
  function revisarCifras() {
    var cifras = (plantilla.value.match(/\d/g) || []).length;
    if (cifras > 0) {
      avisoCifras.className = 'alerta mal';
      avisoCifras.textContent = t.cifras(cifras);
    } else {
      avisoCifras.className = 'alerta';
      avisoCifras.textContent = '';
    }
    return cifras === 0;
  }
  plantilla.addEventListener('input', revisarCifras);
  if (plantilla.value) revisarCifras();

  function reactivar() {
    boton.disabled = false;
    boton.textContent = t.enviar;
  }

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();
    resultado.className = 'alerta';

    if (!revisarCifras()) {
      resultado.className = 'alerta mal';
      resultado.textContent = t.plantilla_con_cifras;
      return;
    }

    var captcha = form.querySelector('[name="cf-turnstile-response"]');
    boton.disabled = true;
    boton.textContent = t.enviando;

    fetch('https://api.xtracto.app/formato', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        entidad: document.getElementById('entidad').value,
        paquete: document.getElementById('paquete').value,
        plantilla: plantilla.value,
        tipo: document.getElementById('tipo').value,
        web: document.getElementById('web').value,
        turnstile: captcha ? captcha.value : ''
      })
    }).then(function (respuesta) {
      return respuesta.json();
    }).then(function (datos) {
      if (datos.ok) {
        form.style.display = 'none';
        resultado.className = 'alerta bien';
        resultado.style.display = 'block';
        resultado.textContent = t.gracias;
        form.parentNode.appendChild(resultado);
      } else {
        resultado.className = 'alerta mal';
        resultado.textContent = t[datos.motivo] || t.generico;
        reactivar();
        if (window.turnstile) window.turnstile.reset();
      }
    }).catch(function () {
      resultado.className = 'alerta mal';
      resultado.textContent = t.sinRed;
      reactivar();
    });
  });
})();
