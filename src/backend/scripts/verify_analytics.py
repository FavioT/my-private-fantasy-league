"""Script para verificar que las métricas incluyen las temporadas 2020-2026"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_manager import LeagueDataManager
from analytics import HistoricalAnalytics

dm = LeagueDataManager(data_dir=os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'), league_config={'league_id': 0})
an = HistoricalAnalytics(dm)

print("=== Temporadas cargadas ===")
print(sorted(an.historical_data.keys()))

print("\n=== Campeones ===")
for c in an.get_championship_history():
    print(f"  {c['year']}: {c['team_name']} ({c['owner']})")

print("\n=== Top scorers historicos (top 5) ===")
for p in an.get_all_time_top_scorers(limit=5):
    print(f"  {p['name']}: {p['total_points']} pts en {p['seasons']} temporadas")

print("\n=== Estadisticas por owner ===")
for o in an.get_owner_statistics():
    print(f"  {o['owner']}: {o['total_wins']}W-{o['total_losses']}L, campeonatos={o['championships']}, temporadas={o['seasons_played']}")
