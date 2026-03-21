"""
Script para inspeccionar la librería espn_api y sus atributos disponibles.
"""

def inspect_player_class():
    """Inspecciona la clase Player de basketball"""
    try:
        from espn_api.basketball import League, Player
        from espn_api.basketball.constant import STATS_MAP, NINE_CAT_STATS, POSITION_MAP, PRO_TEAM_MAP, STAT_ID_MAP
        
        print("=" * 80)
        print("MAPEO DE ESTADÍSTICAS (STATS_MAP)")
        print("=" * 80)
        for key, value in STATS_MAP.items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 80)
        print("ESTADÍSTICAS 9-CAT (NINE_CAT_STATS)")
        print("=" * 80)
        print(NINE_CAT_STATS)
        
        print("\n" + "=" * 80)
        print("MAPEO DE POSICIONES (POSITION_MAP)")
        print("=" * 80)
        # Solo mostrar las primeras 15 posiciones numéricas
        for i in range(16):
            if i in POSITION_MAP:
                print(f"{i}: {POSITION_MAP[i]}")
        
        print("\n" + "=" * 80)
        print("MAPEO DE ID DE STATS (STAT_ID_MAP)")
        print("=" * 80)
        for key, value in STAT_ID_MAP.items():
            print(f"{key}: {value}")
        
        print("\n" + "=" * 80)
        print("ATRIBUTOS DE LA CLASE Player")
        print("=" * 80)
        # Crear un diccionario con atributos de ejemplo
        sample_data = {
            'fullName': 'Sample Player',
            'id': 12345,
            'defaultPositionId': 1,
            'eligibleSlots': [0, 1, 5],
            'acquisitionType': 'FREEAGENT',
            'proTeamId': 1,
            'injuryStatus': 'ACTIVE',
            'positionalRanking': 10,
            'playerPoolEntry': {
                'player': {
                    'stats': []
                }
            }
        }
        
        player = Player(sample_data, 2024)
        
        print("\nAtributos disponibles en un objeto Player:")
        for attr in dir(player):
            if not attr.startswith('_'):
                try:
                    value = getattr(player, attr)
                    if not callable(value):
                        print(f"  • {attr}: {type(value).__name__}")
                except:
                    print(f"  • {attr}: (no accesible)")
        
        print("\n" + "=" * 80)
        print("EJEMPLO DE USO BÁSICO")
        print("=" * 80)
        print("""
from espn_api.basketball import League

# Para liga pública
league = League(league_id=YOUR_LEAGUE_ID, year=2024)

# Para liga privada
league = League(
    league_id=YOUR_LEAGUE_ID, 
    year=2024,
    espn_s2='YOUR_ESPN_S2',
    swid='{YOUR_SWID}'
)

# Obtener equipos y jugadores
for team in league.teams:
    print(f"Team: {team.team_name}")
    for player in team.roster:
        print(f"  - {player.name} ({player.position})")
        print(f"    Total Points: {player.total_points}")
        print(f"    Avg Points: {player.avg_points}")
        print(f"    Stats: {player.stats}")
        
        # Estadísticas 9-CAT
        if hasattr(player, 'nine_cat_averages'):
            print(f"    9-Cat Averages: {player.nine_cat_averages}")

# Obtener agentes libres
free_agents = league.free_agents(size=50)
for player in free_agents:
    print(f"{player.name}: {player.total_points} pts")
""")
        
    except ImportError as e:
        print(f"Error: No se puede importar espn_api. Asegúrate de instalarla con: pip install espn_api")
        print(f"Detalles del error: {e}")
        print("\n" + "=" * 80)
        print("INFORMACIÓN BASADA EN DOCUMENTACIÓN")
        print("=" * 80)
        print("""
Basándome en el código fuente, aquí están las estadísticas disponibles:

ESTADÍSTICAS PRINCIPALES (STATS_MAP):
- Puntos (PTS): Puntos totales
- Rebotes (REB): Rebotes totales
- Asistencias (AST): Asistencias
- Robos (STL): Robos
- Bloqueos (BLK): Bloqueos
- Pérdidas (TO): Turnover/Pérdidas de balón
- Tiros de campo (FGM): Field Goals Made
- Intentos de tiros de campo (FGA): Field Goal Attempts
- Porcentaje de tiros (FG%): Field Goal Percentage
- Tiros libres (FTM): Free Throws Made
- Intentos de tiros libres (FTA): Free Throw Attempts
- Porcentaje de tiros libres (FT%): Free Throw Percentage
- Triples (3PM): Three Pointers Made
- Intentos de triples (3PA): Three Point Attempts

CATEGORÍAS 9-CAT (formato estándar de fantasy basketball):
- PTS, REB, AST, STL, BLK, TO, FGM/FGA (FG%), FTM/FTA (FT%), 3PM

ATRIBUTOS DEL OBJETO Player:
• name: str - Nombre del jugador
• playerId: int - ID único del jugador
• position: str - Posición principal (PG, SG, SF, PF, C)
• eligibleSlots: List[str] - Posiciones elegibles
• posRank: int - Ranking posicional
• acquisitionType: str - Tipo de adquisición (FREEAGENT, DRAFT, etc.)
• proTeam: str - Equipo profesional
• injuryStatus: str - Estado de lesión
• injured: bool - Si está lesionado
• expected_return_date: date - Fecha esperada de regreso (si está lesionado)
• lineupSlot: str - Posición en el lineup (SG, C, PG, SF, IR, BE)
• total_points: int - Puntos totales en la temporada
• avg_points: float - Promedio de puntos
• projected_total_points: int - Proyección de puntos totales
• projected_avg_points: float - Proyección promedio de puntos
• stats: dict - Diccionario con todas las estadísticas por período
• schedule: dict - Calendario de juegos
• news: list - Noticias del jugador
• nine_cat_averages: dict - Promedios en las 9 categorías estándar

El diccionario 'stats' tiene esta estructura:
{
    '2': {  # período de puntuación
        'team': 'NYK',  # equipo rival
        'date': datetime,  # fecha del juego
        'applied_total': 45.0,  # puntos fantasy totales
        'applied_avg': 15.0,  # promedio de puntos fantasy
        'total': {  # estadísticas totales
            'PTS': 20.0,
            'REB': 8.0,
            'AST': 3.0,
            'STL': 2.0,
            'BLK': 1.0,
            'TO': 2.0,
            'FGM': 8.0,
            'FGA': 15.0,
            'FG%': 0.533,
            'FTM': 4.0,
            'FTA': 5.0,
            'FT%': 0.800,
            '3PM': 2.0
        },
        'avg': {  # promedios (si están disponibles)
            ...
        }
    },
    '2024_total': {  # totales de la temporada
        'applied_total': 1200,
        'applied_avg': 24.5,
        'total': {...},
        'avg': {...}
    },
    '2024_projected': {  # proyecciones
        'applied_total': 1500,
        'applied_avg': 25.0,
        'total': {...}
    }
}
""")

if __name__ == "__main__":
    inspect_player_class()
