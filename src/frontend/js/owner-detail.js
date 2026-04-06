const API = '';

function rankBadge(i) {
  if (i === 0) return '<span style="background:#f7d51d;color:#000;padding:2px 5px;border:2px solid #000;font-size:0.4rem;">1</span>';
  if (i === 1) return '<span style="background:#ccc;color:#000;padding:2px 5px;border:2px solid #000;font-size:0.4rem;">2</span>';
  if (i === 2) return '<span style="background:#cd7f32;color:#fff;padding:2px 5px;border:2px solid #000;font-size:0.4rem;">3</span>';
  return String(i + 1);
}

async function init() {
  const params = new URLSearchParams(location.search);
  const owner = params.get('owner');

  if (!owner) {
    document.getElementById('loading').style.display = 'none';
    const errEl = document.getElementById('error-msg');
    errEl.textContent = 'Owner no especificado.';
    errEl.style.display = 'block';
    return;
  }

  const displayName = decodeURIComponent(owner);
  document.title = `${displayName} - Andate Silver`;
  document.getElementById('owner-name').textContent = displayName;

  try {
    const [historyRes, playersRes, champsRes] = await Promise.all([
      fetch(`${API}/api/analytics/owner/${encodeURIComponent(owner)}`),
      fetch(`${API}/api/analytics/owner/${encodeURIComponent(owner)}/top-players`),
      fetch(`${API}/api/analytics/champions`)
    ]);

    const history = historyRes.ok ? await historyRes.json() : null;
    const players = playersRes.ok ? await playersRes.json() : [];
    const champs  = champsRes.ok  ? await champsRes.json()  : [];

    const champYears = new Set(
      champs
        .filter(c => c.owner && c.owner.toLowerCase() === owner.toLowerCase())
        .map(c => c.year)
    );

    renderSummaryCards(history, champYears);
    renderSeasonHistory(history, champYears);
    renderTopPlayers(players);

    if (history) {
      document.getElementById('owner-subtitle').textContent =
        `${history.seasons} temporada${history.seasons !== 1 ? 's' : ''} · ${history.total_wins}W ${history.total_losses}L`;
    }
  } catch (e) {
    console.error(e);
    document.getElementById('loading').style.display = 'none';
    const errEl = document.getElementById('error-msg');
    errEl.textContent = 'Error al cargar los datos del owner.';
    errEl.style.display = 'block';
    return;
  }

  document.getElementById('loading').style.display = 'none';
  document.getElementById('owner-content').style.display = 'block';
}

function renderSummaryCards(data, champYears) {
  if (!data) return;
  const pct = (data.win_percentage * 100).toFixed(1);
  document.getElementById('stat-seasons').textContent = data.seasons;
  document.getElementById('stat-wins').textContent    = data.total_wins;
  document.getElementById('stat-pct').textContent     = pct + '%';
  document.getElementById('stat-champs').textContent  = champYears.size;
}

function renderSeasonHistory(data, champYears) {
  const container = document.getElementById('season-history');
  if (!data || !data.history || !data.history.length) {
    container.innerHTML = '<span class="nes-text is-disabled">Sin datos.</span>';
    return;
  }

  const maxPts = Math.max(...data.history.map(h => h.points_for || 0));

  container.innerHTML = `<div class="data-list">${data.history.map(h => {
    const isChamp = champYears.has(h.year);
    const champBadge = isChamp ? ' <i class="nes-icon trophy is-small"></i>' : '';
    const barPct = maxPts > 0 ? Math.round((h.points_for / maxPts) * 100) : 0;
    const pts = h.points_for ? Math.round(h.points_for) : '—';
    const rowClass = isChamp ? 'data-row champ-row' : 'data-row';
    return `<div class="${rowClass}">
      <div class="dr-rank">
        <span class="year-badge">${h.year}</span>
      </div>
      <div class="dr-main">
        <div class="dr-name">${h.team_name}${champBadge}</div>
        <div class="dr-sub">${h.wins}W · ${h.losses}L · ${pts} pts</div>
      </div>
      <div class="dr-stats">
        <div class="dr-stat">
          <span class="dr-stat-val nes-text is-success">${h.wins}</span>
          <span class="dr-stat-lbl">W</span>
        </div>
        <div class="dr-stat">
          <span class="dr-stat-val nes-text is-error">${h.losses}</span>
          <span class="dr-stat-lbl">L</span>
        </div>
        <div class="dr-stat">
          <span class="dr-stat-val">${pts}</span>
          <span class="dr-stat-lbl">PTS</span>
        </div>
        <div class="wins-bar-bg">
          <div class="wins-bar-fill" style="width:${barPct}%"></div>
        </div>
      </div>
    </div>`;
  }).join('')}</div>`;
}

function renderTopPlayers(players) {
  const container = document.getElementById('top-players');
  if (!players || !players.length) {
    container.innerHTML = '<span class="nes-text is-disabled">Sin jugadores registrados.</span>';
    return;
  }

  container.innerHTML = `<div class="data-list">${players.map((p, i) => {
    const sub = [p.position, p.proTeam, p.seasons_owned > 1 ? `${p.seasons_owned} temp.` : '1 temp.']
      .filter(Boolean).join(' · ');
    return `<div class="data-row">
      <div class="dr-rank">${rankBadge(i)}</div>
      <div class="dr-main">
        <div class="dr-name">${p.name}</div>
        <div class="dr-sub">${sub}</div>
      </div>
      <div class="dr-stats">
        <div class="dr-stat">
          <span class="dr-stat-val nes-text is-primary">${Math.round(p.total_points)}</span>
          <span class="dr-stat-lbl">TOTAL</span>
        </div>
        <div class="dr-stat">
          <span class="dr-stat-val">${p.best_avg.toFixed(1)}</span>
          <span class="dr-stat-lbl">AVG</span>
        </div>
      </div>
    </div>`;
  }).join('')}</div>`;
}

document.addEventListener('DOMContentLoaded', init);
