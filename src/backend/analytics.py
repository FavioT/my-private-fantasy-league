"""
Módulo de analytics para consultas multi-año sobre datos históricos.
Permite análisis y estadísticas combinando múltiples temporadas.
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from data_manager import LeagueDataManager


class HistoricalAnalytics:
    """Análisis de datos históricos multi-año"""
    
    def __init__(self, data_manager: LeagueDataManager):
        """
        Args:
            data_manager: Instancia de LeagueDataManager
        """
        self.data_manager = data_manager
        self._historical_data = None
    
    @property
    def historical_data(self) -> Dict[int, Dict]:
        """Lazy loading de datos históricos"""
        if self._historical_data is None:
            self._historical_data = self.data_manager.load_all_historical_data()
        return self._historical_data
    
    def get_championship_history(self) -> List[Dict]:
        """
        Obtiene el historial de campeones.
        Usa el campo 'playoff_champion' si existe, sino calcula por victorias.
        
        Returns:
            Lista de campeones ordenada por año
        """
        champions = []
        
        for year in sorted(self.historical_data.keys()):
            data = self.historical_data[year]
            teams = data.get('teams', [])
            
            if not teams:
                continue
            
            # Buscar el campeón: primero intentar con playoff_champion
            champion_team_name = data.get('playoff_champion')
            
            if champion_team_name:
                # Buscar el equipo por nombre
                champion = None
                for team in teams:
                    if team['team_name'] == champion_team_name:
                        champion = team
                        break
                
                # Si no se encuentra el equipo por nombre exacto, buscar por nombre aproximado
                if not champion:
                    for team in teams:
                        if champion_team_name.lower() in team['team_name'].lower() or \
                           team['team_name'].lower() in champion_team_name.lower():
                            champion = team
                            break
                
                # Fallback: usar el equipo con más victorias
                if not champion:
                    champion = max(teams, key=lambda t: t.get('wins', 0))
            else:
                # Si no hay playoff_champion, usar el equipo con más victorias
                champion = max(teams, key=lambda t: t.get('wins', 0))
            
            champions.append({
                'year': year,
                'team_name': champion['team_name'],
                'owner': champion.get('owner', 'Unknown'),
                'wins': champion['wins'],
                'losses': champion['losses'],
                'points_for': champion.get('points_for', 0)
            })
        
        return champions
    
    def get_owner_statistics(self) -> List[Dict]:
        """
        Estadísticas agregadas por dueño a través de los años.
        
        Returns:
            Lista de owners con sus stats totales
        """
        owner_stats = defaultdict(lambda: {
            'total_wins': 0,
            'total_losses': 0,
            'total_points': 0,
            'championships': 0,
            'seasons_played': set(),
            'teams': []
        })
        
        for year, data in self.historical_data.items():
            teams = data.get('teams', [])
            
            # Encontrar campeón del año usando playoff_champion si existe
            champion_team_name = data.get('playoff_champion')
            champion_owner = ''
            
            if champion_team_name and teams:
                # Buscar el equipo campeón por nombre
                champion = None
                for team in teams:
                    if team['team_name'] == champion_team_name or \
                       champion_team_name.lower() in team['team_name'].lower() or \
                       team['team_name'].lower() in champion_team_name.lower():
                        champion = team
                        break
                
                if champion:
                    champion_owner = champion.get('owner', '')
            
            # Fallback: usar el equipo con más victorias si no se encontró playoff_champion
            if not champion_owner and teams:
                champion = max(teams, key=lambda t: t.get('wins', 0))
                champion_owner = champion.get('owner', '')
            
            for team in teams:
                owner = team.get('owner', 'Unknown')
                
                owner_stats[owner]['total_wins'] += team.get('wins', 0)
                owner_stats[owner]['total_losses'] += team.get('losses', 0)
                owner_stats[owner]['total_points'] += team.get('points_for', 0)
                owner_stats[owner]['seasons_played'].add(year)
                
                if owner == champion_owner:
                    owner_stats[owner]['championships'] += 1
                
                owner_stats[owner]['teams'].append({
                    'year': year,
                    'team_name': team['team_name'],
                    'record': f"{team['wins']}-{team['losses']}"
                })
        
        # Convertir a lista y calcular win percentage
        result = []
        for owner, stats in owner_stats.items():
            total_games = stats['total_wins'] + stats['total_losses']
            win_pct = stats['total_wins'] / total_games if total_games > 0 else 0
            
            result.append({
                'owner': owner,
                'championships': stats['championships'],
                'total_wins': stats['total_wins'],
                'total_losses': stats['total_losses'],
                'win_percentage': round(win_pct, 3),
                'total_points': round(stats['total_points'], 2),
                'seasons_played': len(stats['seasons_played']),
                'avg_points_per_season': round(stats['total_points'] / len(stats['seasons_played']), 2) if stats['seasons_played'] else 0,
                'teams': stats['teams']
            })
        
        # Ordenar por campeonatos y luego por win percentage
        return sorted(result, key=lambda x: (-x['championships'], -x['win_percentage']))
    
    def get_player_career_stats(self, player_name: str) -> Dict:
        """
        Estadísticas de carrera de un jugador específico.
        
        Args:
            player_name: Nombre del jugador
            
        Returns:
            Dict con historial del jugador
        """
        career = []
        teams_played_for = set()
        total_points = 0
        seasons = 0
        
        for year in sorted(self.historical_data.keys()):
            data = self.historical_data[year]
            
            for team in data.get('teams', []):
                for player in team.get('roster', []):
                    if player['name'].lower() == player_name.lower():
                        seasons += 1
                        total_points += player.get('total_points', 0)
                        teams_played_for.add(team['team_name'])
                        
                        career.append({
                            'year': year,
                            'team': team['team_name'],
                            'owner': team.get('owner', 'Unknown'),
                            'avg_points': player.get('avg_points', 0),
                            'total_points': player.get('total_points', 0),
                            'position': player.get('position', ''),
                            'proTeam': player.get('proTeam', '')
                        })
        
        if not career:
            return None
        
        return {
            'player_name': player_name,
            'seasons_owned': seasons,
            'teams_played_for': list(teams_played_for),
            'total_points': round(total_points, 2),
            'career_avg': round(total_points / seasons, 2) if seasons > 0 else 0,
            'history': career
        }
    
    def get_top_scorers_by_season(self, year: int, limit: int = 10) -> List[Dict]:
        """
        Top anotadores de una temporada específica.
        
        Args:
            year: Año de la temporada
            limit: Número de jugadores a retornar
            
        Returns:
            Lista de top jugadores
        """
        if year not in self.historical_data:
            return []
        
        data = self.historical_data[year]
        all_players = []
        
        for team in data.get('teams', []):
            for player in team.get('roster', []):
                all_players.append({
                    'name': player['name'],
                    'team': team['team_name'],
                    'owner': team.get('owner', 'Unknown'),
                    'avg_points': player.get('avg_points', 0),
                    'total_points': player.get('total_points', 0),
                    'position': player.get('position', ''),
                    'proTeam': player.get('proTeam', '')
                })
        
        # Ordenar por puntos promedio
        return sorted(all_players, key=lambda x: x['avg_points'], reverse=True)[:limit]
    
    def get_all_time_top_scorers(self, limit: int = 20) -> List[Dict]:
        """
        Top anotadores históricos (promedio más alto en una temporada).
        
        Args:
            limit: Número de resultados
            
        Returns:
            Lista de mejores temporadas individuales
        """
        all_performances = []
        
        for year, data in self.historical_data.items():
            for team in data.get('teams', []):
                for player in team.get('roster', []):
                    all_performances.append({
                        'name': player['name'],
                        'year': year,
                        'team': team['team_name'],
                        'owner': team.get('owner', 'Unknown'),
                        'avg_points': player.get('avg_points', 0),
                        'total_points': player.get('total_points', 0),
                        'position': player.get('position', ''),
                        'proTeam': player.get('proTeam', '')
                    })
        
        return sorted(all_performances, key=lambda x: x['avg_points'], reverse=True)[:limit]
    
    def get_team_performance_history(self, owner: str) -> Dict:
        """
        Historial de performance de un dueño específico.
        
        Args:
            owner: Nombre del dueño
            
        Returns:
            Dict con historial completo
        """
        history = []
        
        for year in sorted(self.historical_data.keys()):
            data = self.historical_data[year]
            
            for team in data.get('teams', []):
                if team.get('owner', '').lower() == owner.lower():
                    history.append({
                        'year': year,
                        'team_name': team['team_name'],
                        'wins': team.get('wins', 0),
                        'losses': team.get('losses', 0),
                        'points_for': team.get('points_for', 0),
                        'points_against': team.get('points_against', 0),
                        'roster_size': len(team.get('roster', []))
                    })
        
        if not history:
            return None
        
        total_wins = sum(h['wins'] for h in history)
        total_losses = sum(h['losses'] for h in history)
        total_games = total_wins + total_losses
        
        return {
            'owner': owner,
            'seasons': len(history),
            'total_wins': total_wins,
            'total_losses': total_losses,
            'win_percentage': round(total_wins / total_games, 3) if total_games > 0 else 0,
            'history': history
        }
    
    def get_season_summary(self, year: int) -> Optional[Dict]:
        """
        Resumen completo de una temporada.
        
        Args:
            year: Año de la temporada
            
        Returns:
            Dict con resumen de la temporada
        """
        if year not in self.historical_data:
            return None
        
        data = self.historical_data[year]
        teams = data.get('teams', [])
        
        if not teams:
            return None
        
        # Buscar campeón usando playoff_champion si existe
        champion_team_name = data.get('playoff_champion')
        champion = None
        
        if champion_team_name:
            for team in teams:
                if team['team_name'] == champion_team_name or \
                   champion_team_name.lower() in team['team_name'].lower() or \
                   team['team_name'].lower() in champion_team_name.lower():
                    champion = team
                    break
        
        # Fallback: usar el equipo con más victorias
        if not champion:
            champion = max(teams, key=lambda t: t.get('wins', 0))
        
        worst_team = min(teams, key=lambda t: t.get('wins', 0))
        
        # Encontrar top scorer
        all_players = []
        for team in teams:
            for player in team.get('roster', []):
                all_players.append({
                    'name': player['name'],
                    'avg_points': player.get('avg_points', 0),
                    'team': team['team_name']
                })
        
        top_scorer = max(all_players, key=lambda x: x['avg_points']) if all_players else None
        
        return {
            'year': year,
            'league_name': data.get('league_name', 'Fantasy League'),
            'total_teams': len(teams),
            'champion': {
                'team': champion['team_name'],
                'owner': champion.get('owner', 'Unknown'),
                'record': f"{champion['wins']}-{champion['losses']}"
            },
            'worst_team': {
                'team': worst_team['team_name'],
                'owner': worst_team.get('owner', 'Unknown'),
                'record': f"{worst_team['wins']}-{worst_team['losses']}"
            },
            'top_scorer': top_scorer,
            'avg_wins': round(sum(t['wins'] for t in teams) / len(teams), 2),
            'total_points_scored': round(sum(t.get('points_for', 0) for t in teams), 2)
        }
