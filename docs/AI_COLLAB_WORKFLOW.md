# Plantilla Minima de Trabajo en Paralelo (Copilot + Claude)

Objetivo:
- Permitir trabajo paralelo sin duplicacion de esfuerzos ni conflictos de cambios.

Fuente de verdad:
1. Codigo real
2. .github/PROJECT_CONTEXT.md
3. ROADMAP.md
4. README.md

## 1) Inicio de cada sesion

Checklist rapido:
- Leer .github/PROJECT_CONTEXT.md
- Leer ROADMAP.md (solo la fase/sprint activo)
- Definir una sola tarea concreta para la sesion
- Declarar alcance: archivos permitidos + criterio de terminado

Plantilla de arranque:
- Tarea:
- Alcance (archivos):
- Fuera de alcance:
- Criterio de terminado:
- Riesgos:

## 2) Regla de particion de trabajo

Regla:
- Un asistente por area funcional por sesion.
- Evitar que ambos editen el mismo archivo al mismo tiempo.

Particion sugerida:
- Copilot: implementacion y tests en backend/app y backend/tests
- Claude: documentacion, validaciones cruzadas y QA de cambios

Si ambos tocan codigo:
- Dividir por modulo (ejemplo: etl vs routers)
- Confirmar archivos reservados antes de editar

## 3) Protocolo de reserva de archivos

Antes de editar, publicar reserva temporal:
- Asistente:
- Archivo(s):
- Motivo:
- Tiempo estimado:

Al finalizar, liberar reserva y publicar resultado:
- Cambios hechos:
- Tests ejecutados:
- Riesgos pendientes:

## 4) Protocolo de handoff

Formato unico de handoff entre asistentes:
- Contexto breve:
- Decision tomada:
- Archivos tocados:
- Comandos ejecutados:
- Resultado de tests:
- Siguiente accion recomendada:

## 5) Definicion de terminado (DoD)

Una tarea se considera terminada si:
- Cumple criterio funcional acordado
- Tests relevantes pasan en local
- Se actualiza documentacion afectada
- Si cambia estructura/ETL/endpoints/comandos, se actualiza .github/PROJECT_CONTEXT.md

## 6) Reglas de seguridad de cambios

- No reescribir docs canonicas sin validar contra codigo
- No mezclar refactor grande con feature en la misma tarea
- No cerrar una tarea con tests rotos
- Si hay contradiccion documental, gana el codigo

## 7) Cadencia recomendada (fase a fase)

Para respetar trabajo incremental:
- Fase 1: implementacion minima + test critico
- Fase 2: endurecimiento (errores, observabilidad, docs)

## 8) Comandos base de verificacion

Backend:
- cd backend
- venv/bin/python -m pytest tests/test_combustibles_etl.py
- venv/bin/python -m pytest tests/test_indices_etl.py
- venv/bin/python -m pytest tests/test_scheduler_alerts.py

Frontend:
- cd frontend
- npm run build

## 9) Plantilla corta para pedir trabajo al otro asistente

Mensaje sugerido:
"Toma la tarea X. Limita cambios a [archivos/modulo]. No toques Y. Ejecuta [tests]. Devuelve handoff con resumen, archivos tocados y riesgos."