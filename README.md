# 🏀 My Private Fantasy League

Dashboard de Fantasy Basketball con estilo retro SNES usando NES.css

## 🎮 Características

- **Interfaz Retro**: Estilo pixel art SNES con NES.css
- **Datos en Tiempo Real**: Integración con ESPN Fantasy Basketball API
- **Dashboard Completo**: Estadísticas, proyecciones, calendarios de partidos
- **Responsive**: Optimizado para mobile y desktop

## 🚀 Tecnologías

- **Backend**: Python 3, Flask, espn-api
- **Frontend**: TypeScript, Vanilla JS
- **Estilo**: NES.css, Press Start 2P font
- **Datos**: ESPN Fantasy Basketball API

## 📦 Instalación

```bash
# Instalar dependencias de Python
pip install flask flask-cors espn-api

# Compilar TypeScript
npx tsc

# Ejecutar servidor
python app.py
```

## 🎯 Uso

1. Abre `http://localhost:5000` en tu navegador
2. Selecciona un equipo para ver su roster
3. Haz clic en un jugador para ver estadísticas detalladas

## ⚙️ Configuración

En `app.py`:
- `USE_MOCK = False` → Usa datos reales de ESPN API
- `USE_MOCK = True` → Usa datos mock para desarrollo

## 📁 Estructura del Proyecto

```
├── app.py                    # Backend Flask
├── index.html                # Dashboard principal
├── player-detail.html        # Página de detalles del jugador
├── main.ts                   # Lógica del dashboard
├── player-detail.ts          # Lógica de detalles
├── mock_data.py              # Datos mock de equipos
├── mock_player_details.py    # Datos mock de jugadores
└── tsconfig.json             # Configuración TypeScript
```

## 🏆 Features

- ✅ Lista de equipos con W-L records
- ✅ Roster de jugadores por equipo
- ✅ Estadísticas completas de jugadores
- ✅ Últimos 7 días de rendimiento
- ✅ Proyecciones de temporada
- ✅ Calendario de próximos partidos
- ✅ Badge de % de partidos jugados
- ✅ Estado de lesiones

## 📝 Licencia

Proyecto privado para uso personal
