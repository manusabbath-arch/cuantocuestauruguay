# Agent Entry Point

Este repo usa un único punto de verdad para contexto compartido entre asistentes.

Leer primero:
- .github/PROJECT_CONTEXT.md

Luego, según necesidad:
- ROADMAP.md para prioridades y fases
- README.md para overview general
- backend/app/services/scheduler.py y backend/app/etl/ para comportamiento real

Reglas:
- No duplicar contexto aquí.
- Si el comportamiento del proyecto cambia, actualizar .github/PROJECT_CONTEXT.md.
- Si una doc histórica contradice al código, prevalece el código.

Advertencia actual:
- ARCH-002_COMPLETION_REPORT.txt no representa fielmente la implementación real y no debe usarse como fuente primaria.
