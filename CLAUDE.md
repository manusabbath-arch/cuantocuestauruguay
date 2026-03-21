# Claude Entry Point

Fuente canónica de contexto del proyecto:
- .github/PROJECT_CONTEXT.md

Documentos secundarios:
- ROADMAP.md para prioridades
- README.md para overview

Orden de confianza:
1. código real
2. .github/PROJECT_CONTEXT.md
3. ROADMAP.md
4. resto de documentación

Reglas:
- No mantener contexto duplicado en varios archivos.
- Actualizar .github/PROJECT_CONTEXT.md cuando cambien ETLs, scheduler, endpoints, comandos o estructura real.
- No asumir que ARCH-002 está implementado sólo por existir reportes.
