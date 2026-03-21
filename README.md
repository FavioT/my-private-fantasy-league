# 🏀 My Private Fantasy League

Dashboard de Fantasy Basketball con estilo retro SNES usando NES.css

## 📖 Acerca de

My Private Fantasy League es una aplicación web que transforma los datos de ESPN Fantasy Basketball en un dashboard retro con estética de videojuegos clásicos de SNES. La aplicación consume la API de ESPN en tiempo real para mostrar estadísticas, proyecciones, calendarios de partidos y detalles completos de jugadores con una interfaz pixel art nostálgica.

**Ideal para:**
- 🎮 Fanáticos del basketball que aman la estética retro gaming
- 📊 Managers de fantasy que quieren una vista personalizada de sus ligas
- 🏆 Usuarios de ESPN Fantasy Basketball buscando una experiencia visual única

**Características principales:**
- Visualización en tiempo real de rosters, stats y proyecciones
- Dashboard detallado por jugador con 6 categorías de estadísticas
- Sistema de badges dinámicos para injuries y games-played %
- Calendario de próximos partidos con fechas y rivales
- Modo mock para desarrollo sin credenciales

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
pip install -r requirements.txt

# Configurar variables de entorno
# 1. Copia el archivo de ejemplo:
cp .env.example .env

# 2. Edita .env y completa con tus credenciales de ESPN:
#    - LEAGUE_ID: Tu ID de liga
#    - ESPN_S2: Cookie de sesión (obtener desde navegador)
#    - SWID: Cookie SWID (obtener desde navegador)

# Compilar TypeScript
npx tsc

# Ejecutar servidor (desde la raíz del proyecto)
python src/backend/app.py
```

## 🔐 Obtener Credenciales de ESPN

1. Inicia sesión en [ESPN Fantasy Basketball](https://fantasy.espn.com/basketball/)
2. Abre las DevTools de tu navegador (F12)
3. Ve a la pestaña "Application" o "Storage"
4. En "Cookies" busca:
   - `espn_s2`: Copia el valor completo
   - `SWID`: Copia el valor completo (incluye las llaves `{}`)
5. Pega estos valores en tu archivo `.env`

## 🎯 Uso

1. Abre `http://localhost:5000` en tu navegador
2. Selecciona un equipo para ver su roster
3. Haz clic en un jugador para ver estadísticas detalladas

## ⚙️ Configuración

Todas las configuraciones se manejan mediante variables de entorno en el archivo `.env`:

```bash
# ID de tu liga de ESPN Fantasy Basketball
LEAGUE_ID=76117164

# Año de la temporada
LEAGUE_YEAR=2026

# Cookies de autenticación de ESPN
ESPN_S2=tu_cookie_espn_s2_aqui
SWID={tu_swid_aqui}

# Modo de datos
USE_MOCK=False  # True para datos mock, False para ESPN API real
```

**⚠️ Importante:** Nunca subas tu archivo `.env` a GitHub. Ya está incluido en `.gitignore`.

## 📁 Estructura del Proyecto

```
├── src/
│   ├── backend/              # Código del servidor
│   │   ├── app.py           # Backend Flask
│   │   ├── mocks/           # Datos mock para desarrollo
│   │   │   ├── mock_data.py
│   │   │   └── mock_player_details.py
│   │   └── scripts/         # Scripts de utilidad
│   │       ├── ejemplos_espn_api.py
│   │       ├── inspect_espn_api.py
│   │       └── generate_mock.py
│   └── frontend/            # Código del cliente
│       ├── index.html       # Dashboard principal
│       ├── player-detail.html # Página de detalles
│       └── js/              # JavaScript/TypeScript
│           ├── main.ts
│           ├── main.js
│           ├── player-detail.ts
│           └── player-detail.js
├── .env                     # Configuración (no en git)
├── .env.example             # Ejemplo de configuración
├── requirements.txt         # Dependencias Python
└── tsconfig.json           # Configuración TypeScript
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
