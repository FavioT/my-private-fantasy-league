"""
Ejemplos prácticos de uso de espn_api para Basketball Fantasy

Instrucciones:
1. Instala la librería: pip install espn_api
2. Configura tu LEAGUE_ID y YEAR
3. Si tu liga es privada, agrega ESPN_S2 y SWID
4. Ejecuta los ejemplos que necesites
"""

from espn_api.basketball import League
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN - MODIFICA ESTOS VALORES
# ============================================================================

LEAGUE_ID = 123456  # Reemplaza con tu League ID
YEAR = 2024  # Año de la temporada

# Para ligas privadas, obtén estos valores de las cookies de ESPN
ESPN_S2 = None  # Tu cookie espn_s2
SWID = None  # Tu cookie swid (incluye las llaves {})

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_league():
    """Inicializa y retorna el objeto League"""
    if ESPN_S2 and SWID:
        return League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)
    else:
        return League(league_id=LEAGUE_ID, year=YEAR)


def print_separator(title=""):
    """Imprime un separador visual"""
    if title:
        print(f"\n{'='*80}")
        print(f" {title}")
        print('='*80)
    else:
        print('-'*80)


# ============================================================================
# EJEMPLO 1: Información General de la Liga
# ============================================================================

def example_league_info():
    """Muestra información general de la liga"""
    print_separator("EJEMPLO 1: Información General de la Liga")
    
    league = get_league()
    
    print(f"Nombre de la liga: {league.settings.name}")
    print(f"Número de equipos: {league.settings.team_count}")
    print(f"Tipo de puntuación: {league.settings.scoring_type}")
    print(f"Semana actual: {league.current_week}")
    
    print(f"\nEquipos en la liga:")
    for i, team in enumerate(league.teams, 1):
        print(f"{i:2d}. {team.team_name:30s} ({team.wins}-{team.losses}) - {team.points_for:.1f} pts")


# ============================================================================
# EJEMPLO 2: Análisis de un Equipo Específico
# ============================================================================

def example_team_analysis(team_index=0):
    """Analiza un equipo específico y sus jugadores"""
    print_separator(f"EJEMPLO 2: Análisis de Equipo")
    
    league = get_league()
    team = league.teams[team_index]
    
    print(f"Equipo: {team.team_name}")
    print(f"Dueño: {team.owner}")
    print(f"Récord: {team.wins}-{team.losses}")
    print(f"Puntos a favor: {team.points_for:.1f}")
    print(f"Puntos en contra: {team.points_against:.1f}")
    
    print(f"\nRoster completo:")
    print(f"{'Jugador':<25} {'Pos':<5} {'Equipo':<5} {'Avg Pts':<10} {'Estado':<15}")
    print_separator()
    
    for player in team.roster:
        status = "LESIONADO" if player.injured else player.injuryStatus
        print(f"{player.name:<25} {player.position:<5} {player.proTeam:<5} "
              f"{player.avg_points:<10.1f} {status:<15}")


# ============================================================================
# EJEMPLO 3: Top Jugadores por Estadística
# ============================================================================

def example_top_players(stat='PTS', n=10):
    """Encuentra los mejores jugadores en una estadística"""
    print_separator(f"EJEMPLO 3: Top {n} Jugadores en {stat}")
    
    league = get_league()
    
    # Recopilar todos los jugadores
    all_players = []
    for team in league.teams:
        all_players.extend(team.roster)
    
    # Filtrar y ordenar
    players_with_stats = [
        p for p in all_players 
        if p.nine_cat_averages and stat in p.nine_cat_averages
    ]
    
    sorted_players = sorted(
        players_with_stats,
        key=lambda p: p.nine_cat_averages[stat],
        reverse=(stat != 'TO')  # Para turnovers, menos es mejor
    )
    
    # Mostrar resultados
    print(f"{'Rank':<6} {'Jugador':<25} {'Equipo':<5} {stat:<10} {'Fantasy Pts':<12}")
    print_separator()
    
    for i, player in enumerate(sorted_players[:n], 1):
        value = player.nine_cat_averages[stat]
        print(f"{i:<6} {player.name:<25} {player.proTeam:<5} "
              f"{value:<10.1f} {player.avg_points:<12.1f}")


# ============================================================================
# EJEMPLO 4: Mejores Agentes Libres
# ============================================================================

def example_free_agents(n=20):
    """Muestra los mejores agentes libres disponibles"""
    print_separator(f"EJEMPLO 4: Top {n} Agentes Libres")
    
    league = get_league()
    
    # Obtener agentes libres
    free_agents = league.free_agents(size=n)
    
    print(f"{'Rank':<6} {'Jugador':<25} {'Pos':<5} {'Equipo':<5} {'Avg Pts':<10} {'Total Pts':<10}")
    print_separator()
    
    for i, player in enumerate(free_agents, 1):
        print(f"{i:<6} {player.name:<25} {player.position:<5} {player.proTeam:<5} "
              f"{player.avg_points:<10.1f} {player.total_points:<10.1f}")


# ============================================================================
# EJEMPLO 5: Análisis Detallado de un Jugador
# ============================================================================

def example_player_details(team_index=0, player_index=0):
    """Análisis completo de un jugador específico"""
    print_separator("EJEMPLO 5: Análisis Detallado de Jugador")
    
    league = get_league()
    player = league.teams[team_index].roster[player_index]
    
    print(f"Jugador: {player.name}")
    print(f"Equipo NBA: {player.proTeam}")
    print(f"Posición: {player.position}")
    print(f"Posiciones elegibles: {', '.join(player.eligibleSlots)}")
    print(f"Estado: {player.injuryStatus}")
    if player.injured and player.expected_return_date:
        print(f"Regreso esperado: {player.expected_return_date}")
    
    print(f"\nPuntos Fantasy:")
    print(f"  Total de temporada: {player.total_points:.1f}")
    print(f"  Promedio: {player.avg_points:.1f}")
    print(f"  Proyección total: {player.projected_total_points:.1f}")
    print(f"  Proyección promedio: {player.projected_avg_points:.1f}")
    
    # Estadísticas 9-CAT
    if player.nine_cat_averages:
        print(f"\nEstadísticas 9-CAT (Promedios):")
        for stat, value in sorted(player.nine_cat_averages.items()):
            if stat in ['FG%', 'FT%']:
                print(f"  {stat}: {value:.3f}")
            else:
                print(f"  {stat}: {value:.1f}")
    
    # Últimos 7 días
    last_7 = player.stats.get(f'{league.year}_last_7', {})
    if last_7:
        print(f"\nÚltimos 7 días:")
        print(f"  Promedio fantasy: {last_7.get('applied_avg', 0):.1f}")
    
    # Últimos 30 días
    last_30 = player.stats.get(f'{league.year}_last_30', {})
    if last_30:
        print(f"\nÚltimos 30 días:")
        print(f"  Promedio fantasy: {last_30.get('applied_avg', 0):.1f}")
    
    # Próximos juegos
    if player.schedule:
        print(f"\nPróximos juegos:")
        sorted_schedule = sorted(
            player.schedule.items(),
            key=lambda x: x[1]['date'] if isinstance(x[1].get('date'), datetime) else datetime.max
        )[:5]
        
        for period, game in sorted_schedule:
            date = game.get('date', 'TBD')
            team = game.get('team', 'TBD')
            if isinstance(date, datetime):
                date_str = date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = str(date)
            print(f"  Período {period}: vs {team} - {date_str}")


# ============================================================================
# EJEMPLO 6: Comparación de Jugadores
# ============================================================================

def example_compare_players(team1_idx=0, player1_idx=0, team2_idx=0, player2_idx=1):
    """Compara dos jugadores"""
    print_separator("EJEMPLO 6: Comparación de Jugadores")
    
    league = get_league()
    player1 = league.teams[team1_idx].roster[player1_idx]
    player2 = league.teams[team2_idx].roster[player2_idx]
    
    print(f"\n{player1.name:^30} vs {player2.name:^30}")
    print(f"{player1.proTeam:^30}    {player2.proTeam:^30}")
    print_separator()
    
    # Comparar puntos fantasy
    print(f"{'Promedio Fantasy:':<20} {player1.avg_points:>10.1f}    {player2.avg_points:>10.1f}")
    print(f"{'Total Fantasy:':<20} {player1.total_points:>10.1f}    {player2.total_points:>10.1f}")
    
    # Comparar 9-CAT
    if player1.nine_cat_averages and player2.nine_cat_averages:
        print(f"\nEstadísticas 9-CAT:")
        print(f"{'Stat':<10} {player1.name[:15]:>15}    {player2.name[:15]:>15}  {'Ganador':^15}")
        print_separator()
        
        stats = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', 'FG%', 'FT%', '3PM']
        
        for stat in stats:
            v1 = player1.nine_cat_averages.get(stat, 0)
            v2 = player2.nine_cat_averages.get(stat, 0)
            
            # Para TO, menos es mejor
            if stat == 'TO':
                winner = player1.name[:15] if v1 < v2 else (player2.name[:15] if v2 < v1 else "Empate")
            else:
                winner = player1.name[:15] if v1 > v2 else (player2.name[:15] if v2 > v1 else "Empate")
            
            if stat in ['FG%', 'FT%']:
                print(f"{stat:<10} {v1:>15.3f}    {v2:>15.3f}  {winner:^15}")
            else:
                print(f"{stat:<10} {v1:>15.1f}    {v2:>15.1f}  {winner:^15}")


# ============================================================================
# EJEMPLO 7: Jugadores con Mejor Tendencia
# ============================================================================

def example_hot_players():
    """Encuentra jugadores que están rindiendo mejor recientemente"""
    print_separator("EJEMPLO 7: Jugadores 'Calientes' (Mejor Tendencia Reciente)")
    
    league = get_league()
    
    # Recopilar jugadores
    all_players = []
    for team in league.teams:
        all_players.extend(team.roster)
    
    # Calcular tendencia
    trending_players = []
    for player in all_players:
        last_7 = player.stats.get(f'{league.year}_last_7', {}).get('applied_avg', 0)
        season_avg = player.avg_points
        
        if season_avg > 0 and last_7 > 0:
            improvement = ((last_7 - season_avg) / season_avg) * 100
            trending_players.append((player, improvement, last_7, season_avg))
    
    # Ordenar por mejora
    trending_players.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Jugador':<25} {'Equipo':<5} {'Últimos 7':<12} {'Promedio':<12} {'Mejora':<10}")
    print_separator()
    
    for player, improvement, last_7, season_avg in trending_players[:15]:
        print(f"{player.name:<25} {player.proTeam:<5} {last_7:<12.1f} "
              f"{season_avg:<12.1f} {improvement:>+9.1f}%")


# ============================================================================
# EJEMPLO 8: Análisis de Matchup de la Semana
# ============================================================================

def example_weekly_matchup(week=None):
    """Muestra los matchups de una semana específica"""
    print_separator("EJEMPLO 8: Matchups de la Semana")
    
    league = get_league()
    
    if week is None:
        week = league.current_week
    
    print(f"Semana {week}")
    print_separator()
    
    try:
        boxscores = league.box_scores(week)
        
        for matchup in boxscores:
            print(f"\n{matchup.home_team.team_name} vs {matchup.away_team.team_name}")
            print(f"Score: {matchup.home_score:.1f} - {matchup.away_score:.1f}")
            
            if matchup.home_score > matchup.away_score:
                print(f"Ganador: {matchup.home_team.team_name}")
            elif matchup.away_score > matchup.home_score:
                print(f"Ganador: {matchup.away_team.team_name}")
            else:
                print("Empate")
    except Exception as e:
        print(f"Error al obtener boxscores: {e}")


# ============================================================================
# EJEMPLO 9: Buscar Jugador por Nombre
# ============================================================================

def example_search_player(name="LeBron"):
    """Busca un jugador por nombre"""
    print_separator(f"EJEMPLO 9: Buscar Jugador '{name}'")
    
    league = get_league()
    
    try:
        results = league.player_info(name=name)
        
        if not results:
            print(f"No se encontraron jugadores con el nombre '{name}'")
            return
        
        print(f"{'Jugador':<30} {'Pos':<5} {'Equipo':<5} {'Avg Pts':<10} {'Total Pts':<10}")
        print_separator()
        
        for player in results[:10]:  # Mostrar primeros 10 resultados
            print(f"{player.name:<30} {player.position:<5} {player.proTeam:<5} "
                  f"{player.avg_points:<10.1f} {player.total_points:<10.1f}")
    except Exception as e:
        print(f"Error en la búsqueda: {e}")


# ============================================================================
# EJEMPLO 10: Estadísticas del Equipo Completo
# ============================================================================

def example_team_stats(team_index=0):
    """Calcula estadísticas agregadas del equipo"""
    print_separator("EJEMPLO 10: Estadísticas Agregadas del Equipo")
    
    league = get_league()
    team = league.teams[team_index]
    
    print(f"Equipo: {team.team_name}")
    print_separator()
    
    # Inicializar contadores
    stats_totals = {
        'PTS': 0, 'REB': 0, 'AST': 0, 'STL': 0, 
        'BLK': 0, 'TO': 0, '3PM': 0
    }
    fg_totals = {'made': 0, 'attempts': 0}
    ft_totals = {'made': 0, 'attempts': 0}
    player_count = 0
    
    # Sumar estadísticas de todos los jugadores activos
    for player in team.roster:
        if player.lineupSlot not in ['BE', 'IR'] and player.nine_cat_averages:
            player_count += 1
            for stat in stats_totals:
                stats_totals[stat] += player.nine_cat_averages.get(stat, 0)
    
    # Mostrar promedios del equipo
    if player_count > 0:
        print(f"Promedios del equipo (jugadores activos: {player_count}):\n")
        for stat, total in stats_totals.items():
            avg = total / player_count if player_count > 0 else 0
            print(f"  {stat}: {avg:.1f}")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def main():
    """Función principal con menú de ejemplos"""
    
    print("="*80)
    print("  ESPN API Basketball Fantasy - Ejemplos Prácticos")
    print("="*80)
    print("\nAsegúrate de configurar LEAGUE_ID y YEAR al inicio del archivo.")
    print("Para ligas privadas, también configura ESPN_S2 y SWID.\n")
    
    examples = {
        '1': ('Información General de la Liga', example_league_info),
        '2': ('Análisis de un Equipo', lambda: example_team_analysis(0)),
        '3': ('Top 10 en Puntos', lambda: example_top_players('PTS', 10)),
        '4': ('Mejores Agentes Libres', lambda: example_free_agents(20)),
        '5': ('Análisis Detallado de Jugador', lambda: example_player_details(0, 0)),
        '6': ('Comparar Dos Jugadores', lambda: example_compare_players(0, 0, 0, 1)),
        '7': ('Jugadores con Mejor Tendencia', example_hot_players),
        '8': ('Matchups de la Semana', lambda: example_weekly_matchup()),
        '9': ('Buscar Jugador', lambda: example_search_player("LeBron")),
        '10': ('Estadísticas del Equipo', lambda: example_team_stats(0)),
        'all': ('Ejecutar Todos los Ejemplos', None),
    }
    
    print("Ejemplos disponibles:")
    for key, (desc, _) in examples.items():
        if key != 'all':
            print(f"  {key:>3}. {desc}")
    print(f"  {'all':>3}. Ejecutar todos los ejemplos")
    print(f"  {'q':>3}. Salir")
    
    while True:
        choice = input("\nSelecciona un ejemplo (o 'q' para salir): ").strip().lower()
        
        if choice == 'q':
            print("¡Hasta luego!")
            break
        
        if choice == 'all':
            for key, (desc, func) in examples.items():
                if key != 'all' and func:
                    try:
                        func()
                    except Exception as e:
                        print(f"\nError en {desc}: {e}")
                    input("\nPresiona Enter para continuar...")
        elif choice in examples and choice != 'all':
            try:
                examples[choice][1]()
            except Exception as e:
                print(f"\nError: {e}")
                print("\nVerifica:")
                print("- Que LEAGUE_ID y YEAR estén configurados correctamente")
                print("- Que tengas conexión a internet")
                print("- Si es una liga privada, que ESPN_S2 y SWID estén configurados")
        else:
            print("Opción no válida. Intenta de nuevo.")
        
        if choice != 'q':
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    # Puedes descomentar y ejecutar ejemplos específicos directamente:
    
    # example_league_info()
    # example_team_analysis(0)
    # example_top_players('PTS', 10)
    # example_free_agents(20)
    # example_player_details(0, 0)
    # example_compare_players(0, 0, 0, 1)
    # example_hot_players()
    # example_weekly_matchup()
    # example_search_player("LeBron")
    # example_team_stats(0)
    
    # O ejecuta el menú interactivo:
    main()
