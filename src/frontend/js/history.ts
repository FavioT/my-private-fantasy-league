// Configuración de la API
const API_BASE: string = '';

// Tipos
interface Champion {
  year: number;
  team_name: string;
  owner: string;
  wins: number;
  losses: number;
  points_for: number;
}

interface OwnerStats {
  owner: string;
  championships: number;
  total_wins: number;
  total_losses: number;
  win_percentage: number;
  total_points: number;
  seasons_played: number;
  avg_points_per_season: number;
}

interface Player {
  name: string;
  year: number;
  team: string;
  owner: string;
  avg_points: number;
  total_points: number;
  position: string;
  proTeam: string;
}

interface SeasonSummary {
  year: number;
  league_name: string;
  total_teams: number;
  champion: {
    team: string;
    owner: string;
    record: string;
  };
  worst_team: {
    team: string;
    owner: string;
    record: string;
  };
  top_scorer: {
    name: string;
    team: string;
    avg_points: number;
  };
  avg_wins: number;
  total_points_scored: number;
}

// Estado global
let currentTab: string = 'champions';
let availableYears: number[] = [];
let selectedYear: number | null = null;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', async () => {
  try {
    await loadAvailableYears();
    await loadTabData(currentTab);
  } catch (error) {
    console.error('Error al inicializar:', error);
    showError('Error al cargar la aplicación');
  }
});

// Cargar años disponibles
async function loadAvailableYears(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/api/analytics/available-years`);
    const data = await response.json();
    availableYears = data.years || [];
    selectedYear = availableYears[availableYears.length - 2] || availableYears[0];
  } catch (error) {
    console.error('Error al cargar años:', error);
  }
}

// Cambiar de tab
function switchTab(tabName: string): void {
  currentTab = tabName;
  
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.remove('active');
  });
  (event?.target as HTMLElement)?.closest('.tab-button')?.classList.add('active');
  
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.remove('active');
  });
  document.getElementById(`tab-${tabName}`)?.classList.add('active');
  
  loadTabData(tabName);
}

// Cargar datos según el tab
async function loadTabData(tabName: string): Promise<void> {
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
async function loadChampions(): Promise<void> {
  const container = document.getElementById('champions-list');
  if (!container) return;
  
  container.innerHTML = '<div class="loading">Cargando campeones...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/champions`);
    const champions: Champion[] = await response.json();
    
    if (!champions || champions.length === 0) {
      container.innerHTML = '<p class="nes-text">No hay datos de campeones todavía.</p>';
      return;
    }
    
    let html = '<ul class="champions-list">';
    
    champions.forEach(champ => {
      html += `
        <li class="champion-item">
          <span class="champion-year"><i class="nes-icon trophy is-small"></i> ${champ.year}</span>
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
    
    const totalChampionships: Record<string, number> = {};
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
async function loadOwnerStats(): Promise<void> {
  const container = document.getElementById('owners-stats');
  if (!container) return;
  
  container.innerHTML = '<div class="loading">Cargando estadísticas...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/owner-stats`);
    const owners: OwnerStats[] = await response.json();
    
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
            <th><i class="nes-icon trophy is-small"></i></th>
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
          <td class="trophy-icon">${owner.championships > 0 ? '<i class="nes-icon trophy is-small"></i>'.repeat(owner.championships) : '-'}</td>
          <td>${owner.seasons_played}</td>
          <td style="color: #92cc41; font-weight: bold;">${owner.total_wins}</td>
          <td style="color: #e76e55;">${owner.total_losses}</td>
          <td><strong>${(owner.win_percentage * 100).toFixed(1)}%</strong></td>
          <td>${owner.avg_points_per_season.toFixed(1)}</td>
        </tr>
      `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar stats de dueños:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar estadísticas</div>';
  }
}

// Cargar top jugadores
async function loadTopPlayers(): Promise<void> {
  const container = document.getElementById('players-stats');
  if (!container) return;
  
  container.innerHTML = '<div class="loading">Cargando jugadores...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/top-scorers?limit=30`);
    const players: Player[] = await response.json();
    
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
    
    html += '</tbody></table>';
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar top players:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar jugadores</div>';
  }
}

// Cargar selector de temporadas
async function loadSeasonSelector(): Promise<void> {
  const filterContainer = document.getElementById('year-filter');
  
  let filterHtml = '<span style="font-size: 0.5rem;">Selecciona año:</span>';
  availableYears.forEach(year => {
    const activeClass = year === selectedYear ? 'active' : '';
    filterHtml += `
      <button class="year-badge ${activeClass}" onclick="selectYear(${year})">
        ${year}
      </button>
    `;
  });
  
  if (filterContainer) {
    filterContainer.innerHTML = filterHtml;
  }
  
  if (selectedYear) {
    await loadSeasonSummary(selectedYear);
  }
}

// Seleccionar año
async function selectYear(year: number): Promise<void> {
  selectedYear = year;
  
  document.querySelectorAll('.year-badge').forEach(badge => {
    badge.classList.remove('active');
    if (badge.textContent?.trim() == String(year)) {
      badge.classList.add('active');
    }
  });
  
  await loadSeasonSummary(year);
}

// Cargar resumen de temporada
async function loadSeasonSummary(year: number): Promise<void> {
  const container = document.getElementById('season-summary');
  if (!container) return;
  
  container.innerHTML = '<div class="loading">Cargando temporada...</div>';
  
  try {
    const response = await fetch(`${API_BASE}/api/analytics/season/${year}/summary`);
    const summary: SeasonSummary = await response.json();
    
    if (!summary || (summary as any).error) {
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
    
    const topScorersResponse = await fetch(`${API_BASE}/api/analytics/season/${year}/top-scorers?limit=10`);
    const topScorers: Player[] = await topScorersResponse.json();
    
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
      
      html += '</tbody></table></div>';
    }
    
    container.innerHTML = html;
  } catch (error) {
    console.error('Error al cargar resumen de temporada:', error);
    container.innerHTML = '<div class="error-message">❌ Error al cargar resumen</div>';
  }
}

// Mostrar mensaje de error
function showError(message: string): void {
  console.error(message);
}

// Hacer funciones globales
(window as any).switchTab = switchTab;
(window as any).selectYear = selectYear;
