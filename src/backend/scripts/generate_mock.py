"""
Script para generar datos mock desde la API real de ESPN
Ejecutar: python generate_mock.py

Esto actualizará el archivo mock_data.py con datos reales actuales
"""

from espn_api.basketball import League
from dotenv import load_dotenv
import json
import os

# Cargar variables de entorno desde .env en la raíz del proyecto
_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
load_dotenv(os.path.join(_root, '.env'))

def get_league():
    return League(
        league_id=int(os.environ['LEAGUE_ID']),
        year=int(os.getenv('LEAGUE_YEAR', '2026')),
        espn_s2=os.environ['ESPN_S2'],
        swid=os.environ['SWID']
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
