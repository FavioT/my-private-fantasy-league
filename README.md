<img src="src/frontend/favicon.ico" alt="My Private Fantasy League logo" width="96" height="96">

# My Private Fantasy League

Dashboard privado de Fantasy Basketball con estética retro, construido con Flask, TypeScript y NES.css.

## Resumen

La aplicación muestra datos de una liga de ESPN Fantasy Basketball, incluyendo equipos, rosters, estadísticas y detalle de jugadores. Puede trabajar con datos reales de ESPN o en modo mock para desarrollo.

## Stack

- Backend: Python, Flask, espn-api
- Frontend: TypeScript, Vanilla JS
- UI: NES.css

## Puesta en marcha

```bash
pip install -r requirements.txt
npx tsc
python src/backend/app.py
```

La app queda disponible en `http://localhost:5000`.

## Configuración

Variables principales en `.env`:

```bash
LEAGUE_ID=your_league_id_here
LEAGUE_YEAR=2026
ESPN_S2=tu_cookie_espn_s2_aqui
SWID={tu_swid_aqui}
USE_MOCK=False
```

Si no quieres usar credenciales de ESPN durante el desarrollo, configura `USE_MOCK=True`.

## Estructura

```text
src/backend/   Backend Flask y lógica de datos
src/frontend/  HTML, assets y scripts del cliente
data/          Temporadas guardadas en JSON
api/           Entrada para despliegue
```

## Licencia

Proyecto privado para uso personal.
