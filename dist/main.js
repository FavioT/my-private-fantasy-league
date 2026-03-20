async function loadTeams() {
    const tbody = document.getElementById("teams");
    const loading = document.getElementById("teams-loading");
    const table = document.getElementById("teams-table");
    const status = document.getElementById("status");
    try {
        const res = await fetch("http://localhost:5000/teams");
        const data = await res.json();
        // Ordenar equipos por victorias (descendente)
        data.sort((a, b) => b.wins - a.wins);
        // Ocultar loading, mostrar tabla
        loading.style.display = "none";
        table.style.display = "table";
        data.forEach((team, index) => {
            const tr = document.createElement("tr");
            const position = index + 1;
            const winPercentage = ((team.wins / (team.wins + team.losses)) * 100).toFixed(1);
            tr.innerHTML = `
        <td class="tui-td center">${position}</td>
        <td class="tui-td">${team.name}</td>
        <td class="tui-td center tui-text-green">${team.wins}</td>
        <td class="tui-td center tui-text-red">${team.losses}</td>
        <td class="tui-td center">${team.wins}-${team.losses} (${winPercentage}%)</td>
      `;
            tbody.appendChild(tr);
        });
        status.className = "tui-text-green";
        status.textContent = "● ONLINE";
    }
    catch (error) {
        loading.textContent = "✖ Error al cargar equipos";
        loading.className = "center tui-text-red";
        status.className = "tui-text-red";
        status.textContent = "● ERROR";
        console.error("Error loading teams:", error);
    }
}
loadTeams();
