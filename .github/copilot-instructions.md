# Copilot Instructions

Usar este archivo sólo como punto de entrada.

Fuente canónica de contexto:
- .github/PROJECT_CONTEXT.md

Prioridad para entender el repo:
1. código real
2. .github/PROJECT_CONTEXT.md
3. ROADMAP.md
4. README.md

Reglas de trabajo para Copilot en este proyecto:
- No confiar en documentación histórica de ARCH-002 sin validar contra código.
- Si cambias estructura, ETLs, endpoints, fuentes o comandos, actualiza .github/PROJECT_CONTEXT.md.
- Evitar duplicar contexto en este archivo; mantenerlo delgado.
- Para prioridades de producto y fases, leer ROADMAP.md.
- Para comportamiento real de backend, mirar scheduler.py, routers y etl/.

Puntos importantes actuales:
- Combustibles está implementado y testeado.
- Utilities sigue parcialmente apoyado en TARIFF_HISTORY manual.
- Índices IPC y dólar BCU ya existen en backend/app/etl/indices.py.
- Parte del README y de ARCH-002_COMPLETION_REPORT.txt es aspiracional y puede no reflejar el estado real.

Si hay contradicción entre docs:
- prevalece el código
- luego .github/PROJECT_CONTEXT.md

## Referencias Arquitectónicas

Para desarrollo de frontend (especialmente visualización de gasto público):
- Consultar `docs/inspiration-usaspending/` para patrones de React + Redux + Recharts adaptables
- El archivo `docs/inspiration-usaspending/README_PATRON_GASTO.md` contiene recomendaciones específicas para P2-A
- Ver `.github/PROJECT_CONTEXT.md` › "Referencias Externas" para documentos base
