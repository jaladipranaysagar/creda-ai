const form = document.querySelector('#scan-form');
const content = document.querySelector('#content');
const button = document.querySelector('#scan-button');
const result = document.querySelector('#result');
const emptyState = document.querySelector('#empty-state');

function escapeHtml(text) {
  const node = document.createElement('div');
  node.textContent = text;
  return node.innerHTML;
}

function showResult(data) {
  emptyState.classList.add('hidden'); result.classList.remove('hidden');
  document.querySelector('#score').textContent = data.score;
  document.querySelector('#risk-level').textContent = `${data.risk_level} risk`;
  document.querySelector('#category').textContent = data.category;
  document.querySelector('#summary').textContent = data.summary;
  document.querySelector('#findings').innerHTML = data.findings.length
    ? data.findings.map(f => `<div class="finding"><strong>${escapeHtml(f.label)}</strong><span>+${f.points}</span><p>${escapeHtml(f.detail)}</p></div>`).join('')
    : '<p class="muted">Keep using normal online-safety habits; an absence of signals is not a guarantee.</p>';
}

async function loadHistory() {
  const holder = document.querySelector('#history');
  try {
    const response = await fetch('/api/scans'); const items = await response.json();
    holder.innerHTML = items.length ? items.map(item => `<div class="history-item"><span class="risk-badge ${item.risk_level}">${item.risk_level} · ${item.score}</span><span class="history-content">${escapeHtml(item.content)}</span><time class="history-date">${new Date(item.created_at).toLocaleString()}</time></div>`).join('') : '<p class="muted">No scans yet. Your checks will be saved here.</p>';
  } catch { holder.innerHTML = '<p class="muted">History is temporarily unavailable.</p>'; }
}

form.addEventListener('submit', async event => {
  event.preventDefault(); button.disabled = true; button.innerHTML = 'Analyzing… <span>◌</span>';
  try {
    const response = await fetch('/api/scans', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({content: content.value})});
    if (!response.ok) throw new Error(); showResult(await response.json()); loadHistory();
  } catch { alert('The scan could not be completed. Please try again.'); }
  finally { button.disabled = false; button.innerHTML = 'Analyze for risk <span>→</span>'; }
});
document.querySelector('#refresh-history').addEventListener('click', loadHistory);
loadHistory();

