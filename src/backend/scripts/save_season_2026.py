"""
Script para obtener y guardar los datos de la temporada 2026 en JSON.
Ejecutar desde la raíz del proyecto:
    python src/backend/scripts/save_season_2026.py
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_manager import LeagueDataManager

LEAGUE_CONFIG = {
    'league_id': 76117164,
    'espn_s2': 'AEBmFeUmTSryp0cGx8qZ7bQ5kpucH7tgYxY9k7V776NBbap9vCQaxqUij%2BS2McI7VbhxKxpu%2F%2FNRioOjV%2FCsAG9VVZLS3plbxcWCoUG2ea9rRn%2Bewg7D1Arpte8kYsvYpTGBKyLwaETILDeBHtVr%2FgiTERCurvzPH9JGXBnYkn3bdvAPxptcEAr1Sb1UKikOEhDvUCnG6kKnpf1yepo%2FzSyE80%2BuApbvkNrjgIyjpfHv1AX2Ip%2Bj%2F1WN24m4RFlPx8cBThF3%2BCIhQgPc%2FbhhVEPT6NEgb5q67I6N2qPby48u5Q%3D%3D',
    'swid': '{DA611254-3C72-4FA0-8A47-D236659F6792}'
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
