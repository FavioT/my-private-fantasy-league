interface Team {
  id: number;
  name: string;
  wins: number;
  losses: number;
}

interface Player {
  playerId: number;
  name: string;
  position: string;
  team: string;
  injured: boolean;
  injuryStatus: string | null;
}

interface TeamPlayersResponse {
  teamName: string;
  players: Player[];
}

let selectedTeamId: number | null = null;

async function loadTeams() {
  const tbody = document.getElementById("teams")!;
  const loading = document.getElementById("teams-loading")!;
  const container = document.getElementById("teams-container")!;
  const status = document.getElementById("status")!;

  try {
    const res = await fetch("http://localhost:5000/teams");
    const data: Team[] = await res.json();

    // Ordenar equipos por victorias (descendente)
    data.sort((a, b) => b.wins - a.wins);

    // Ocultar loading, mostrar tabla
    loading.style.display = "none";
    container.style.display = "block";

    data.forEach((team, index) => {
      const tr = document.createElement("tr");
      tr.className = "clickable-row";
      tr.dataset.teamId = team.id.toString();
      
      const position = index + 1;
      const winPercentage = ((team.wins / (team.wins + team.losses)) * 100).toFixed(1);
      
      tr.innerHTML = `
        <td class="center-text">${position}</td>
        <td>${team.name}</td>
        <td class="center-text nes-text is-success">${team.wins}</td>
        <td class="center-text nes-text is-error">${team.losses}</td>
        <td class="center-text">${winPercentage}%</td>
      `;
      
      // Agregar evento de click
      tr.addEventListener("click", () => loadTeamPlayers(team.id, tr));
      
      tbody.appendChild(tr);
    });

    status.className = "nes-text is-success";
    status.textContent = "● ONLINE";
  } catch (error) {
    loading.innerHTML = '<span class="nes-text is-error">✖ Error al cargar equipos</span>';
    status.className = "nes-text is-error";
    status.textContent = "● ERROR";
    console.error("Error loading teams:", error);
  }
}

async function loadTeamPlayers(teamId: number, rowElement: HTMLElement) {
  const playersEmpty = document.getElementById("players-empty")!;
  const playersLoading = document.getElementById("players-loading")!;
  const playersContainer = document.getElementById("players-container")!;
  const playersBody = document.getElementById("players")!;
  const playersHeader = document.getElementById("players-header")!;
  const status = document.getElementById("status")!;

  // Remover selección anterior
  document.querySelectorAll(".selected-row").forEach(el => {
    el.classList.remove("selected-row");
  });

  // Marcar fila actual como seleccionada
  rowElement.classList.add("selected-row");
  selectedTeamId = teamId;

  // Mostrar loading
  playersEmpty.style.display = "none";
  playersContainer.style.display = "none";
  playersLoading.style.display = "block";

  try {
    const res = await fetch(`http://localhost:5000/teams/${teamId}/players`);
    const data: TeamPlayersResponse = await res.json();

    // Actualizar header con nombre del equipo
    playersHeader.textContent = data.teamName;

    // Limpiar tabla anterior
    playersBody.innerHTML = "";

    // Agregar jugadores
    data.players.forEach((player) => {
      const tr = document.createElement("tr");
      tr.style.cursor = "pointer";
      tr.className = "player-row-clickable";
      
      const statusText = player.injured 
        ? `<span class="player-injured">⚠ ${player.injuryStatus || "Lesionado"}</span>`
        : '<span class="nes-text is-success">✓</span>';
      
      const nameClass = player.injured ? "player-injured" : "";
      
      tr.innerHTML = `
        <td class="${nameClass}">${player.name}</td>
        <td class="center-text">${player.position}</td>
        <td class="center-text">${player.team}</td>
        <td class="center-text">${statusText}</td>
      `;
      
      // Hacer que la fila sea clickable
      tr.addEventListener("click", () => {
        const url = `/player-detail.html?id=${player.playerId}`;
        window.location.href = url;
      });
      
      // Efecto hover
      tr.addEventListener("mouseenter", () => {
        tr.style.backgroundColor = "rgba(146, 204, 65, 0.2)";
      });
      
      tr.addEventListener("mouseleave", () => {
        tr.style.backgroundColor = "";
      });
      
      playersBody.appendChild(tr);
    });

    // Mostrar tabla
    playersLoading.style.display = "none";
    playersContainer.style.display = "block";

  } catch (error) {
    playersLoading.innerHTML = '<span class="nes-text is-error">✖ Error al cargar jugadores</span>';
    status.className = "nes-text is-error";
    status.textContent = "● ERROR";
    console.error("Error loading players:", error);
  }
}

loadTeams();