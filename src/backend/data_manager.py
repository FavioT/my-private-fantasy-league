"""
Data Manager para manejo de datos históricos y actuales de la liga.
Gestiona la carga desde JSON (años históricos) y espn_api (año actual).
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from espn_api.basketball import League


class LeagueDataManager:
    """Administra datos históricos (JSON) y actuales (espn_api)"""

    def __init__(self, data_dir: str = 'data', league_config: Optional[Dict] = None):
        """
        Inicializa el data manager.
        
        Args:
            data_dir: Directorio donde se guardan los archivos JSON históricos
            league_config: Configuración para conectarse a espn_api
                          {'league_id': int, 'espn_s2': str, 'swid': str}
        """
        self.data_dir = data_dir
        self.league_config = league_config or {}
        self.current_year = datetime.now().year
        self.cache = {}  # Cache en memoria para datos históricos
        
        # Crear directorio si no existe
        os.makedirs(self.data_dir, exist_ok=True)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _clean_for_json(self, obj: Any) -> Any:
        """Limpia recursivamente objetos para hacerlos serializables a JSON."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._clean_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Para objetos no serializables, intentar convertir a string
            try:
                return str(obj)
            except:
                return None

    def _get_owner_from_team(self, team) -> str:
        """Extrae el nombre del owner de un objeto Team de espn_api."""
        if not team:
            return 'Unknown'
        if hasattr(team, 'owner') and team.owner:
            return team.owner
        owners = getattr(team, 'owners', None)
        if isinstance(owners, list) and owners:
            first = owners[0]
            if isinstance(first, str):
                return first
            if isinstance(first, dict):
                return (f"{first.get('firstName', '')} {first.get('lastName', '')}".strip()
                        or first.get('displayName', 'Unknown'))
        return 'Unknown'

    def _serialize_player_entry(self, player) -> Dict:
        """Serializa un jugador de roster a dict."""
        player_stats = {}
        if hasattr(player, 'stats'):
            player_stats = self._clean_for_json(player.stats)
        return {
            'playerId': player.playerId,
            'name': player.name,
            'position': player.position,
            'proTeam': player.proTeam,
            'injured': player.injured,
            'injuryStatus': player.injuryStatus if player.injured else None,
            'avg_points': float(getattr(player, 'avg_points', 0) or 0),
            'total_points': float(getattr(player, 'total_points', 0) or 0),
            'stats': player_stats,
        }

    # ── Carga / fetch ────────────────────────────────────────────────────────

    def get_season_data(self, year: int) -> Dict:
        """
        Obtiene datos de una temporada específica.
        - Si existe el JSON guardado: Lee desde JSON
        - Si no existe: Obtiene de espn_api en tiempo real
        
        Args:
            year: Año de la temporada
            
        Returns:
            Dict con datos de la temporada
        """
        file_path = os.path.join(self.data_dir, f"season_{year}.json")
        if os.path.exists(file_path):
            return self._load_from_json(year)
        else:
            return self._fetch_from_espn(year)

    def _load_from_json(self, year: int) -> Dict:
        """Carga datos históricos desde archivo JSON"""
        # Verificar cache primero
        if year in self.cache:
            return self.cache[year]
        
        file_path = os.path.join(self.data_dir, f"season_{year}.json")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encontró archivo para la temporada {year}")
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            self.cache[year] = data  # Guardar en cache
            return data

    def _fetch_from_espn(self, year: int) -> Dict:
        """Obtiene datos actuales desde espn_api"""
        if not self.league_config.get('league_id'):
            raise ValueError("Configuración de liga incompleta")
        
        league = League(
            league_id=self.league_config['league_id'],
            year=year,
            espn_s2=self.league_config.get('espn_s2', ''),
            swid=self.league_config.get('swid', '')
        )
        
        return self._serialize_league_data(league)

    # ── Serialización ────────────────────────────────────────────────────────

    def _serialize_league_data(self, league: League) -> Dict:
        """
        Convierte objeto League de espn_api a diccionario serializable.
        Incluye:
          - teams / rosters activos
          - draft_picks: todos los picks del draft con metadata
          - dropped_drafted_players: jugadores drafteados que fueron dropeados,
            con sus stats consultadas vía player_info()
        """
        teams_data = []
        roster_player_ids: set = set()

        # ── Equipos y rosters activos ────────────────────────────────────────
        for team in league.teams:
            roster = []
            for player in team.roster:
                roster_player_ids.add(player.playerId)
                roster.append(self._serialize_player_entry(player))

            owner = self._get_owner_from_team(team)
            teams_data.append({
                'team_id': team.team_id,
                'team_name': team.team_name,
                'owner': owner,
                'wins': team.wins,
                'losses': team.losses,
                'points_for': getattr(team, 'points_for', 0),
                'points_against': getattr(team, 'points_against', 0),
                'roster': roster
            })

        # ── Draft picks ──────────────────────────────────────────────────────
        draft_picks = []
        dropped_drafted_players = []

        for overall, pick in enumerate(getattr(league, 'draft', []) or [], start=1):
            player_id = getattr(pick, 'playerId', None)
            if player_id is None:
                continue

            pick_team = getattr(pick, 'team', None)
            team_name = getattr(pick_team, 'team_name', '') if pick_team else ''
            owner_name = self._get_owner_from_team(pick_team)
            round_num = int(getattr(pick, 'round_num', 0) or 0)
            round_pick = int(getattr(pick, 'round_pick', 0) or 0)

            draft_picks.append({
                'overall': overall,
                'round_num': round_num,
                'round_pick': round_pick,
                'playerId': player_id,
                'playerName': getattr(pick, 'playerName', None),
                'team_name': team_name,
                'owner': owner_name,
            })

            # Jugador dropeado: no está en ningún roster activo
            if player_id not in roster_player_ids:
                base = {
                    'playerId': player_id,
                    'name': getattr(pick, 'playerName', None) or 'Unknown',
                    'position': '',
                    'proTeam': '',
                    'avg_points': 0.0,
                    'total_points': 0.0,
                    'injured': False,
                    'injuryStatus': None,
                    'stats': {},
                    'draft_round': round_num,
                    'draft_pick': round_pick,
                    'draft_overall': overall,
                    'draft_team': team_name,
                    'draft_owner': owner_name,
                }
                try:
                    p = league.player_info(playerId=player_id)
                    if p:
                        base.update({
                            'name': getattr(p, 'name', base['name']),
                            'position': getattr(p, 'position', ''),
                            'proTeam': getattr(p, 'proTeam', ''),
                            'avg_points': float(getattr(p, 'avg_points', 0) or 0),
                            'total_points': float(getattr(p, 'total_points', 0) or 0),
                            'injured': bool(getattr(p, 'injured', False)),
                            'injuryStatus': (getattr(p, 'injuryStatus', None)
                                             if getattr(p, 'injured', False) else None),
                            'stats': self._clean_for_json(getattr(p, 'stats', {})),
                        })
                except Exception:
                    pass  # Usamos valores base si la API falla
                dropped_drafted_players.append(base)

        return {
            'year': league.year,
            'league_name': (league.settings.name
                            if hasattr(league.settings, 'name') else 'Fantasy League'),
            'current_week': getattr(league, 'current_week', 0),
            'playoff_champion': None,  # Editar manualmente después de los playoffs
            'teams': teams_data,
            'draft_picks': draft_picks,
            'dropped_drafted_players': dropped_drafted_players,
            'exported_at': datetime.now().isoformat()
        }

    # ── Persistencia ─────────────────────────────────────────────────────────

    def save_season_to_json(self, year: int, data: Optional[Dict] = None) -> str:
        """
        Guarda datos de una temporada a archivo JSON.
        Si no se proporciona data, obtiene los datos de espn_api.
        """
        if data is None:
            data = self._fetch_from_espn(year)
        file_path = os.path.join(self.data_dir, f"season_{year}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.cache[year] = data
        return file_path

    def get_available_years(self) -> List[int]:
        """Retorna lista de años con datos disponibles."""
        years = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith('season_') and filename.endswith('.json'):
                    try:
                        years.append(int(filename.replace('season_', '').replace('.json', '')))
                    except ValueError:
                        continue
        if self.league_config.get('league_id'):
            years.append(self.current_year)
        return sorted(years)

    def load_all_historical_data(self) -> Dict[int, Dict]:
        """Carga todos los datos históricos disponibles."""
        all_data = {}
        for year in self.get_available_years():
            try:
                all_data[year] = self._load_from_json(year)
            except FileNotFoundError:
                continue
        return all_data
