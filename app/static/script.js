const form = document.getElementById('upload-form');
const input = document.getElementById('pdf-input');
const statusEl = document.getElementById('status');
const summary = document.getElementById('summary');
const results = document.getElementById('results');
const downloadLink = document.getElementById('download-link');
const fileLabel = document.getElementById('file-label');

input.addEventListener('change', () => {
  const file = input.files?.[0];
  fileLabel.textContent = file ? file.name : 'Escolha um PDF';
});

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const file = input.files?.[0];
  if (!file) {
    statusEl.textContent = 'Selecione um PDF primeiro.';
    return;
  }

  statusEl.textContent = 'Processando... extraindo páginas e calculando acordes.';
  results.hidden = true;
  summary.innerHTML = '';

  const data = new FormData();
  data.append('pdf', file);

  try {
    const resp = await fetch('/api/process', { method: 'POST', body: data });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'Erro no processamento');
    }

    const payload = await resp.json();
    statusEl.textContent = 'Pronto! Sua partitura foi harmonizada.';

    payload.resumo.forEach(item => {
      const div = document.createElement('div');
      div.className = 'result-item';
      div.innerHTML = `<strong>Página ${item.pagina}</strong>: ${item.acordes.join(' · ')}`;
      summary.appendChild(div);
    });

    downloadLink.href = payload.download_url;
    downloadLink.hidden = false;
    results.hidden = false;
  } catch (err) {
    console.error(err);
    statusEl.textContent = `Falha: ${err.message}`;
  }
});
