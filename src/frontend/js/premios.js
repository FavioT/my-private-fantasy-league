const API = "";
const SEASON_YEAR = 2026;
const COMPARE_YEAR = 2025;

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function metricHtml(metric) {
  return `<span class="metric-badge">${escapeHtml(metric.label)}: ${escapeHtml(metric.value)}</span>`;
}

function winnerNameHtml(player) {
  if (!player) return '<p class="winner-name nes-text is-disabled">Sin ganador</p>';

  const name = escapeHtml(player.name);
  if (player.player_id) {
    return `<a class="winner-link" href="/player-detail.html?id=${encodeURIComponent(player.player_id)}"><p class="winner-name">${name}</p></a>`;
  }

  return `<p class="winner-name">${name}</p>`;
}

function finalistsHtml(finalists) {
  if (!finalists || !finalists.length) return "";

  return `
    <div class="finalists">
      <p class="finalists-title">FINALISTAS</p>
      ${finalists.map((f, i) => `
        <p class="finalist-item">${i + 2}. ${escapeHtml(f.name)} (${escapeHtml(f.team_name || "-")})</p>
      `).join("")}
    </div>
  `;
}

function renderAwardCard(award) {
  const theme = escapeHtml(award.theme || "blue");
  const reason = award.reason ? `<p class="winner-reason">${escapeHtml(award.reason)}</p>` : "";
  const metrics = (award.metrics || []).map(metricHtml).join("");

  if (!award.available) {
    return `
      <article class="award-card ${theme}">
        <div class="award-header">
          <div>
            <p class="award-title">${escapeHtml(award.title)}</p>
            <p class="award-subtitle">${escapeHtml(award.subtitle || "")}</p>
          </div>
        </div>
        <p class="winner-name nes-text is-disabled">No disponible</p>
        <p class="winner-reason">${escapeHtml(award.unavailable_reason || "Sin datos suficientes para calcular este premio.")}</p>
      </article>
    `;
  }

  return `
    <article class="award-card ${theme}">
      <div class="award-header">
        <div>
          <p class="award-title">${escapeHtml(award.title)}</p>
          <p class="award-subtitle">${escapeHtml(award.subtitle || "")}</p>
        </div>
      </div>

      ${winnerNameHtml(award.winner)}
      <div class="metrics-row">${metrics}</div>
      ${reason}
      ${finalistsHtml(award.finalists)}
    </article>
  `;
}

function setLoadingState() {
  document.getElementById("awards-loading").style.display = "block";
  document.getElementById("awards-error").style.display = "none";
  document.getElementById("awards-empty").style.display = "none";
  document.getElementById("awards-content").style.display = "none";
}

function setErrorState(message) {
  const error = document.getElementById("awards-error");
  error.style.display = "block";
  error.innerHTML = `<span class="nes-text is-error">${escapeHtml(message)}</span>`;

  document.getElementById("awards-loading").style.display = "none";
  document.getElementById("awards-empty").style.display = "none";
  document.getElementById("awards-content").style.display = "none";
}

function setEmptyState() {
  document.getElementById("awards-loading").style.display = "none";
  document.getElementById("awards-error").style.display = "none";
  document.getElementById("awards-empty").style.display = "block";
  document.getElementById("awards-content").style.display = "none";
}

function setContentState() {
  document.getElementById("awards-loading").style.display = "none";
  document.getElementById("awards-error").style.display = "none";
  document.getElementById("awards-empty").style.display = "none";
  document.getElementById("awards-content").style.display = "block";
}

async function loadAwards() {
  setLoadingState();

  try {
    const response = await fetch(`${API}/api/analytics/season/${SEASON_YEAR}/awards?compare_year=${COMPARE_YEAR}`);
    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || `Error HTTP ${response.status}`);
    }

    const awards = data.awards || [];
    if (!awards.length) {
      setEmptyState();
      return;
    }

    document.getElementById("season-pill").textContent = `SEASON ${data.year || SEASON_YEAR}`;
    document.getElementById("compare-pill").textContent = `VS ${data.compare_year || COMPARE_YEAR}`;

    const grid = document.getElementById("awards-grid");
    grid.innerHTML = awards.map(renderAwardCard).join("");

    const methodologyList = document.getElementById("methodology-list");
    const notes = data.methodology_notes || [];
    methodologyList.innerHTML = notes.map(note => `<li>${escapeHtml(note)}</li>`).join("");

    setContentState();
  } catch (error) {
    console.error(error);
    setErrorState("No se pudieron cargar los premios de la temporada 2026.");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("reload-btn").addEventListener("click", loadAwards);
  loadAwards();
});

