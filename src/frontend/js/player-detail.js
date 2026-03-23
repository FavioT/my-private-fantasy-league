async function loadPlayerDetails() {
    const loading = document.getElementById("loading");
    const content = document.getElementById("player-content");
    // Obtener player ID de URL
    const urlParams = new URLSearchParams(window.location.search);
    const playerId = urlParams.get("id");
    if (!playerId) {
        loading.innerHTML = '<span class="nes-text is-error">Error: No se especificó jugador</span>';
        return;
    }
    try {
        const res = await fetch(`/players/${playerId}`);
        if (!res.ok) {
            if (res.status === 404) {
                loading.innerHTML = `
          <div class="nes-container  is-dark">
            <p class="nes-text is-warning">Datos no disponibles para este jugador</p>
            <p style="font-size: 0.6rem; margin-top: 1rem;">
              Solo los siguientes jugadores tienen datos detallados:<br>
              LeBron James (1), Stephen Curry (2), Kevin Durant (3),<br>
              Joel Embiid (4), Luka Doncic (5), Kawhi Leonard (6)
            </p>
            <button type="button" class="nes-btn" onclick="window.location.href='/'" style="margin-top: 1rem;">
              Volver
            </button>
          </div>
        `;
                return;
            }
            throw new Error("Player not found");
        }
        const player = await res.json();
        // Ocultar loading, mostrar contenido
        loading.style.display = "none";
        content.style.display = "block";
        // Llenar información del header
        document.getElementById("player-name").textContent = player.name;
        document.getElementById("player-position").textContent = player.position;
        document.getElementById("player-team").textContent = player.proTeam;
        document.getElementById("fantasy-team-name").textContent = `Equipo Fantasy: ${player.teamName}`;
        // Estado de lesión
        const injuryDiv = document.getElementById("injury-status");
        if (player.injured && player.injuryStatus) {
            injuryDiv.innerHTML = `<span class="nes-badge is-error"><span class="is-error">${player.injuryStatus}</span></span>`;
        }
        else {
            injuryDiv.innerHTML = `<span class="nes-badge is-success"><span class="is-success">Saludable</span></span>`;
        }
        // Badge de partidos jugados
        const gamesPlayedBadge = document.getElementById("games-played-badge");
        const totalGamesInSeason = 82; // Temporada regular NBA
        const gamesPlayed = player.stats.gamesPlayed;
        const gamesPlayedPercentage = ((gamesPlayed / totalGamesInSeason) * 100).toFixed(1);
        // Determinar el color del badge según el porcentaje
        let percentageClass = "is-success"; // Verde por defecto
        if (parseFloat(gamesPlayedPercentage) < 50) {
            percentageClass = "is-error"; // Rojo si menos del 50%
        }
        else if (parseFloat(gamesPlayedPercentage) < 75) {
            percentageClass = "is-warning"; // Amarillo si entre 50-75%
        }
        gamesPlayedBadge.innerHTML = `
      <a href="#" class="nes-badge is-splited games-played-badge">
        <span class="is-primary">PJ</span>
        <span class="${percentageClass}">${gamesPlayedPercentage}%</span>
      </a>
    `;
        // Información de adquisición
        const acqDiv = document.getElementById("acquisition-info");
        if (player.acquisitionType === "DRAFT") {
            acqDiv.innerHTML = `
        <div class="acquisition-badge badge-draft">
          Drafteado: Ronda ${player.draftRound}, Pick ${player.draftPick}
        </div>
      `;
        }
        else {
            acqDiv.innerHTML = `
        <div class="acquisition-badge badge-fa">
          Agencia Libre
        </div>
      `;
        }
        // Estadísticas principales
        document.getElementById("stat-gp").textContent = player.stats.gamesPlayed.toString();
        document.getElementById("stat-mpg").textContent = player.stats.minutesPerGame.toFixed(1);
        document.getElementById("stat-ppg").textContent = player.stats.pointsPerGame.toFixed(1);
        document.getElementById("stat-rpg").textContent = player.stats.reboundsPerGame.toFixed(1);
        document.getElementById("stat-apg").textContent = player.stats.assistsPerGame.toFixed(1);
        document.getElementById("stat-spg").textContent = player.stats.stealsPerGame.toFixed(1);
        document.getElementById("stat-bpg").textContent = player.stats.blocksPerGame.toFixed(1);
        document.getElementById("stat-tpg").textContent = player.stats.turnoversPerGame.toFixed(1);
        // Eficiencia
        document.getElementById("stat-fgp").textContent = player.stats.fieldGoalPct.toFixed(1) + "%";
        document.getElementById("stat-ftp").textContent = player.stats.freeThrowPct.toFixed(1) + "%";
        document.getElementById("stat-3pm").textContent = player.stats.threePointMade.toFixed(1);
        document.getElementById("stat-3pp").textContent = player.stats.threePointPct.toFixed(1) + "%";
        document.getElementById("stat-dd").textContent = player.stats.doubleDoubles.toString();
        document.getElementById("stat-td").textContent = player.stats.tripleDoubles.toString();
        document.getElementById("stat-fppg").textContent = player.stats.avgFantasyPoints.toFixed(1);
        // Últimos 7 días
        document.getElementById("stat-l7-ppg").textContent = player.lastSevenDays.pointsPerGame.toFixed(1);
        document.getElementById("stat-l7-rpg").textContent = player.lastSevenDays.reboundsPerGame.toFixed(1);
        document.getElementById("stat-l7-apg").textContent = player.lastSevenDays.assistsPerGame.toFixed(1);
        document.getElementById("stat-l7-fgp").textContent = player.lastSevenDays.fieldGoalPct.toFixed(1) + "%";
        document.getElementById("stat-l7-fppg").textContent = player.lastSevenDays.avgFantasyPoints.toFixed(1);
        // Próximos partidos
        const gamesContainer = document.getElementById("upcoming-games");
        if (player.upcomingGames && player.upcomingGames.length > 0) {
            gamesContainer.innerHTML = player.upcomingGames.map(game => {
                const gameDate = new Date(game.date);
                const dateStr = gameDate.toLocaleDateString('es-ES', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric'
                });
                const location = game.isHome ? "vs" : "@";
                const locationClass = game.isHome ? "home-game" : "away-game";
                const statusStr = game.status ? ` (${game.status})` : "";
                return `
          <div class="game-item">
            <div class="game-date">${dateStr}</div>
            <div class="game-matchup">
              <span class="${locationClass}">${location}</span> ${game.opponent}${statusStr}
            </div>
          </div>
        `;
            }).join('');
        }
        else {
            gamesContainer.innerHTML = '<div style="text-align: center; color: #ccc;">Sin partidos programados</div>';
        }
        // Proyecciones
        document.getElementById("proj-pts").textContent = player.projections.seasonPoints.toString();
        document.getElementById("proj-reb").textContent = player.projections.seasonRebounds.toString();
        document.getElementById("proj-ast").textContent = player.projections.seasonAssists.toString();
        // Noticias
        document.getElementById("player-news").textContent = player.news;
    }
    catch (error) {
        loading.innerHTML = '<span class="nes-text is-error">Error al cargar jugador</span>';
        console.error("Error loading player:", error);
    }
}
loadPlayerDetails();
