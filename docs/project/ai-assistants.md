# Continuar CumpleIA con otra plataforma de IA

## Qué se transfiere automáticamente

- código fuente;
- Git history;
- tests;
- migraciones;
- CI;
- README/documentación;
- ADRs;
- archivos de configuración sin secretos.

## Qué no se transfiere automáticamente

- conversaciones históricas con Claude;
- memorias internas de Claude Code;
- decisiones que nunca se documentaron;
- contexto de tareas que quedó solo en prompts o chats.

## Estrategia recomendada

1. Mantener `AGENTS.md` neutral en la raíz.
2. Mantener `docs/PROJECT_STATUS.md` breve y vigente.
3. Mantener ADRs para decisiones duraderas.
4. Archivar notas fechadas.
5. Permitir archivos específicos por herramienta (`CLAUDE.md`, etc.) solo como capas delgadas que remitan a las fuentes neutrales.

## Prompt de arranque para cualquier agente

> Lee `AGENTS.md`, `docs/PROJECT_STATUS.md`, `docs/ARCHITECTURE_CURRENT.md`, los ADR vigentes y `docs/BACKLOG.md`. Después inspecciona `git status`, `git log` y las migraciones actuales. No asumas que una nota histórica describe el estado vivo. Antes de modificar código, ejecuta o verifica los checks definidos en `AGENTS.md`.
