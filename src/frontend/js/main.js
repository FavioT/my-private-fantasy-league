// ============================================================
// Dashboard principal – datos históricos 2020-2026
// ============================================================

const API = "";

let currentYear = "all";

// ============================================================
// Utilidades UI
// ============================================================

function showLoading(sectionId) {
  const loading = document.getElementById(`${sectionId}-loading`);
  const content = document.getElementById(`${sectionId}-content`);
  if (loading) loading.style.display = "block";
  if (content) content.style.display = "none";
}

function showContent(sectionId) {
  const loading = document.getElementById(`${sectionId}-loading`);
  const content = document.getElementById(`${sectionId}-content`);
  if (loading) loading.style.display = "none";
  if (content) content.style.display = "block";
}

function showError(sectionId, msg) {
  const loading = document.getElementById(`${sectionId}-loading`);
  if (loading) loading.innerHTML = `<span class="nes-text is-error">✖ ${msg}</span>`;
}

function rankMedal(i) {
  if (i === 0) return `<span style="background:#f7d51d;padding:2px 5px;border:2px solid #000;font-size:0.45rem;">1</span>`;
  if (i === 1) return `<span style="background:#c0c0c0;padding:2px 5px;border:2px solid #000;font-size:0.45rem;">2</span>`;
  if (i === 2) return `<span style="background:#cd7f32;padding:2px 5px;border:2px solid #000;font-size:0.45rem;">3</span>`;
  return `${i + 1}`;
}

// ============================================================
// Selector de año
// ============================================================

function selectYear(year) {
  currentYear = year;
  document.querySelectorAll(".year-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.year === year);
  });
  loadAll();
}

// ============================================================
// Carga principal
// ============================================================

async function loadAll() {
  if (currentYear === "all") {
    await Promise.all([
      loadAllYearsChampions(),
      loadAllYearsTopScorers(),
      loadAllYearsOwnerStats(),
    ]);
  } else {
    const yr = parseInt(currentYear);
    await Promise.all([
      loadSeasonStandings(yr),
      loadSeasonTopScorers(yr),
      loadSeasonOwnerStats(yr),
    ]);
  }
}

// ============================================================
// VISTA MULTI-AÑO
// ============================================================

async function loadAllYearsChampions() {
  showLoading("champions");
  document.getElementById("champions-title").textContent = "Campeones";

  try {
    const res = await fetch(`${API}/api/analytics/champions`);
    const data = await res.json();

    document.getElementById("card-seasons").textContent = String(data.length);

    if (data.length > 0) {
      const last = data[data.length - 1];
      document.getElementById("card-champion").textContent = last.team_name;
      document.getElementById("card-champion-label").textContent = `CAMPEÓN ${last.year}`;
    }

    const tbody = document.getElementById("champions-body");
    tbody.innerHTML = "";
    [...data].reverse().forEach(entry => {
      const row = document.createElement("div");
      row.className = "data-row";
      row.innerHTML = `
        <span class="dr-rank"><span style="background:#f7d51d;padding:1px 4px;border:2px solid #000;font-size:0.4rem;">${entry.year}</span></span>
        <div class="dr-main">
          <div class="dr-name">${entry.team_name}</div>
          <div class="dr-sub">${entry.owner || "—"}</div>
        </div>
        <div class="dr-stats">
          <span class="dr-stat"><span class="dr-stat-val nes-text is-success">${entry.wins}</span><span class="dr-stat-lbl">W</span></span>
          <span class="dr-stat"><span class="dr-stat-val nes-text is-error">${entry.losses}</span><span class="dr-stat-lbl">L</span></span>
        </div>
      `;
      tbody.appendChild(row);
    });

    showContent("champions");
  } catch (e) {
    showError("champions", "Error al cargar campeones");
  }
}

async function loadAllYearsTopScorers() {
  showLoading("scorers");
  document.getElementById("scorers-title").textContent = "Top Scorers";

  try {
    const res = await fetch(`${API}/api/analytics/top-scorers?limit=12`);
    const data = await res.json();

    if (data.length > 0) {
      document.getElementById("card-top-scorer").textContent = data[0].name;
      document.getElementById("card-top-scorer-label").textContent =
        `TOP SCORER (${data[0].total_points.toFixed(1)} pts tot.)`;
    }

    const tbody = document.getElementById("scorers-body");
    tbody.innerHTML = "";
    data.forEach((player, i) => {
      const row = document.createElement("div");
      row.className = "data-row";
      row.innerHTML = `
        <span class="dr-rank">${rankMedal(i)}</span>
        <div class="dr-main">
          <div class="dr-name">${player.name}</div>
          <div class="dr-sub">${player.proTeam || ""}${player.seasons ? ` · ${player.seasons} temp.` : ""}</div>
        </div>
        <div class="dr-stats">
          <span class="dr-stat"><span class="dr-stat-val nes-text is-primary">${player.total_points.toFixed(1)}</span><span class="dr-stat-lbl">PTS</span></span>
        </div>
      `;
      tbody.appendChild(row);
    });

    showContent("scorers");
  } catch (e) {
    showError("scorers", "Error al cargar top scorers");
  }
}

async function loadAllYearsOwnerStats() {
  showLoading("owners");

  try {
    const res = await fetch(`${API}/api/analytics/owner-stats`);
    const data = await res.json();

    const topWinner = data.reduce((best, o) => o.total_wins > best.total_wins ? o : best, data[0]);
    const cardTeams = document.getElementById("card-teams");
    cardTeams.textContent = topWinner.owner;
    cardTeams.style.fontSize = "0.65rem";
    document.getElementById("card-teams-label").textContent = `MÁS VICTORIAS (${topWinner.total_wins} W)`;

    const tbody = document.getElementById("owners-body");
    tbody.innerHTML = "";
    data.forEach((owner, i) => {
      const pct = (owner.win_percentage * 100).toFixed(1);
      const champs = owner.championships > 0
        ? `${'<i class="nes-icon trophy is-small"></i>'.repeat(owner.championships)}`
        : "";

      const row = document.createElement("div");
      row.className = "data-row";
      row.innerHTML = `
        <span class="dr-rank">${rankMedal(i)}</span>
        <div class="dr-main">
          <div class="dr-name">${owner.owner}${champs ? ` <span class="nes-text is-warning" style="font-size:0.38rem;">${champs}</span>` : ""}</div>
          <div class="dr-sub">${owner.seasons_played} temp. · ${pct}%</div>
        </div>
        <div class="dr-stats">
          <span class="dr-stat"><span class="dr-stat-val nes-text is-success">${owner.total_wins}</span><span class="dr-stat-lbl">W</span></span>
          <span class="dr-stat"><span class="dr-stat-val nes-text is-error">${owner.total_losses}</span><span class="dr-stat-lbl">L</span></span>
        </div>
      `;
      tbody.appendChild(row);
    });

    showContent("owners");
  } catch (e) {
    showError("owners", "Error al cargar estadísticas de dueños");
  }
}

// ============================================================
// VISTA AÑO ESPECÍFICO
// ============================================================

async function loadSeasonStandings(year) {
  showLoading("champions");
  document.getElementById("champions-title").textContent = `Clasificación ${year}`;

  try {
    const [summaryRes, dataRes] = await Promise.all([
      fetch(`${API}/api/analytics/season/${year}/summary`),
      fetch(`${API}/api/analytics/season/${year}`),
    ]);
    const summary = await summaryRes.json();
    const seasonData = await dataRes.json();

    document.getElementById("card-seasons").textContent = String(year);
    document.getElementById("card-champion").textContent = summary.champion?.team || "—";
    document.getElementById("card-champion-label").textContent = `CAMPEÓN ${year}`;
    document.getElementById("card-teams").textContent = String(summary.total_teams);
    document.getElementById("card-teams-label").textContent = "EQUIPOS";

    const teams = [...(seasonData.teams || [])].sort((a, b) => b.wins - a.wins);
    const champion = summary.champion?.team || "";

    const tbody = document.getElementById("champions-body");
    tbody.innerHTML = "";
    teams.forEach((team, i) => {
      const isChamp = team.team_name === champion;
      const row = document.createElement("div");
      row.className = "data-row";
      row.innerHTML = `
        <span class="dr-rank">${isChamp ? '<i class="nes-icon trophy is-small"></i>' : rankMedal(i)}</span>
        <div class="dr-main">
          <div class="dr-name">${team.team_name}${isChamp ? ' <span style="font-size:0.36rem;background:#f7d51d;padding:1px 4px;border:2px solid #000;">CAMPEÓN</span>' : ""}</div>
          <div class="dr-sub">${team.owner || "—"}</div>
        </div>
        <div class="dr-stats">
          <span class="dr-stat"><span class="dr-stat-val nes-text is-success">${team.wins}</span><span class="dr-stat-lbl">W</span></span>
          <span class="dr-stat"><span class="dr-stat-val nes-text is-error">${team.losses}</span><span class="dr-stat-lbl">L</span></span>
        </div>
      `;
      tbody.appendChild(row);
    });

    showContent("champions");
  } catch (e) {
    showError("champions", "Error al cargar clasificación");
  }
}

async function loadSeasonTopScorers(year) {
  showLoading("scorers");
  document.getElementById("scorers-title").textContent = `Top Scorers ${year}`;

  try {
    const res = await fetch(`${API}/api/analytics/season/${year}/top-scorers?limit=12`);
    const data = await res.json();

    if (data.length > 0) {
      document.getElementById("card-top-scorer").textContent = data[0].name;
      document.getElementById("card-top-scorer-label").textContent =
        `TOP SCORER ${year} (${data[0].total_points.toFixed(1)} pts tot.)`;
    }

    const tbody = document.getElementById("scorers-body");
    tbody.innerHTML = "";
    data.forEach((player, i) => {
      const row = document.createElement("div");
      row.className = "data-row";
      row.innerHTML = `
        <span class="dr-rank">${rankMedal(i)}</span>
        <div class="dr-main">
          <div class="dr-name">${player.name}</div>
          <div class="dr-sub">${player.proTeam || ""}${player.team ? ` · ${player.team}` : ""}</div>
        </div>
        <div class="dr-stats">
          <span class="dr-stat"><span class="dr-stat-val nes-text is-primary">${player.total_points.toFixed(1)}</span><span class="dr-stat-lbl">PTS</span></span>
        </div>
      `;
      tbody.appendChild(row);
    });

    showContent("scorers");
  } catch (e) {
    showError("scorers", "Error al cargar top scorers");
  }
}

async function loadSeasonOwnerStats(year) {
  showLoading("owners");

  try {
    const res = await fetch(`${API}/api/analytics/season/${year}`);
    const data = await res.json();

    const teams = [...(data.teams || [])].sort((a, b) => b.wins - a.wins);
    const tbody = document.getElementById("owners-body");
    tbody.innerHTML = "";
    teams.forEach((team, i) => {
      const pct = ((team.wins / (team.wins + team.losses)) * 100).toFixed(1);
      const row = document.createElement("div");
      row.className = "data-row";
      row.innerHTML = `
        <span class="dr-rank">${rankMedal(i)}</span>
        <div class="dr-main">
          <div class="dr-name">${team.owner || "—"}</div>
          <div class="dr-sub">${team.team_name || ""} · ${pct}%</div>
        </div>
        <div class="dr-stats">
          <span class="dr-stat"><span class="dr-stat-val nes-text is-success">${team.wins}</span><span class="dr-stat-lbl">W</span></span>
          <span class="dr-stat"><span class="dr-stat-val nes-text is-error">${team.losses}</span><span class="dr-stat-lbl">L</span></span>
        </div>
      `;
      tbody.appendChild(row);
    });

    showContent("owners");
  } catch (e) {
    showError("owners", "Error al cargar datos de la temporada");
  }
}

// ============================================================
// Inicialización
// ============================================================

loadAll();
