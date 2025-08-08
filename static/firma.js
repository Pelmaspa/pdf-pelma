
function getFormData() {
  const inputs = document.querySelectorAll('input, textarea');
  const data = {};
  inputs.forEach(el => {
    if (el.type !== 'button' && el.name !== '') data[el.placeholder || el.name || el.type] = el.value;
  });
  return data;
}

function getCanvasImage(id) {
  const canvas = document.getElementById(id);
  return canvas ? canvas.toDataURL() : null;
}

function inviaModulo(modulo) {
  const campi = getFormData();
  const firma1 = getCanvasImage('firma1') || getCanvasImage('signature-pad');
  const firma2 = getCanvasImage('firma2');

  fetch('/invia_modulo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ campi, firma1, firma2, modulo })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      alert('Modulo inviato con successo!');
      window.location.reload();
    } else {
      alert('Errore durante l\'invio.');
    }
  })
  .catch(err => alert('Errore di connessione: ' + err));
}
