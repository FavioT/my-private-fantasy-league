"""
Script para obtener y guardar los datos de la temporada 2026 en JSON.
Ejecutar desde la raíz del proyecto:
    python src/backend/scripts/save_season_2026.py
"""

import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env en la raíz del proyecto
_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
load_dotenv(os.path.join(_root, '.env'))

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_manager import LeagueDataManager

LEAGUE_CONFIG = {
    'league_id': int(os.environ['LEAGUE_ID']),
    'espn_s2': os.environ['ESPN_S2'],
    'swid': os.environ['SWID']
}

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')

def main():
    print("Conectando con la API de ESPN para la temporada 2026...")
    manager = LeagueDataManager(data_dir=DATA_DIR, league_config=LEAGUE_CONFIG)

    try:
        file_path = manager.save_season_to_json(2026)
        print(f"Datos guardados correctamente en: {os.path.abspath(file_path)}")

        data = manager.cache[2026]
        print(f"  Liga: {data.get('league_name')}")
        print(f"  Semana actual: {data.get('current_week')}")
        print(f"  Equipos: {len(data.get('teams', []))}")
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
