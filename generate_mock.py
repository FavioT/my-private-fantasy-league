"""
Script para generar datos mock desde la API real de ESPN
Ejecutar: python generate_mock.py

Esto actualizará el archivo mock_data.py con datos reales actuales
"""

from espn_api.basketball import League
import json

def get_league():
    return League(
        league_id=76117164,
        year=2026,
        espn_s2='AEBmFeUmTSryp0cGx8qZ7bQ5kpucH7tgYxY9k7V776NBbap9vCQaxqUij%2BS2McI7VbhxKxpu%2F%2FNRioOjV%2FCsAG9VVZLS3plbxcWCoUG2ea9rRn%2Bewg7D1Arpte8kYsvYpTGBKyLwaETILDeBHtVr%2FgiTERCurvzPH9JGXBnYkn3bdvAPxptcEAr1Sb1UKikOEhDvUCnG6kKnpf1yepo%2FzSyE80%2BuApbvkNrjgIyjpfHv1AX2Ip%2Bj%2F1WN24m4RFlPx8cBThF3%2BCIhQgPc%2FbhhVEPT6NEgb5q67I6N2qPby48u5Q%3D%3D', 
        swid='{DA611254-3C72-4FA0-8A47-D236659F6792}'
    )

def generate_mock_data():
    print("🔄 Obteniendo datos de ESPN...")
    league = get_league()
    
    # Generar datos de equipos
    mock_teams = []
    mock_players = {}
    
    for team in league.teams:
        print(f"📊 Procesando: {team.team_name}")
        
        # Datos del equipo
        mock_teams.append({
            "id": team.team_id,
            "name": team.team_name,
            "wins": team.wins,
            "losses": team.losses
        })
        
        # Datos de jugadores
        players = []
        for player in team.roster:
            players.append({
                "name": player.name,
                "position": player.position,
                "team": player.proTeam,
                "injured": player.injured,
                "injuryStatus": player.injuryStatus if player.injured else None
            })
        
        mock_players[team.team_id] = {
            "teamName": team.team_name,
            "players": players
        }
    
    # Escribir archivo
    print("\n💾 Generando mock_data.py...")
    
    with open("mock_data.py", "w", encoding="utf-8") as f:
        f.write("# Mock data para desarrollo - Evita llamadas repetidas a la API de ESPN\n\n")
        f.write(f"MOCK_TEAMS = {json.dumps(mock_teams, indent=4, ensure_ascii=False)}\n\n")
        f.write(f"MOCK_PLAYERS = {json.dumps(mock_players, indent=4, ensure_ascii=False)}\n")
    
    print(f"✅ ¡Listo! Generados {len(mock_teams)} equipos con sus jugadores")
    print(f"\n📝 Para usar estos datos, asegúrate de que USE_MOCK = True en app.py")

if __name__ == "__main__":
    generate_mock_data()
