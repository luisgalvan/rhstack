# Changelog

## v0.2.0: rhstack ya no depende solo de Claude Code

- **Nuevo: `comms-clarity`**, un Editor de Claridad que reescribe un memo, anuncio de política o
  correo de ciclo de mérito para que alguien ocupado entienda en segundos qué cambió y qué tiene
  que hacer — sin tocar cifras, fechas ni compromisos del original.
- **rhstack ya no depende solo de Claude Code.** Ahora se instala igual de directo en
  **Antigravity CLI** (sucesora de Gemini CLI) y en **Codex**; Cursor, Qwen Code y Kimi lo leen
  vía integración declarativa.
- **Los análisis numéricos (`comp-bands`, `pay-equity-audit`, `merit-cycle`, `offer-builder`,
  `survey-analysis`) ahora requieren Python 3.11+ instalado en tu computadora.** Instalar Python es un solo
  comando (`winget install Python.Python.3.12`) y solo hace falta una vez.
- **Nueva página pública**: [rhstack.uk](https://rhstack.uk)

## v0.1.0.0: Lanzamiento inicial de rhstack

Tu equipo virtual de People acaba de volverse mucho más capaz.

- **Todo especialista ahora sigue el mismo flujo de docs generados que el resto de rhstack**:
  edita la plantilla de una skill, regenera, y el SKILL.md que invocas con `/skill-name` siempre
  está sincronizado con lo que está en el repositorio.
- **Nuevo: un ciclo completo de revisión y lanzamiento para el trabajo de People.**
  `plan-cfo-review` y `plan-legal-review` dan a tus propuestas de compensación una aprobación de
  presupuesto y cumplimiento antes de salir; `auto-people-review` corre ambas más un borrador de
  comunicación en una sola pasada; `cycle-ship` cierra un ciclo con un incremento de versión y una
  entrada estilo CHANGELOG.
- **Nuevo: `market-drift-check`** compara las bandas y resultados de este ciclo contra los del
  ciclo anterior y señala regresiones antes de que las presentes.
- **Nuevo: `rollout-watch` y `publish-and-monitor`** te dan un ciclo de monitoreo post-lanzamiento
  después de que sale un cambio de compensación o política: observa señales de rotación y
  engagement en lugar de enterarte tres meses después de que algo se rompió.
- **Nuevo: `people-investigate`** para depuración sistemática de causa raíz de un problema de
  People que es más profundo de lo que una sola sesión de office-hours puede resolver, y
  **`people-retro`** para cerrar el ciclo después de que termina.
- **Nuevo: `compliance-audit`** recorre un checklist de transparencia salarial y derecho laboral
  entre jurisdicciones (y siempre te dice cuándo llamar a un abogado en lugar de adivinar).
- **Nuevo: `total-rewards-design`** construye una filosofía de Total Rewards desde cero para
  empresas que todavía no tienen una.
- **Nuevo: `hris-connect`**: un paso de configuración de una sola vez para que rhstack aprenda el
  formato de exportación de tu HRIS/nómina una vez, en lugar de preguntar cada vez.
- **Nuevo: `policy-qa` y `plan-policy-review`** te dan una segunda mirada de solo-informe sobre
  una política o plan antes de que salga, sin que rhstack haga cambios en tu nombre.

### Para contribuyentes

- Se agregó toda la maquinaria de ingeniería del proyecto: scripts de `package.json`, un
  pipeline de generación plantilla → SKILL.md (`scripts/gen-skill-docs.ts`), un dashboard de
  salud de skills (`scripts/skill-check.ts`), una suite de pruebas por niveles (validación
  estática gratuita, LLM-judge pagado, E2E pagado), selección de pruebas basada en diff, y
  workflows de CI (`skill-docs.yml`, `evals.yml`, `actionlint.yml`).
