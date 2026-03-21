# Datos Históricos

Este directorio contiene los archivos JSON con las estadísticas históricas de la liga fantasy.

## 📁 Estructura

Los archivos siguen el formato `season_{year}.json`:

```
data/
├── season_2020.json
├── season_2021.json
├── season_2022.json
├── season_2023.json
├── season_2024.json
└── season_2025.json
```

## 🔒 Privacidad

**IMPORTANTE:** Los archivos JSON contienen datos privados de tu liga y **NO están incluidos** en el repositorio por razones de privacidad.

## 🚀 Cómo generar tus datos

Para exportar tus propios datos históricos:

1. Configura tu archivo `.env` con tus credenciales de ESPN
2. Ejecuta el script de exportación:
   ```bash
   cd src/backend/scripts
   python export_historical_data.py --all
   ```

3. Los archivos se generarán en este directorio (`data/`)

## 📝 Formato de ejemplo

```json
{
  "year": 2023,
  "league_name": "Mi Liga Fantasy",
  "current_week": 175,
  "playoff_champion": "Nombre del Equipo Campeón",
  "teams": [
    {
      "team_id": 1,
      "team_name": "Equipo 1",
      "owner": "Nombre",
      "wins": 15,
      "losses": 8,
      "points_for": 2450.5,
      "points_against": 2300.2,
      "roster": [...]
    }
  ]
}
```

## ⚙️ Configuración

Después de exportar, recuerda editar manualmente el campo `playoff_champion` con el nombre del equipo que ganó los playoffs.

Ver [HISTORICAL_DATA_GUIDE.md](../HISTORICAL_DATA_GUIDE.md) para más detalles.
