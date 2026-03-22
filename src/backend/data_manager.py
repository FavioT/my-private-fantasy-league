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
    
    def _clean_for_json(self, obj: Any) -> Any:
        """
        Limpia recursivamente objetos para hacerlos serializables a JSON.
        Convierte datetime a ISO string, elimina objetos no serializables.
        """
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
    
    def get_season_data(self, year: int) -> Dict:
        """
        Obtiene datos de una temporada específica.
        - Años históricos (<current_year): Lee desde JSON
        - Año actual: Obtiene de espn_api en tiempo real
        
        Args:
            year: Año de la temporada
            
        Returns:
            Dict con datos de la temporada
        """
        if year < self.current_year:
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
    
    def _serialize_league_data(self, league: League) -> Dict:
        """Convierte objeto League de espn_api a diccionario serializable"""
        teams_data = []
        
        for team in league.teams:
            roster = []
            for player in team.roster:
                # Obtener stats y limpiarlos de objetos no serializables
                player_stats = {}
                if hasattr(player, 'stats'):
                    player_stats = self._clean_for_json(player.stats)
                
                roster.append({
                    'playerId': player.playerId,
                    'name': player.name,
                    'position': player.position,
                    'proTeam': player.proTeam,
                    'injured': player.injured,
                    'injuryStatus': player.injuryStatus if player.injured else None,
                    'avg_points': getattr(player, 'avg_points', 0),
                    'total_points': getattr(player, 'total_points', 0),
                    'stats': player_stats
                })
            
            # Obtener owner - puede estar en varios formatos según la versión de la API
            owner = 'Unknown'
            if hasattr(team, 'owner'):
                owner = team.owner
            elif hasattr(team, 'owners'):
                # Algunos años puede ser una lista
                owners_list = team.owners
                if isinstance(owners_list, list) and len(owners_list) > 0:
                    owner = owners_list[0] if isinstance(owners_list[0], str) else owners_list[0].get('firstName', 'Unknown')
                elif isinstance(owners_list, str):
                    owner = owners_list
            
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
        
        return {
            'year': league.year,
            'league_name': league.settings.name if hasattr(league.settings, 'name') else 'Fantasy League',
            'current_week': getattr(league, 'current_week', 0),
            'playoff_champion': None,  # Editar manualmente después de los playoffs
            'teams': teams_data,
            'exported_at': datetime.now().isoformat()
        }
    
    def save_season_to_json(self, year: int, data: Optional[Dict] = None) -> str:
        """
        Guarda datos de una temporada a archivo JSON.
        Si no se proporciona data, obtiene los datos de espn_api.
        
        Args:
            year: Año de la temporada
            data: Datos a guardar (opcional, si None obtiene de espn_api)
            
        Returns:
            Ruta del archivo guardado
        """
        if data is None:
            data = self._fetch_from_espn(year)
        
        file_path = os.path.join(self.data_dir, f"season_{year}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Actualizar cache
        self.cache[year] = data
        
        return file_path
    
    def get_available_years(self) -> List[int]:
        """Retorna lista de años con datos disponibles"""
        years = []
        
        # Buscar archivos JSON
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith('season_') and filename.endswith('.json'):
                    try:
                        year = int(filename.replace('season_', '').replace('.json', ''))
                        years.append(year)
                    except ValueError:
                        continue
        
        # Agregar año actual si hay configuración
        if self.league_config.get('league_id'):
            years.append(self.current_year)
        
        return sorted(years)
    
    def load_all_historical_data(self) -> Dict[int, Dict]:
        """Carga todos los datos históricos disponibles"""
        all_data = {}
        
        for year in self.get_available_years():
            if year < self.current_year:
                try:
                    all_data[year] = self._load_from_json(year)
                except FileNotFoundError:
                    continue
        
        return all_data
