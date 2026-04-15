"""
Módulo de analytics para consultas multi-año sobre datos históricos.
Permite análisis y estadísticas combinando múltiples temporadas.
"""

from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
from espn_api.basketball import League
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

    def _extract_owner_name(self, team) -> str:
        """Obtiene el nombre del owner desde dicts históricos u objetos Team de espn_api."""
        if not team:
            return 'Unknown'

        if isinstance(team, dict):
            owner = team.get('owner')
            if owner:
                return owner
            owners = team.get('owners')
        else:
            owner = getattr(team, 'owner', None)
            if owner:
                return owner
            owners = getattr(team, 'owners', None)

        if isinstance(owners, list) and owners:
            first_owner = owners[0]
            if isinstance(first_owner, dict):
                full_name = f"{first_owner.get('firstName', '')} {first_owner.get('lastName', '')}".strip()
                return full_name or first_owner.get('displayName', 'Unknown')
            if isinstance(first_owner, str):
                return first_owner

        return 'Unknown'

    def _extract_games_played(self, player: Dict, year: int) -> int:
        """Obtiene GP desde el snapshot serializado del jugador."""
        stats = player.get('stats') or {}
        if not isinstance(stats, dict):
            return 0

        total_stats = stats.get(f'{year}_total', {})
        if not isinstance(total_stats, dict):
            return 0

        avg_stats = total_stats.get('avg', {})
        if not isinstance(avg_stats, dict):
            return 0

        return int(avg_stats.get('GP', 0) or 0)

    def _get_live_league(self, year: int) -> Optional[League]:
        """Devuelve la liga en vivo si hay credenciales configuradas."""
        config = self.data_manager.league_config or {}
        league_id = config.get('league_id')
        espn_s2 = config.get('espn_s2')
        swid = config.get('swid')

        if not league_id or not espn_s2 or not swid:
            return None

        try:
            return League(
                league_id=league_id,
                year=year,
                espn_s2=espn_s2,
                swid=swid
            )
        except Exception:
            return None

    def _build_season_player_pool(self, year: int) -> tuple[List[Dict], Dict[int, Dict], bool, int]:
        """Construye el pool de jugadores del año y, si existe, metadata viva de draft."""
        live_league = self._get_live_league(year)
        draft_map: Dict[int, Dict] = {}
        total_rounds = 0

        if live_league:
            players = []
            for team in live_league.teams:
                owner = self._extract_owner_name(team)
                for player in team.roster:
                    stats = player.stats if hasattr(player, 'stats') and isinstance(player.stats, dict) else {}
                    total_stats = stats.get(f'{year}_total', {}) if isinstance(stats, dict) else {}
                    avg_stats = total_stats.get('avg', {}) if isinstance(total_stats, dict) else {}

                    players.append({
                        'player_id': player.playerId,
                        'name': player.name,
                        'team_name': team.team_name,
                        'owner': owner,
                        'position': getattr(player, 'position', ''),
                        'pro_team': getattr(player, 'proTeam', ''),
                        'total_points': float(getattr(player, 'total_points', 0) or 0),
                        'avg_points': float(getattr(player, 'avg_points', 0) or 0),
                        'games_played': int(avg_stats.get('GP', 0) or 0),
                        'acquisition_type': (getattr(player, 'acquisitionType', '') or '').upper(),
                        'injured': bool(getattr(player, 'injured', False)),
                        'injury_status': getattr(player, 'injuryStatus', None) if getattr(player, 'injured', False) else None,
                    })

            for overall_pick, pick in enumerate(getattr(live_league, 'draft', []) or [], start=1):
                round_num = int(getattr(pick, 'round_num', 0) or 0)
                total_rounds = max(total_rounds, round_num)
                player_id = getattr(pick, 'playerId', None)
                if player_id is None:
                    continue

                draft_map[player_id] = {
                    'draft_round': round_num,
                    'draft_pick': int(getattr(pick, 'round_pick', 0) or 0),
                    'draft_overall': overall_pick,
                    'draft_team': getattr(getattr(pick, 'team', None), 'team_name', ''),
                    'draft_owner': self._extract_owner_name(getattr(pick, 'team', None))
                }

            # Incorporar jugadores dropeados guardados en el JSON de la temporada.
            # Los datos en vivo sólo contienen rosters activos; los dropeados se
            # pierden de todos los cálculos de premios si no los agregamos aquí.
            try:
                saved_data = self.data_manager.get_season_data(year)
                roster_ids_live = {p['player_id'] for p in players if p['player_id'] is not None}
                for dropped in saved_data.get('dropped_drafted_players', []):
                    pid = dropped.get('playerId')
                    if pid is None or pid in roster_ids_live:
                        continue
                    players.append({
                        'player_id': pid,
                        'name': dropped.get('name', 'Unknown'),
                        'team_name': dropped.get('draft_team', ''),
                        'owner': dropped.get('draft_owner', ''),
                        'position': dropped.get('position', ''),
                        'pro_team': dropped.get('proTeam', ''),
                        'total_points': float(dropped.get('total_points', 0) or 0),
                        'avg_points': float(dropped.get('avg_points', 0) or 0),
                        'games_played': self._extract_games_played(dropped, year),
                        'acquisition_type': None,
                        'injured': bool(dropped.get('injured', False)),
                        'injury_status': dropped.get('injuryStatus'),
                        'draft_round': dropped.get('draft_round'),
                        'draft_pick': dropped.get('draft_pick'),
                        'draft_overall': dropped.get('draft_overall'),
                        'draft_team': dropped.get('draft_team'),
                        'draft_owner': dropped.get('draft_owner'),
                    })
                    # Asegurar que el draft_map también tenga la entrada de este jugador
                    if pid not in draft_map and dropped.get('draft_overall'):
                        draft_map[pid] = {
                            'draft_round': dropped.get('draft_round'),
                            'draft_pick': dropped.get('draft_pick'),
                            'draft_overall': dropped.get('draft_overall'),
                            'draft_team': dropped.get('draft_team', ''),
                            'draft_owner': dropped.get('draft_owner', ''),
                        }
            except Exception:
                pass  # Si el JSON no existe aún, continuar sólo con datos en vivo

            return players, draft_map, True, total_rounds

        season_data = self.data_manager.get_season_data(year)
        players = []

        # Jugadores en roster activo
        for team in season_data.get('teams', []):
            owner = self._extract_owner_name(team)
            for player in team.get('roster', []):
                players.append({
                    'player_id': player.get('playerId'),
                    'name': player.get('name', 'Unknown'),
                    'team_name': team.get('team_name', ''),
                    'owner': owner,
                    'position': player.get('position', ''),
                    'pro_team': player.get('proTeam', ''),
                    'total_points': float(player.get('total_points', 0) or 0),
                    'avg_points': float(player.get('avg_points', 0) or 0),
                    'games_played': self._extract_games_played(player, year),
                    'acquisition_type': None,
                    'injured': bool(player.get('injured', False)),
                    'injury_status': player.get('injuryStatus')
                })

        # Jugadores drafteados que fueron dropeados durante la temporada
        roster_ids_in_pool = {p['player_id'] for p in players if p['player_id'] is not None}
        for dropped in season_data.get('dropped_drafted_players', []):
            pid = dropped.get('playerId')
            if pid in roster_ids_in_pool:
                continue  # ya está en el pool via roster
            players.append({
                'player_id': pid,
                'name': dropped.get('name', 'Unknown'),
                'team_name': dropped.get('draft_team', ''),
                'owner': dropped.get('draft_owner', ''),
                'position': dropped.get('position', ''),
                'pro_team': dropped.get('proTeam', ''),
                'total_points': float(dropped.get('total_points', 0) or 0),
                'avg_points': float(dropped.get('avg_points', 0) or 0),
                'games_played': self._extract_games_played(dropped, year),
                'acquisition_type': None,
                'injured': bool(dropped.get('injured', False)),
                'injury_status': dropped.get('injuryStatus'),
                # Agregar metadata de draft directamente
                'draft_round': dropped.get('draft_round'),
                'draft_pick': dropped.get('draft_pick'),
                'draft_overall': dropped.get('draft_overall'),
                'draft_team': dropped.get('draft_team'),
                'draft_owner': dropped.get('draft_owner'),
            })

        # Construir draft_map desde draft_picks guardados en el JSON
        for pick in season_data.get('draft_picks', []):
            pid = pick.get('playerId')
            if pid is None:
                continue
            round_num = int(pick.get('round_num', 0) or 0)
            total_rounds = max(total_rounds, round_num)
            if pid not in draft_map:
                draft_map[pid] = {
                    'draft_round': round_num,
                    'draft_pick': int(pick.get('round_pick', 0) or 0),
                    'draft_overall': int(pick.get('overall', 0) or 0),
                    'draft_team': pick.get('team_name', ''),
                    'draft_owner': pick.get('owner', ''),
                }

        return players, draft_map, False, total_rounds

    def _build_previous_season_map(self, year: int) -> Dict[int, Dict]:
        """Mapa por player_id con stats del año anterior."""
        if year not in self.historical_data:
            return {}

        previous_map = {}
        previous_data = self.historical_data[year]

        # Jugadores en roster activo
        for team in previous_data.get('teams', []):
            for player in team.get('roster', []):
                player_id = player.get('playerId')
                if player_id is None:
                    continue
                previous_map[player_id] = {
                    'previous_avg_points': float(player.get('avg_points', 0) or 0),
                    'previous_total_points': float(player.get('total_points', 0) or 0),
                    'previous_games_played': self._extract_games_played(player, year)
                }

        # Jugadores dropeados que fueron drafteados ese año
        for dropped in previous_data.get('dropped_drafted_players', []):
            player_id = dropped.get('playerId')
            if player_id is None or player_id in previous_map:
                continue
            previous_map[player_id] = {
                'previous_avg_points': float(dropped.get('avg_points', 0) or 0),
                'previous_total_points': float(dropped.get('total_points', 0) or 0),
                'previous_games_played': self._extract_games_played(dropped, year)
            }

        return previous_map

    def _player_payload(self, player: Dict) -> Dict:
        """Serializa un jugador para el frontend de premios."""
        return {
            'player_id': player.get('player_id'),
            'name': player.get('name', 'Unknown'),
            'team_name': player.get('team_name', ''),
            'owner': player.get('owner', 'Unknown'),
            'position': player.get('position', ''),
            'pro_team': player.get('pro_team', ''),
            'total_points': round(player.get('total_points', 0), 1),
            'avg_points': round(player.get('avg_points', 0), 2),
            'games_played': int(player.get('games_played', 0) or 0),
            'season_rank': player.get('season_rank'),
            'acquisition_type': player.get('acquisition_type'),
            'draft_round': player.get('draft_round'),
            'draft_pick': player.get('draft_pick'),
            'draft_overall': player.get('draft_overall'),
            'draft_team': player.get('draft_team'),
            'draft_owner': player.get('draft_owner'),
            'previous_avg_points': round(player['previous_avg_points'], 2) if player.get('previous_avg_points') is not None else None,
            'previous_total_points': round(player['previous_total_points'], 1) if player.get('previous_total_points') is not None else None,
            'avg_delta': round(player['avg_delta'], 2) if player.get('avg_delta') is not None else None,
            'total_delta': round(player['total_delta'], 1) if player.get('total_delta') is not None else None,
            'value_over_slot': player.get('value_over_slot'),
            'miss_score': player.get('miss_score')
        }

    def _award_payload(
        self,
        award_id: str,
        title: str,
        subtitle: str,
        icon: str,
        theme: str,
        criteria: str,
        winner: Optional[Dict],
        finalists: Optional[List[Dict]] = None,
        reason: Optional[str] = None,
        metrics: Optional[List[Dict]] = None,
        available: bool = True,
        unavailable_reason: Optional[str] = None
    ) -> Dict:
        """Estructura estándar para un premio."""
        return {
            'id': award_id,
            'title': title,
            'subtitle': subtitle,
            'icon': icon,
            'theme': theme,
            'criteria': criteria,
            'available': available,
            'reason': reason,
            'metrics': metrics or [],
            'winner': self._player_payload(winner) if winner else None,
            'finalists': [self._player_payload(player) for player in (finalists or [])],
            'unavailable_reason': unavailable_reason
        }

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
        
        # Ordenar por puntos totales
        return sorted(all_players, key=lambda x: x['total_points'], reverse=True)[:limit]
    
    def get_all_time_top_scorers(self, limit: int = 20) -> List[Dict]:
        """
        Top anotadores históricos (suma total de puntos en todas las temporadas).
        
        Args:
            limit: Número de resultados
            
        Returns:
            Lista de jugadores ordenados por puntos totales acumulados en todos los años
        """
        player_stats = defaultdict(lambda: {
            'total_points': 0.0,
            'seasons': 0,
            'teams': set(),
            'position': '',
            'proTeam': ''
        })
        
        for year, data in self.historical_data.items():
            for team in data.get('teams', []):
                for player in team.get('roster', []):
                    name = player['name']
                    player_stats[name]['total_points'] += player.get('total_points', 0)
                    player_stats[name]['seasons'] += 1
                    player_stats[name]['teams'].add(team['team_name'])
                    if player.get('position'):
                        player_stats[name]['position'] = player['position']
                    if player.get('proTeam'):
                        player_stats[name]['proTeam'] = player['proTeam']
        
        result = []
        for name, stats in player_stats.items():
            seasons = stats['seasons']
            total = round(stats['total_points'], 2)
            result.append({
                'name': name,
                'total_points': total,
                'avg_points': round(total / seasons, 2) if seasons > 0 else 0,
                'seasons': seasons,
                'team': ', '.join(sorted(stats['teams'])),
                'position': stats['position'],
                'proTeam': stats['proTeam']
            })
        
        return sorted(result, key=lambda x: x['total_points'], reverse=True)[:limit]
    
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

    def get_owner_top_players(self, owner: str, limit: int = 15) -> List[Dict]:
        """
        Top jugadores históricos de un dueño específico.

        Args:
            owner: Nombre del dueño
            limit: Número de resultados

        Returns:
            Lista de jugadores ordenados por puntos totales acumulados mientras fueron del owner
        """
        player_stats = defaultdict(lambda: {
            'total_points': 0.0,
            'seasons_owned': 0,
            'best_avg': 0.0,
            'position': '',
            'proTeam': ''
        })

        for year, data in self.historical_data.items():
            for team in data.get('teams', []):
                if team.get('owner', '').lower() == owner.lower():
                    for player in team.get('roster', []):
                        name = player['name']
                        player_stats[name]['total_points'] += player.get('total_points', 0)
                        player_stats[name]['seasons_owned'] += 1
                        avg = player.get('avg_points', 0)
                        if avg > player_stats[name]['best_avg']:
                            player_stats[name]['best_avg'] = avg
                        if player.get('position'):
                            player_stats[name]['position'] = player['position']
                        if player.get('proTeam'):
                            player_stats[name]['proTeam'] = player['proTeam']

        result = []
        for name, stats in player_stats.items():
            result.append({
                'name': name,
                'total_points': round(stats['total_points'], 2),
                'best_avg': round(stats['best_avg'], 2),
                'seasons_owned': stats['seasons_owned'],
                'position': stats['position'],
                'proTeam': stats['proTeam']
            })

        return sorted(result, key=lambda x: x['total_points'], reverse=True)[:limit]

    def get_season_awards(self, year: int, compare_year: Optional[int] = None) -> Optional[Dict]:
        """Calcula premios fantasy de una temporada al estilo NBA."""
        if compare_year is None:
            compare_year = year - 1

        try:
            players, draft_map, live_data_used, total_rounds = self._build_season_player_pool(year)
        except FileNotFoundError:
            return None

        if not players:
            return None

        previous_map = self._build_previous_season_map(compare_year)

        # Construir el conjunto de jugadores que aparecieron en CUALQUIER temporada anterior al año actual
        all_historical_player_ids: set = set()
        all_historical_player_names: set = set()
        for hist_year, hist_data in self.historical_data.items():
            if hist_year >= year:
                continue
            for hist_team in hist_data.get('teams', []):
                for hist_player in hist_team.get('roster', []):
                    pid = hist_player.get('playerId')
                    if pid is not None:
                        all_historical_player_ids.add(pid)
                    pname = (hist_player.get('name') or '').strip().lower()
                    if pname:
                        all_historical_player_names.add(pname)
            # También incluir jugadores dropeados que fueron drafteados ese año
            for dropped in hist_data.get('dropped_drafted_players', []):
                pid = dropped.get('playerId')
                if pid is not None:
                    all_historical_player_ids.add(pid)
                pname = (dropped.get('name') or '').strip().lower()
                if pname:
                    all_historical_player_names.add(pname)

        for player in players:
            player.update(draft_map.get(player.get('player_id'), {}))

            previous = previous_map.get(player.get('player_id'), {})
            player['previous_avg_points'] = previous.get('previous_avg_points')
            player['previous_total_points'] = previous.get('previous_total_points')
            player['previous_games_played'] = previous.get('previous_games_played')

            if player.get('previous_avg_points') is not None:
                player['avg_delta'] = player.get('avg_points', 0) - player.get('previous_avg_points', 0)
                player['total_delta'] = player.get('total_points', 0) - player.get('previous_total_points', 0)
            else:
                player['avg_delta'] = None
                player['total_delta'] = None

            # Marcar si el jugador es genuinamente nuevo (no apareció en ninguna temporada anterior)
            pid = player.get('player_id')
            pname = (player.get('name') or '').strip().lower()
            if pid is not None:
                player['is_true_rookie'] = pid not in all_historical_player_ids
            else:
                player['is_true_rookie'] = pname not in all_historical_player_names

        ranked_players = sorted(
            players,
            key=lambda player: (player.get('total_points', 0), player.get('avg_points', 0)),
            reverse=True
        )

        for index, player in enumerate(ranked_players, start=1):
            player['season_rank'] = index
            if player.get('draft_overall'):
                player['value_over_slot'] = int(player['draft_overall']) - index
                player['miss_score'] = index - int(player['draft_overall'])

        eligible_players = [player for player in ranked_players if player.get('games_played', 0) >= 10] or ranked_players

        awards = []

        # MVP
        mvp_candidates = eligible_players[:3]
        mvp = mvp_candidates[0] if mvp_candidates else None
        awards.append(self._award_payload(
            award_id='mvp',
            title='MVP de la season fantasy',
            subtitle=f'Mayor producción total en {year}',
            icon='trophy',
            theme='gold',
            criteria='Se ordena por puntos fantasy totales y se desempata por promedio.',
            winner=mvp,
            finalists=mvp_candidates[1:],
            reason=(
                f"{mvp['name']} lidera la temporada con {round(mvp['total_points'], 1)} puntos fantasy "
                f"en {mvp['games_played']} partidos."
            ) if mvp else None,
            metrics=[
                {'label': 'PTS', 'value': round(mvp['total_points'], 1) if mvp else '—'},
                {'label': 'AVG', 'value': round(mvp['avg_points'], 2) if mvp else '—'},
                {'label': 'GP', 'value': mvp['games_played'] if mvp else '—'}
            ]
        ))

        # Draft steal
        drafted_players = [player for player in ranked_players if player.get('draft_overall')]
        late_round_threshold = max(6, int(total_rounds * 0.6)) if total_rounds else 6
        late_round_pool = [player for player in drafted_players if (player.get('draft_round') or 0) >= late_round_threshold]
        if not late_round_pool and drafted_players:
            late_round_pool = [player for player in drafted_players if (player.get('draft_round') or 0) >= 5] or drafted_players

        draft_steal_candidates = sorted(
            late_round_pool,
            key=lambda player: (player.get('value_over_slot', -9999), player.get('total_points', 0), player.get('avg_points', 0)),
            reverse=True
        )[:3]
        draft_steal = draft_steal_candidates[0] if draft_steal_candidates else None
        awards.append(self._award_payload(
            award_id='draft-steal',
            title='Robo del draft',
            subtitle='El pick tardío que mejor pagó',
            icon='star',
            theme='green',
            criteria='Solo picks de rondas tardías. Se mide por diferencia entre pick global y ranking actual.',
            winner=draft_steal,
            finalists=draft_steal_candidates[1:],
            reason=(
                f"{draft_steal['name']} fue tomado en la ronda {draft_steal['draft_round']} "
                f"(pick global {draft_steal['draft_overall']}) y hoy marcha #{draft_steal['season_rank']}."
            ) if draft_steal else None,
            metrics=[
                {'label': 'RND', 'value': draft_steal['draft_round'] if draft_steal else '—'},
                {'label': 'PICK', 'value': draft_steal['draft_overall'] if draft_steal else '—'},
                {'label': 'VAL', 'value': draft_steal['value_over_slot'] if draft_steal else '—'}
            ],
            available=bool(draft_steal),
            unavailable_reason='No hay datos de draft disponibles para esta temporada.' if not draft_steal else None
        ))

        # Free agency steal
        free_agency_types = {'ADD', 'WAIVERS', 'FREEAGENT', 'FREE_AGENT'}
        free_agency_candidates = [
            player for player in ranked_players
            if (player.get('acquisition_type') or '').upper() in free_agency_types
        ][:3]
        free_agency_steal = free_agency_candidates[0] if free_agency_candidates else None
        awards.append(self._award_payload(
            award_id='free-agency-steal',
            title='Robo del free agency',
            subtitle='La mejor incorporación del waiver wire',
            icon='coin',
            theme='blue',
            criteria='Entre jugadores agregados desde free agency o waivers, gana el de mayor puntaje total.',
            winner=free_agency_steal,
            finalists=free_agency_candidates[1:],
            reason=(
                f"{free_agency_steal['name']} es la mejor apuesta de free agency con "
                f"{round(free_agency_steal['total_points'], 1)} puntos acumulados."
            ) if free_agency_steal else None,
            metrics=[
                {'label': 'PTS', 'value': round(free_agency_steal['total_points'], 1) if free_agency_steal else '—'},
                {'label': 'AVG', 'value': round(free_agency_steal['avg_points'], 2) if free_agency_steal else '—'},
                {'label': 'ACQ', 'value': (free_agency_steal.get('acquisition_type') or '—') if free_agency_steal else '—'}
            ],
            available=bool(free_agency_steal),
            unavailable_reason='No hay metadata de adquisiciones en vivo para calcular free agency.' if not free_agency_steal else None
        ))

        # Worst pick
        early_round_pool = [player for player in drafted_players if (player.get('draft_round') or 0) <= 4]
        if not early_round_pool and drafted_players:
            early_round_pool = [player for player in drafted_players if (player.get('draft_round') or 0) <= 5] or drafted_players

        worst_pick_candidates = sorted(
            early_round_pool,
            key=lambda player: (player.get('miss_score', -9999), -player.get('total_points', 0), -player.get('avg_points', 0)),
            reverse=True
        )[:3]
        worst_pick = worst_pick_candidates[0] if worst_pick_candidates else None
        awards.append(self._award_payload(
            award_id='worst-pick',
            title='Peor pick',
            subtitle='La apuesta premium que menos devolvió',
            icon='close',
            theme='red',
            criteria='Entre picks altos del draft, pierde el que más cayó frente a su slot original.',
            winner=worst_pick,
            finalists=worst_pick_candidates[1:],
            reason=(
                f"{worst_pick['name']} salió {worst_pick['draft_overall']} global y hoy figura #{worst_pick['season_rank']}."
            ) if worst_pick else None,
            metrics=[
                {'label': 'RND', 'value': worst_pick['draft_round'] if worst_pick else '—'},
                {'label': 'PICK', 'value': worst_pick['draft_overall'] if worst_pick else '—'},
                {'label': 'DROP', 'value': worst_pick['miss_score'] if worst_pick else '—'}
            ],
            available=bool(worst_pick),
            unavailable_reason='No hay datos de draft disponibles para esta temporada.' if not worst_pick else None
        ))

        # MIP
        mip_pool = [
            player for player in ranked_players
            if player.get('previous_avg_points') is not None
            and player.get('games_played', 0) >= 15
            and (player.get('previous_games_played') or 0) >= 10
            and (player.get('avg_delta') or 0) > 0
        ]
        mip_candidates = sorted(
            mip_pool,
            key=lambda player: (player.get('avg_delta', 0), player.get('total_delta', 0), player.get('avg_points', 0)),
            reverse=True
        )[:3]
        mip = mip_candidates[0] if mip_candidates else None
        awards.append(self._award_payload(
            award_id='mip',
            title='MIP',
            subtitle=f'La mayor mejora entre {compare_year} y {year}',
            icon='like',
            theme='purple',
            criteria='Se compara el salto en promedio fantasy, con piso mínimo de partidos en ambos años.',
            winner=mip,
            finalists=mip_candidates[1:],
            reason=(
                f"{mip['name']} subió de {round(mip['previous_avg_points'], 2)} a {round(mip['avg_points'], 2)} "
                f"puntos fantasy por partido."
            ) if mip else None,
            metrics=[
                {'label': '2025', 'value': round(mip['previous_avg_points'], 2) if mip else '—'},
                {'label': '2026', 'value': round(mip['avg_points'], 2) if mip else '—'},
                {'label': 'DELTA', 'value': round(mip['avg_delta'], 2) if mip else '—'}
            ],
            available=bool(mip),
            unavailable_reason=f'No hay suficiente historial {compare_year} para calcular la mejora.' if not mip else None
        ))

        # Novato del Año — jugador que NO aparecía en NINGUNA temporada anterior (2020 en adelante)
        rookie_pool = [
            player for player in ranked_players
            if player.get('is_true_rookie', False)
            and player.get('games_played', 0) >= 5
        ]
        rookie_candidates = sorted(
            rookie_pool,
            key=lambda player: (player.get('total_points', 0), player.get('avg_points', 0)),
            reverse=True
        )[:3]
        rookie = rookie_candidates[0] if rookie_candidates else None
        rookie_hist_years = sorted(y for y in self.historical_data.keys() if y < year)
        rookie_years_str = f"{min(rookie_hist_years)}–{max(rookie_hist_years)}" if rookie_hist_years else str(year - 1)
        awards.append(self._award_payload(
            award_id='rookie',
            title='Novato del Año',
            subtitle=f'Primera aparición en la liga en {year}',
            icon='heart',
            theme='blue',
            criteria=(
                f'Jugadores que no figuraban en ningún roster entre {rookie_years_str}. '
                'Entre ellos, gana el de mayor puntaje fantasy total con mínimo 5 partidos.'
            ),
            winner=rookie,
            finalists=rookie_candidates[1:],
            reason=(
                f"{rookie['name']} debuta en la liga en {year} con "
                f"{round(rookie['total_points'], 1)} pts fantasy en {rookie['games_played']} partidos "
                f"({round(rookie['avg_points'], 2)} AVG)."
            ) if rookie else None,
            metrics=[
                {'label': 'PTS', 'value': round(rookie['total_points'], 1) if rookie else '—'},
                {'label': 'AVG', 'value': round(rookie['avg_points'], 2) if rookie else '—'},
                {'label': 'GP',  'value': rookie['games_played'] if rookie else '—'}
            ],
            available=bool(rookie),
            unavailable_reason=(
                f'No hay novatos con suficientes partidos en {year} '
                f'(verificado contra temporadas {rookie_years_str}).'
            ) if not rookie else None
        ))

        notes = [
            f'Premios calculados con snapshot {year} y comparación vs {compare_year}.',
            'El MVP usa puntos fantasy totales; el MIP usa salto en promedio fantasy por partido.',
            f'El Novato del Año verifica contra todas las temporadas históricas ({rookie_years_str}): el jugador no debe haber estado activo en ninguna de ellas.'
        ]
        if live_data_used:
            notes.append('Draft y free agency usan metadata viva de ESPN para acquisitionType y picks del draft.')
        else:
            notes.append('Sin metadata viva de ESPN, algunos premios pueden quedar limitados.')

        return {
            'year': year,
            'compare_year': compare_year,
            'generated_at': datetime.now().isoformat(),
            'data_source': 'live' if live_data_used else 'historical',
            'methodology_notes': notes,
            'awards': awards
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
