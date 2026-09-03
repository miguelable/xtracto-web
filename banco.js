/*
 * Formulario de alta de banco, en las dos lenguas.
 *
 * Va aparte de `formato.js` y no como una rama suya porque son dos envíos distintos: aquí no hay
 * plantilla, y por tanto tampoco el aviso en vivo de cifras que es la mitad de ese fichero. Los
 * textos se eligen por el `lang` del documento, igual que allí, para que la CSP pueda seguir
 * prohibiendo el script en línea sin excepciones.
 *
 * El país se manda tal cual lo escribe la persona. El Worker lo valida contra letras y espacios, y
 * ahí está la defensa: la comprobación del navegador es comodidad, no seguridad.
 */
(function () {
  var TEXTOS = {
    es: {
      enviando: 'Enviando…',
      enviar: 'Pedir este banco',
      gracias: '¡Recibido, gracias! Cada identificador se comprueba a mano antes de entrar en el '
             + 'catálogo, así que puede tardar. Cuando tu banco esté, aparecerá en Ajustes para que '
             + 'lo enciendas.',
      enEspera: 'Recibido y guardado, gracias. Ahora mismo no se ha podido publicar, así que se '
              + 'publicará solo en cuanto se pueda. No hace falta que lo envíes otra vez.',
      sinRed: 'No se pudo conectar. Revisa tu conexión e inténtalo otra vez.',
      generico: 'No se pudo enviar. Inténtalo más tarde.',
      captcha: 'No se pudo verificar que no eres un robot. Recarga la página e inténtalo otra vez.',
      captcha_sin_token: 'Marca antes la casilla de verificación.',
      limite: 'Has enviado varias peticiones en poco tiempo. Prueba dentro de un rato.',
      entidad: 'Falta el nombre del banco o de la aplicación.',
      pais: 'El país solo puede llevar letras. Escríbelo sin números ni signos.',
      paquete: 'El identificador de la app no tiene la forma esperada (algo como com.ejemplo.banca). '
             + 'Si no lo sabes, déjalo vacío.',
      ruta: 'No se pudo enviar. Inténtalo más tarde.'
    },
    en: {
      enviando: 'Sending…',
      enviar: 'Request this bank',
      gracias: 'Got it, thank you! Every identifier is checked by hand before it enters the '
             + 'catalogue, so it may take a while. Once your bank is in, it will show up in '
             + 'Settings for you to switch on.',
      enEspera: 'Received and stored, thank you. It could not be published right now, so it will be '
              + 'published on its own as soon as possible. No need to send it again.',
      sinRed: 'Could not connect. Check your connection and try again.',
      generico: 'Could not send it. Please try again later.',
      captcha: 'We could not verify that you are not a robot. Reload the page and try again.',
      captcha_sin_token: 'Tick the verification box first.',
      limite: 'You have sent several requests in a short time. Try again in a while.',
      entidad: 'The bank or application name is missing.',
      pais: 'The country can only contain letters. Write it without numbers or symbols.',
      paquete: 'The application id is not in the expected shape (something like com.example.bank). '
             + 'If you do not know it, leave it empty.',
      ruta: 'Could not send it. Please try again later.'
    }
  };

  var t = TEXTOS[document.documentElement.lang] || TEXTOS.es;
  var form = document.getElementById('formulario');
  var resultado = document.getElementById('resultado');
  var boton = document.getElementById('enviar');

  // Prellenado desde la app: xtracto.app/pide-tu-banco.html?entidad=...&paquete=...
  var params = new URLSearchParams(location.search);
  ['entidad', 'pais', 'paquete'].forEach(function (campo) {
    var valor = params.get(campo);
    if (valor) document.getElementById(campo).value = valor;
  });

  function reactivar() {
    boton.disabled = false;
    boton.textContent = t.enviar;
  }

  form.addEventListener('submit', function (evento) {
    evento.preventDefault();
    resultado.className = 'alerta';

    var captcha = form.querySelector('[name="cf-turnstile-response"]');
    boton.disabled = true;
    boton.textContent = t.enviando;

    fetch('https://api.xtracto.app/banco', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        entidad: document.getElementById('entidad').value,
        pais: document.getElementById('pais').value,
        paquete: document.getElementById('paquete').value,
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
        resultado.textContent = datos.estado === 'en_espera' ? t.enEspera : t.gracias;
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
