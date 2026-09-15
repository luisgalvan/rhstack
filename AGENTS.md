# AGENTS.md

Guía de entrada para cualquier agente de IA que trabaje en este repositorio: Claude Code,
Antigravity CLI, Codex, Cursor, Qwen Code, Kimi, OpenCode, u otro. Si tu agente ya lee
`CLAUDE.md` directamente, ese archivo sigue siendo la memoria de proyecto canónica; este archivo
es la versión agnóstica de plataforma del mismo contexto, para agentes que no lo cargan por
defecto — incluido Antigravity CLI (`agy`), que lee este mismo archivo directo desde la raíz.

## Qué es rhstack

Un paquete de skills de Recursos Humanos: cada skill es un prompt en lenguaje natural
(`skills/<dominio>/<skill>/SKILL.md`) que hace que el agente actúe como un especialista de
People concreto (Analista de Compensación, Auditor de Equidad Salarial, Job Architect, etc.).
Ver [README.md](README.md) para la tabla completa de especialistas y qué problema resuelve cada
uno, y [ETHOS.md](ETHOS.md) para la filosofía de construcción.

## Cómo se descubre una skill

Cada agente tiene su propio mecanismo de carga; no asumas que el tuyo funciona como Claude Code:

- **Claude Code:** plugin instalado vía `/plugin install rhstack@luisgalvan` (ver
  `.claude-plugin/plugin.json`), o symlinks locales vía `./setup` en modo desarrollo.
- **Antigravity CLI (`agy`):** lee `AGENTS.md` directamente desde la raíz del repo clonado, sin
  manifiesto ni archivo de contexto aparte (sucesora de Gemini CLI, retirada en junio de 2026).
- **Codex, OpenCode:** manifiestos declarativos en `.codex-plugin/plugin.json` y
  `opencode.json` que apuntan directamente a la carpeta `skills/`; no hay copias.
- **Cursor:** `.cursor/skills/<nombre-de-skill>/SKILL.md`: Cursor espera un directorio plano
  (sin subcarpetas de dominio), así que estos son un espejo generado de
  `skills/<dominio>/<skill>/SKILL.md`, no una segunda fuente de verdad.
- **Qwen Code, Kimi:** `qwen-extension.json`, `kimi.plugin.json`: mismo patrón declarativo.
  No verificados contra esas CLIs reales (no disponibles en este entorno de desarrollo); trátalos
  como mejor esfuerzo hasta que alguien los confirme.

Ninguna skill debe asumir que el runtime es Claude Code como único camino posible. Todos los
scripts de análisis se invocan como `python skills/<dominio>/<skill>/scripts/<script>.py`, sin
binario compilado ni rama especial por CLI de IA: funciona igual en Claude Code, Antigravity CLI,
Codex y Cursor, siempre que la máquina tenga Python 3.11+ instalado.

## Fuente de verdad y generación

- El contenido de cada skill se edita en `SKILL.md.tmpl`; `SKILL.md` (y su espejo de Cursor) se
  **generan**: nunca los edites a mano. Corre `bun run gen:skill-docs` después de tocar una
  plantilla.
- `AGENTS.md` no tiene espejo propio: es un archivo de raíz que cada agente (Antigravity CLI
  incluido) lee directo.

## Antes de cambiar código

- `bun test`: validación gratuita de skills + drift de todo lo generado (SKILL.md, espejo de
  Cursor). Debe pasar antes de cualquier commit.
- `bun run test:evals`: evals pagados (LLM-judge + E2E contra Claude). Requiere
  `ANTHROPIC_API_KEY`.
- `bun run test:e2e:gemini`: las mismas pruebas E2E, corridas contra un modelo Gemini vía `agy`
  (Antigravity CLI); es la prueba de que el contenido de las skills es portable más allá de
  Claude, no solo que el manifiesto existe.

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para el flujo completo de agregar o modificar una skill.
