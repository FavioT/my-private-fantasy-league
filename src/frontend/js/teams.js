const API = '';

function rankBadge(i) {
  if (i === 0) return '<span class="rank-gold">1</span>';
  if (i === 1) return '<span class="rank-silver">2</span>';
  if (i === 2) return '<span class="rank-bronze">3</span>';
  return String(i + 1);
}

function switchTab(tab, event) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  if (event && event.target) event.target.closest('.tab-button').classList.add('active');
}

async function loadOwners() {
  const container = document.getElementById('owners-list');
  try {
    const res = await fetch(`${API}/api/analytics/owner-stats`);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const owners = await res.json();

    if (!owners.length) {
      container.innerHTML = '<span class="nes-text is-disabled">Sin datos.</span>';
      return;
    }

    const maxWins = Math.max(...owners.map(o => o.total_wins));

    container.innerHTML = `<div class="data-list">${owners.map((o, i) => {
      const pct = (o.win_percentage * 100).toFixed(1);
      const barPct = maxWins > 0 ? Math.round((o.total_wins / maxWins) * 100) : 0;
      const champs = o.championships > 0
        ? ' · ' + '<i class="nes-icon trophy is-small"></i>'.repeat(o.championships)
        : '';
      return `<div class="data-row clickable" role="link" tabindex="0"
          onclick="window.location.href='/owner-detail.html?owner=${encodeURIComponent(o.owner)}'"
          onkeydown="if(event.key==='Enter')window.location.href='/owner-detail.html?owner=${encodeURIComponent(o.owner)}'">
        <div class="dr-rank">${rankBadge(i)}</div>
        <div class="dr-main">
          <div class="dr-name">${o.owner}</div>
          <div class="dr-sub">${o.seasons_played} temporadas${champs}</div>
        </div>
        <div class="dr-stats">
          <div class="dr-stat">
            <span class="dr-stat-val nes-text is-success">${o.total_wins}</span>
            <span class="dr-stat-lbl">W</span>
          </div>
          <div class="dr-stat">
            <span class="dr-stat-val nes-text is-error">${o.total_losses}</span>
            <span class="dr-stat-lbl">L</span>
          </div>
          <div class="dr-stat">
            <span class="dr-stat-val nes-text is-primary">${pct}%</span>
            <span class="dr-stat-lbl">WIN%</span>
          </div>
          <div class="wins-bar-bg">
            <div class="wins-bar-fill" style="width:${barPct}%"></div>
          </div>
        </div>
      </div>`;
    }).join('')}</div>`;
  } catch (e) {
    container.innerHTML = '<span class="nes-text is-error">Error cargando owners.</span>';
    console.error(e);
  }
}

async function loadCurrentSeason() {
  const container = document.getElementById('season-list');
  try {
    const res = await fetch(`${API}/api/analytics/season/2026`);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    const teams = (data.teams || []).slice().sort((a, b) => b.wins - a.wins);
    if (!teams.length) {
      container.innerHTML = '<span class="nes-text is-disabled">Sin datos.</span>';
      return;
    }

    const champName = data.playoff_champion || '';
    const maxWins = teams[0].wins;

    container.innerHTML = `<div class="data-list">${teams.map((t, i) => {
      const isChamp = champName && (
        t.team_name === champName ||
        t.team_name.toLowerCase().includes(champName.toLowerCase()) ||
        champName.toLowerCase().includes(t.team_name.toLowerCase())
      );
      const champBadge = isChamp ? ' <i class="nes-icon trophy is-small"></i>' : '';
      const barPct = maxWins > 0 ? Math.round((t.wins / maxWins) * 100) : 0;
      const pts = t.points_for ? Math.round(t.points_for) : '—';
      return `<div class="data-row">
        <div class="dr-rank">${rankBadge(i)}</div>
        <div class="dr-main">
          <div class="dr-name">${t.team_name}${champBadge}</div>
          <div class="dr-sub">${t.owner || ''}</div>
        </div>
        <div class="dr-stats">
          <div class="dr-stat">
            <span class="dr-stat-val nes-text is-success">${t.wins}</span>
            <span class="dr-stat-lbl">W</span>
          </div>
          <div class="dr-stat">
            <span class="dr-stat-val nes-text is-error">${t.losses}</span>
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
  } catch (e) {
    container.innerHTML = '<span class="nes-text is-error">Error cargando temporada.</span>';
    console.error(e);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadOwners();
  loadCurrentSeason();
});
