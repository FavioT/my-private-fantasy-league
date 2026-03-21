// Configuración de la API
const API_BASE = 'http://localhost:5000';

// Estado global
let currentTab = 'champions';
let availableYears = [];
let selectedYear = null;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', async () => {
  try {
    // Cargar años disponibles
    await loadAvailableYears();
    
    // Cargar datos del tab activo
    await loadTabData(currentTab);
  } catch (error) {
    console.error('Error al inicializar:', error);
    showError('Error al cargar la aplicación');
  }
});

// Cargar años disponibles
async function loadAvailableYears() {
  try {
    const response = await fetch(`${API_BASE}/api/analytics/available-years`);
    const data = await response.json();
    availableYears = data.years || [];
    selectedYear = availableYears[availableYears.length - 2] || availableYears[0]; // Penúltimo año
  } catch (error) {
    console.error('Error al cargar años:', error);
  }
}

// Cambiar de tab
function switchTab(tabName) {
  currentTab = tabName;
  
  // Actualizar botones
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.closest('.tab-button').classList.add('active');
  
  // Actualizar contenido
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });
  document.getElementById(`tab-${tabName}`).classList.add('active');
  
  // Cargar datos del tab
  loadTabData(tabName);
}

// Cargar datos según el tab
async function loadTabData(tabName) {
  try {
    switch (tabName) {
      case 'champions':
        await loadChampions();
        break;
      case 'owners':
        await loadOwnerStats();
        break;
      case 'players':
        await loadTopPlayers();
        break;
      case 'seasons':
        await loadSeasonSelector();
        break;
    }
  } catch (error) {
    console.error(`Error al cargar datos del tab ${tabName}:`, error);
    showError(`Error al cargar ${tabName}`);
  }
}

// Cargar historial de campeones
async function loadChampions() {
  const container = document.getElementById('champions-list');
  container.innerHTML = '<div class="loading">Cargando campeones...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/champions`);
    const champions = await response.json();
    
    if (!champions || champions.length === 0) {
      container.innerHTML = '<p class="nes-text">No hay datos de campeones todavía.</p>';
      return;
    }
    
    let html = '<ul class="champions-list">';
    
    champions.forEach(champ => {
      html += `
        <li class="champion-item">
          <span class="champion-year">🏆 ${champ.year}</span>
          <div class="champion-info">
            <div><strong>${champ.team_name}</strong></div>
            <div style="font-size: 0.45rem; color: #666;">${champ.owner}</div>
          </div>
          <div class="champion-record">
            ${champ.wins}-${champ.losses}<br>
            <span style="font-size: 0.4rem;">${champ.points_for.toFixed(1)} pts</span>
          </div>
        </li>
      `;
    });
    
    html += '</ul>';
    
    // Agregar estadísticas adicionales
    const totalChampionships = {};
    champions.forEach(champ => {
      totalChampionships[champ.owner] = (totalChampionships[champ.owner] || 0) + 1;
    });
    
    const sortedOwners = Object.entries(totalChampionships)
      .sort((a, b) => b[1] - a[1]);
    
    html += '<div class="nes-container is-dark" style="margin-top: 2rem;">';
    html += '<p style="font-size: 0.5rem; margin-bottom: 1rem;">🏅 Campeonatos por Dueño:</p>';
    html += '<div class="stats-grid">';
    
    sortedOwners.forEach(([owner, count], index) => {
      const badge = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
      html += `
        <div class="stat-card">
          <span class="rank-badge ${badge}">${index + 1}</span>
          <strong style="margin-left: 0.5rem;">${owner}</strong>
          <div class="stat-value">${count} ${count === 1 ? 'campeonato' : 'campeonatos'}</div>
        </div>
      `;
    });
    
    html += '</div></div>';
    
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar campeones:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar campeones</div>';
  }
}

// Cargar estadísticas de dueños
async function loadOwnerStats() {
  const container = document.getElementById('owners-stats');
  container.innerHTML = '<div class="loading">Cargando estadísticas...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/owner-stats`);
    const owners = await response.json();
    
    if (!owners || owners.length === 0) {
      container.innerHTML = '<p class="nes-text">No hay datos de dueños todavía.</p>';
      return;
    }
    
    let html = `
      <table class="owner-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Dueño</th>
            <th>🏆</th>
            <th>Temporadas</th>
            <th>Victorias</th>
            <th>Derrotas</th>
            <th>Win %</th>
            <th>Pts/Temp</th>
          </tr>
        </thead>
        <tbody>
    `;
    
    owners.forEach((owner, index) => {
      const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
      html += `
        <tr>
          <td><span class="rank-badge ${rankClass}">${index + 1}</span></td>
          <td><strong>${owner.owner}</strong></td>
          <td class="trophy-icon">${owner.championships > 0 ? '🏆'.repeat(owner.championships) : '-'}</td>
          <td>${owner.seasons_played}</td>
          <td style="color: #92cc41; font-weight: bold;">${owner.total_wins}</td>
          <td style="color: #e76e55;">${owner.total_losses}</td>
          <td><strong>${(owner.win_percentage * 100).toFixed(1)}%</strong></td>
          <td>${owner.avg_points_per_season.toFixed(1)}</td>
        </tr>
      `;
    });
    
    html += `
        </tbody>
      </table>
    `;
    
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar stats de dueños:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar estadísticas</div>';
  }
}

// Cargar top jugadores
async function loadTopPlayers() {
  const container = document.getElementById('players-stats');
  container.innerHTML = '<div class="loading">Cargando jugadores...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/top-scorers?limit=30`);
    const players = await response.json();
    
    if (!players || players.length === 0) {
      container.innerHTML = '<p class="nes-text">No hay datos de jugadores todavía.</p>';
      return;
    }
    
    let html = `
      <p style="font-size: 0.5rem; margin-bottom: 1rem;">🎮 Top 30 Mejores Temporadas Individuales</p>
      <table class="player-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Jugador</th>
            <th>Año</th>
            <th>Equipo Fantasy</th>
            <th>Pos</th>
            <th>Equipo NBA</th>
            <th>Pts/Juego</th>
            <th>Total Pts</th>
          </tr>
        </thead>
        <tbody>
    `;
    
    players.forEach((player, index) => {
      const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
      html += `
        <tr>
          <td><span class="rank-badge ${rankClass}">${index + 1}</span></td>
          <td><strong>${player.name}</strong></td>
          <td>${player.year}</td>
          <td style="font-size: 0.4rem;">${player.team}</td>
          <td>${player.position}</td>
          <td><strong>${player.proTeam}</strong></td>
          <td style="color: #92cc41; font-weight: bold;">${player.avg_points.toFixed(1)}</td>
          <td>${player.total_points.toFixed(0)}</td>
        </tr>
      `;
    });
    
    html += `
        </tbody>
      </table>
    `;
    
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar top players:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar jugadores</div>';
  }
}

// Cargar selector de temporadas
async function loadSeasonSelector() {
  const filterContainer = document.getElementById('year-filter');
  const summaryContainer = document.getElementById('season-summary');
  
  // Crear botones de años
  let filterHtml = '<span style="font-size: 0.5rem;">Selecciona año:</span>';
  availableYears.forEach(year => {
    const activeClass = year === selectedYear ? 'active' : '';
    filterHtml += `
      <button class="year-badge ${activeClass}" onclick="selectYear(${year})">
        ${year}
      </button>
    `;
  });
  
  filterContainer.innerHTML = filterHtml;
  
  // Cargar resumen del año seleccionado
  if (selectedYear) {
    await loadSeasonSummary(selectedYear);
  }
}

// Seleccionar año
async function selectYear(year) {
  selectedYear = year;
  
  // Actualizar badges
  document.querySelectorAll('.year-badge').forEach(badge => {
    badge.classList.remove('active');
    if (badge.textContent.trim() == year) {
      badge.classList.add('active');
    }
  });
  
  // Cargar resumen
  await loadSeasonSummary(year);
}

// Cargar resumen de temporada
async function loadSeasonSummary(year) {
  const container = document.getElementById('season-summary');
  container.innerHTML = '<div class="loading">Cargando temporada...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/season/${year}/summary`);
    const summary = await response.json();
    
    if (!summary || summary.error) {
      container.innerHTML = '<p class="nes-text is-error">No hay datos para esta temporada.</p>';
      return;
    }
    
    let html = `
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-card-header">
            <i class="nes-icon trophy"></i>
            Campeón ${summary.year}
          </div>
          <div class="stat-card-body">
            <div class="stat-value">${summary.champion.team}</div>
            <div class="stat-label">${summary.champion.owner}</div>
            <div style="margin-top: 0.5rem; font-size: 0.5rem;">
              Record: <strong>${summary.champion.record}</strong>
            </div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-card-header">
            <i class="nes-icon star"></i>
            Top Scorer
          </div>
          <div class="stat-card-body">
            <div class="stat-value">${summary.top_scorer ? summary.top_scorer.name : 'N/A'}</div>
            <div class="stat-label">${summary.top_scorer ? summary.top_scorer.team : ''}</div>
            <div style="margin-top: 0.5rem; font-size: 0.5rem;">
              Promedio: <strong>${summary.top_scorer ? summary.top_scorer.avg_points.toFixed(1) : 0} pts</strong>
            </div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-card-header">
            <i class="nes-icon is-medium heart"></i>
            Estadísticas de Liga
          </div>
          <div class="stat-card-body">
            <div style="margin-bottom: 0.5rem;">
              Equipos: <strong>${summary.total_teams}</strong>
            </div>
            <div style="margin-bottom: 0.5rem;">
              Promedio victorias: <strong>${summary.avg_wins.toFixed(1)}</strong>
            </div>
            <div>
              Total puntos: <strong>${summary.total_points_scored.toFixed(0)}</strong>
            </div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-card-header">
            <i class="nes-icon close"></i>
            Peor Equipo
          </div>
          <div class="stat-card-body">
            <div class="stat-value">${summary.worst_team.team}</div>
            <div class="stat-label">${summary.worst_team.owner}</div>
            <div style="margin-top: 0.5rem; font-size: 0.5rem;">
              Record: <strong>${summary.worst_team.record}</strong>
            </div>
          </div>
        </div>
      </div>
    `;
    
    // Cargar top scorers de la temporada
    const topScorersResponse = await fetch(`${API_BASE}/api/analytics/season/${year}/top-scorers?limit=10`);
    const topScorers = await topScorersResponse.json();
    
    if (topScorers && topScorers.length > 0) {
      html += `
        <div class="nes-container is-rounded" style="margin-top: 2rem;">
          <p style="font-size: 0.5rem; margin-bottom: 1rem;">🎯 Top 10 Jugadores ${year}</p>
          <table class="player-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Jugador</th>
                <th>Equipo</th>
                <th>Pos</th>
                <th>Pts/Juego</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
      `;
      
      topScorers.forEach((player, index) => {
        const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
        html += `
          <tr>
            <td><span class="rank-badge ${rankClass}">${index + 1}</span></td>
            <td><strong>${player.name}</strong></td>
            <td style="font-size: 0.4rem;">${player.team}</td>
            <td>${player.position}</td>
            <td style="color: #92cc41; font-weight: bold;">${player.avg_points.toFixed(1)}</td>
            <td>${player.total_points.toFixed(0)}</td>
          </tr>
        `;
      });
      
      html += `
            </tbody>
          </table>
        </div>
      `;
    }
    
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar resumen de temporada:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar resumen</div>';
  }
}

// Mostrar mensaje de error
function showError(message) {
  console.error(message);
}
