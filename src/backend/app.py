from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from espn_api.basketball import League
from mocks.mock_data import MOCK_TEAMS, MOCK_PLAYERS
from mocks.mock_player_details import MOCK_PLAYER_DETAILS
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from data_manager import LeagueDataManager
from analytics import HistoricalAnalytics

# Cargar variables de entorno desde .env (en la raíz del proyecto)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)

# Configuración desde variables de entorno
USE_MOCK = os.getenv('USE_MOCK', 'False').lower() == 'true'
LEAGUE_ID = int(os.getenv('LEAGUE_ID', '0'))
LEAGUE_YEAR = int(os.getenv('LEAGUE_YEAR', '2026'))
ESPN_S2 = os.getenv('ESPN_S2', '')
SWID = os.getenv('SWID', '')

# Inicializar Data Manager y Analytics
league_config = {
    'league_id': LEAGUE_ID,
    'espn_s2': ESPN_S2,
    'swid': SWID
}
data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
data_manager = LeagueDataManager(data_dir=data_dir, league_config=league_config)
analytics = HistoricalAnalytics(data_manager)

def get_league():
    if not LEAGUE_ID or not ESPN_S2 or not SWID:
        raise ValueError("Configuración incompleta. Revisa tu archivo .env")
    
    return League(
        league_id=LEAGUE_ID,
        year=LEAGUE_YEAR,
        espn_s2=ESPN_S2, 
        swid=SWID
    )

# Directorio del frontend con ruta absoluta (necesario para Vercel)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

# Rutas para servir archivos estáticos
@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/player-detail.html')
def player_detail_page():
    return send_from_directory(FRONTEND_DIR, 'player-detail.html')

@app.route('/teams.html')
def teams_page():
    return send_from_directory(FRONTEND_DIR, 'teams.html')

@app.route('/owner-detail.html')
def owner_detail_page():
    return send_from_directory(FRONTEND_DIR, 'owner-detail.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/teams")
def get_teams():
    if USE_MOCK:
        return jsonify(MOCK_TEAMS)
    
    league = get_league()

    teams = []
    for team in league.teams:
        teams.append({
            "id": team.team_id,
            "name": team.team_name,
            "wins": team.wins,
            "losses": team.losses
        })

    return jsonify(teams)

@app.route("/teams/<int:team_id>/players")
def get_team_players(team_id):
    if USE_MOCK:
        if team_id in MOCK_PLAYERS:
            return jsonify(MOCK_PLAYERS[team_id])
        else:
            return jsonify({"error": "Team not found"}), 404
    
    league = get_league()
    
    team = None
    for t in league.teams:
        if t.team_id == team_id:
            team = t
            break
    
    if not team:
        return jsonify({"error": "Team not found"}), 404
    
    players = []
    for player in team.roster:
        # Usar el playerId de ESPN API
        players.append({
            "playerId": player.playerId,
            "name": player.name,
            "position": player.position,
            "team": player.proTeam,
            "injured": player.injured,
            "injuryStatus": player.injuryStatus if player.injured else None
        })
    
    return jsonify({
        "teamName": team.team_name,
        "players": players
    })

@app.route("/players/<int:player_id>")
def get_player_details(player_id):
    if USE_MOCK:
        if player_id in MOCK_PLAYER_DETAILS:
            return jsonify(MOCK_PLAYER_DETAILS[player_id])
        else:
            return jsonify({"error": "Player not found"}), 404
    
    # Buscar el jugador en todos los equipos
    league = get_league()
    player = None
    team_name = None
    
    for team in league.teams:
        for p in team.roster:
            if p.playerId == player_id:
                player = p
                team_name = team.team_name
                break
        if player:
            break
    
    if not player:
        return jsonify({"error": "Player not found"}), 404
    
    # Obtener estadísticas del jugador desde el objeto stats
    year_key = f"{2026}_total"
    last7_key = f"{2026}_last_7"
    proj_key = f"{2026}_projected"
    
    total_stats = player.stats.get(year_key, {}) if hasattr(player, 'stats') else {}
    last7_stats = player.stats.get(last7_key, {}) if hasattr(player, 'stats') else {}
    proj_stats = player.stats.get(proj_key, {}) if hasattr(player, 'stats') else {}
    
    # Obtener promedios y totales
    avg = total_stats.get('avg', {})
    total = total_stats.get('total', {})
    last7_avg = last7_stats.get('avg', {})
    proj_avg = proj_stats.get('avg', {})
    proj_total = proj_stats.get('total', {})
    
    # Generar próximos partidos desde el schedule
    today = datetime.now()
    upcoming_games = []
    
    if hasattr(player, 'schedule'):
        # Filtrar solo próximos partidos (7 días desde hoy)
        sorted_games = sorted(
            [(k, v) for k, v in player.schedule.items() if v.get('date') and v['date'] > today],
            key=lambda x: x[1]['date']
        )
        
        for _, game_info in sorted_games[:5]:  # Tomar los primeros 5 partidos
            upcoming_games.append({
                "date": game_info['date'].strftime("%Y-%m-%d"),
                "opponent": game_info.get('team', 'TBD'),
                "isHome": True  # ESPN API no especifica claramente home/away
            })
    
    # Construir respuesta con datos reales
    response = {
        "playerId": player.playerId,
        "name": player.name,
        "position": player.position,
        "proTeam": player.proTeam,
        "teamName": team_name,
        "injured": player.injured,
        "injuryStatus": player.injuryStatus if player.injured else None,
        "acquisitionType": player.acquisitionType if hasattr(player, 'acquisitionType') else "FREE_AGENT",
        "draftRound": None,
        "draftPick": None,
        "stats": {
            "gamesPlayed": int(avg.get('GP', 0)),
            "minutesPerGame": round(avg.get('MPG', 0), 1),
            "pointsPerGame": round(avg.get('PPG', 0), 1),
            "reboundsPerGame": round(avg.get('RPG', 0), 1),
            "assistsPerGame": round(avg.get('APG', 0), 1),
            "stealsPerGame": round(avg.get('SPG', 0), 1),
            "blocksPerGame": round(avg.get('BPG', 0), 1),
            "turnoversPerGame": round(avg.get('TOPG', 0), 1),
            "fieldGoalPct": round(avg.get('FG%', 0) * 100, 1),
            "freeThrowPct": round(avg.get('FT%', 0) * 100, 1),
            "threePointMade": round(avg.get('3PG', 0), 1),
            "threePointPct": round(avg.get('3PT%', 0) * 100, 1),
            "totalPoints": int(total.get('PTS', 0)),
            "totalRebounds": int(total.get('REB', 0)),
            "totalAssists": int(total.get('AST', 0)),
            "totalSteals": int(total.get('STL', 0)),
            "totalBlocks": int(total.get('BLK', 0)),
            "doubleDoubles": int(total.get('DD', 0)),
            "tripleDoubles": int(total.get('TD', 0)),
            "avgFantasyPoints": round(player.avg_points, 1)
        },
        "lastSevenDays": {
            "pointsPerGame": round(last7_avg.get('PPG', 0), 1),
            "reboundsPerGame": round(last7_avg.get('RPG', 0), 1),
            "assistsPerGame": round(last7_avg.get('APG', 0), 1),
            "fieldGoalPct": round(last7_avg.get('FG%', 0) * 100, 1),
            "avgFantasyPoints": round(last7_stats.get('applied_avg', 0), 1)
        },
        "projections": {
            "seasonPoints": int(proj_total.get('PTS', 0)),
            "seasonRebounds": int(proj_total.get('REB', 0)),
            "seasonAssists": int(proj_total.get('AST', 0))
        },
        "upcomingGames": upcoming_games if upcoming_games else [
            {"date": (today + timedelta(days=2)).strftime("%Y-%m-%d"), "opponent": "TBD", "isHome": True},
            {"date": (today + timedelta(days=4)).strftime("%Y-%m-%d"), "opponent": "TBD", "isHome": False}
        ],
        "news": getattr(player.news, 'headline', 'Datos en tiempo real de ESPN API') if hasattr(player, 'news') and player.news else "Datos en tiempo real de ESPN API"
    }
    
    return jsonify(response)


# ============================================================================
# ENDPOINTS DE ANALYTICS - Consultas Multi-Año
# ============================================================================

@app.route("/api/analytics/available-years")
def get_available_years():
    """Lista de años con datos disponibles"""
    try:
        years = data_manager.get_available_years()
        return jsonify({
            "years": years,
            "total": len(years)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/champions")
def get_champions():
    """Historial de campeones por año"""
    try:
        champions = analytics.get_championship_history()
        return jsonify(champions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/owner-stats")
def get_owner_stats():
    """Estadísticas agregadas de todos los dueños"""
    try:
        stats = analytics.get_owner_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/owner/<owner_name>")
def get_owner_history(owner_name):
    """Historial completo de un dueño específico"""
    try:
        history = analytics.get_team_performance_history(owner_name)
        if history is None:
            return jsonify({"error": "Owner not found"}), 404
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/player/<player_name>")
def get_player_career(player_name):
    """Estadísticas de carrera de un jugador"""
    try:
        career = analytics.get_player_career_stats(player_name)
        if career is None:
            return jsonify({"error": "Player not found in historical data"}), 404
        return jsonify(career)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/top-scorers")
def get_all_time_top_scorers():
    """Top anotadores de todos los tiempos"""
    try:
        limit = request.args.get('limit', default=20, type=int)
        top_scorers = analytics.get_all_time_top_scorers(limit=limit)
        return jsonify(top_scorers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/season/<int:year>/top-scorers")
def get_season_top_scorers(year):
    """Top anotadores de una temporada específica"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        top_scorers = analytics.get_top_scorers_by_season(year, limit=limit)
        if not top_scorers:
            return jsonify({"error": "Season not found"}), 404
        return jsonify(top_scorers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/season/<int:year>/summary")
def get_season_summary_endpoint(year):
    """Resumen completo de una temporada"""
    try:
        summary = analytics.get_season_summary(year)
        if summary is None:
            return jsonify({"error": "Season not found"}), 404
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/season/<int:year>")
def get_season_data(year):
    """Datos completos de una temporada"""
    try:
        data = data_manager.get_season_data(year)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": f"Season {year} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analytics/all-teams")
def get_all_teams():
    """Retorna todos los equipos únicos que existieron en la liga"""
    try:
        all_data = data_manager.load_all_historical_data()
        teams_seen = {}
        for _year, season_data in sorted(all_data.items()):
            for team in season_data.get('teams', []):
                name = team.get('team_name', '').strip()
                owner = team.get('owner', '').strip()
                if name and name not in teams_seen:
                    teams_seen[name] = owner
        result = [{'team_name': k, 'owner': v} for k, v in sorted(teams_seen.items())]
        return jsonify(result)
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
def get_owner_top_players(owner_name):
    """Top jugadores históricos de un owner específico"""
    try:
        limit = request.args.get('limit', default=15, type=int)
        players = analytics.get_owner_top_players(owner_name, limit=limit)
        return jsonify(players)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)