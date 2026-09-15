# desarrollo de rhstack

La disciplina de ingeniería de rhstack aplica a los artefactos de comp/People el mismo rigor que ya
es estándar en ingeniería de software: fuente de verdad única, generación en vez de edición manual,
pruebas antes de cada commit, versionado explícito. Ante la duda sobre *por qué* existe una
convención aquí, la respuesta casi siempre es "esa disciplina funciona bien para código, y aplica
igual de bien a artefactos de comp/People." Ver también README.md y ETHOS.md.

## Comandos

```bash
bun install            # instalar dependencias
bun test                # correr pruebas gratuitas (validación de skills + drift de gen-skill-docs, <2s)
bun run test:evals      # correr evals pagados: LLM judge + E2E (basado en diff, ~$4/run máx)
bun run test:evals:all  # correr TODOS los evals pagados sin importar el diff
bun run test:e2e        # correr solo pruebas E2E contra Claude (basado en diff)
bun run test:e2e:all    # correr TODAS las pruebas E2E contra Claude sin importar el diff
bun run test:e2e:gemini      # correr pruebas E2E contra Gemini vía `agy` (basado en diff)
bun run test:e2e:gemini:all  # correr TODAS las pruebas E2E contra Gemini vía `agy`
bun run eval:select     # mostrar qué pruebas correrían según el diff actual
bun run gen:skill-docs  # regenerar los SKILL.md a partir de las plantillas
bun run skill:check     # dashboard de salud para todas las skills
bun run dev:skill       # modo watch: auto-regenera y valida al cambiar
bun run eval:list       # listar todas las corridas de evals desde ~/.rhstack-dev/evals/
bun run eval:compare    # comparar dos corridas de evals (auto-elige la más reciente)
bun run eval:summary    # estadísticas agregadas entre todas las corridas de evals
bun run build           # gen:skill-docs
```

`test:evals` requiere `ANTHROPIC_API_KEY`. Las pruebas E2E lanzan `claude -p "/<skill> ..."`
contra el dataset sintético en `examples/` y verifican que se produzcan los archivos de salida
esperados con la estructura esperada. Los resultados persisten en `~/.rhstack-dev/evals/` con
comparación automática contra la corrida anterior.

**Selección de pruebas basada en diff:** `test:evals` y `test:e2e` seleccionan pruebas
automáticamente según el `git diff` contra la rama base. Cada prueba declara sus dependencias de
archivos en `test/helpers/touchfiles.ts`. Los cambios a touchfiles globales (gen-skill-docs,
skill-parser, llm-judge, session-runner) disparan todas las pruebas. Usa `EVALS_ALL=1` o las
variantes de script `:all` para forzar todas las pruebas. Corre `eval:select` para previsualizar
qué pruebas correrían.

**Backend de las pruebas E2E:** por defecto las pruebas E2E lanzan `claude -p` y requieren
`ANTHROPIC_API_KEY`. Con `RHSTACK_E2E_BACKEND=agy` (usado por `test:e2e:gemini*`) lanzan `agy -p`
contra un modelo Gemini en su lugar: no requieren `ANTHROPIC_API_KEY` a menos que también corra
el eval de tipo `llm-eval` (el juez LLM siempre usa la API de Anthropic). Requiere la CLI `agy`
(Antigravity CLI, sucesora de Gemini CLI) instalada y autenticada. Usa `RHSTACK_E2E_MODEL` para
elegir el modelo (default
`gemini-3.5-flash-high`; ver `agy models` para el resto). Esto valida que las skills, al ser
prompts en lenguaje natural, funcionen igual sobre un modelo distinto de Claude: no cambia el
comportamiento por defecto de `bun test` ni de `test:evals`.

## Pruebas

```bash
bun test              # correr antes de cada commit, gratis, <2s
bun run test:evals    # correr antes de lanzar, pagado, basado en diff (~$4/run máx)
```

`bun test` corre la validación de skills (frontmatter, secciones requeridas, higiene de scripts)
y las verificaciones de drift de gen-skill-docs. `bun run test:evals` corre evals de calidad tipo
LLM-judge y pruebas E2E vía `claude -p`. Ambas deben pasar antes de crear un PR.

## Estructura del proyecto

**Nota sobre `skills/`:** hoy todas las skills existentes pertenecen al dominio de Compensación y
Beneficios, y viven en una lista plana. rhstack apunta a cinco dominios (Comp & Ben, Gestión de
Talento, Desarrollo Organizacional, Clima y Cultura, Comunicación Interna); cuando exista más de
uno, `skills/` se reorganizará por dominio (`comp-ben/`, `talent/`, `org-dev/`, `culture/`,
`comms/`) más una capa `_pipeline/` agnóstica al dominio para las skills de revisión/lanzamiento.
Ver TODOS.md para el detalle y el orden de construcción. No anticipes esa reorganización: el árbol
de abajo es la estructura real de hoy.

```
rhstack/
├── .claude-plugin/          # plugin.json + marketplace.json, instalación vía /plugin install
├── skills/                  # Cada skill especialista (fuente única de verdad: SKILL.md.tmpl)
│   ├── people-office-hours/ # CHRO, punto de entrada diagnóstico
│   ├── job-architecture/    # Job Architect, niveles, escalas
│   ├── comp-bands/          # Analista de Compensación, bandas, compa-ratio
│   │   └── scripts/         # Análisis determinístico (Python 3, solo stdlib)
│   ├── pay-equity-audit/    # Auditor de Equidad Salarial
│   │   └── scripts/
│   ├── merit-cycle/         # Comp Ops, matriz de mérito, simulación de presupuesto
│   │   └── scripts/
│   ├── survey-analysis/     # Analista de Encuestas de Mercado, modelos de mercado, job pricing
│   │   └── scripts/
│   ├── offer-builder/       # Recruiting Comp Partner
│   │   └── scripts/         # Proyección de equity (interés compuesto)
│   ├── benefits-review/     # Especialista en Beneficios
│   ├── jd-writer/           # Talent Partner
│   ├── cycle-ship/          # Finaliza y versiona un artefacto de People para lanzamiento
│   ├── plan-review/         # Revisión de pares de un plan de People antes de lanzarlo
│   ├── plan-cfo-review/     # Aprobación de Finanzas/presupuesto
│   ├── plan-legal-review/   # Aprobación de cumplimiento/legal
│   ├── auto-people-review/  # Pipeline: revisión CFO → revisión Legal → borrador de comunicación
│   ├── market-drift-check/  # Compara este ciclo vs el anterior, señala regresiones
│   ├── rollout-watch/       # Ciclo de monitoreo post-lanzamiento para un cambio de comp/política
│   ├── second-opinion/      # Verificación cruzada de un análisis vía una segunda CLI de IA
│   ├── publish-and-monitor/ # Publica comunicación → inicia rollout-watch
│   ├── people-investigate/  # Depuración sistemática de causa raíz para un problema de People
│   ├── people-retro/        # Retrospectiva de un ciclo completado
│   ├── document-cycle/      # Actualizaciones de docs post-ciclo (doc de filosofía, doc de bandas, FAQ)
│   ├── compliance-audit/    # Checklist jurisdiccional de transparencia salarial + derecho laboral
│   ├── total-rewards-design/# Diseña una filosofía de Total Rewards desde cero
│   ├── hris-connect/        # Configuración única: formato de exportación de HRIS/nómina
│   ├── policy-qa/           # Pasada de QA de solo-informe sobre un doc de política
│   └── plan-policy-review/  # Auditoría de solo-informe de un plan de People antes de ejecutarlo
├── scripts/                  # Herramientas de build + DX
│   ├── gen-skill-docs.ts     # Generador de plantilla → SKILL.md
│   ├── skill-check.ts        # Dashboard de salud
│   ├── dev-skill.ts          # Modo watch
│   ├── eval-select.ts        # Previsualización de selección de pruebas basada en diff
│   ├── eval-list.ts          # Listar corridas de evals persistidas
│   ├── eval-compare.ts       # Comparar dos corridas de evals
│   └── eval-summary.ts       # Estadísticas agregadas entre corridas de evals
├── test/                     # Validación de skills + pruebas de evals
│   ├── helpers/               # skill-parser.ts, touchfiles.ts, session-runner.ts, llm-judge.ts, eval-store.ts
│   ├── fixtures/               # JSON de verdad de referencia, baselines de evals (nunca datos reales de empleados)
│   ├── skill-validation.test.ts  # Nivel 1: validación estática (gratis, <1s), coincide con el glob por defecto de `bun test`
│   ├── gen-skill-docs.test.ts    # Nivel 1: verificación de drift plantilla/salida (gratis, <1s), mismo glob
│   ├── skill-llm-eval.eval.ts    # Nivel 3: LLM-as-judge (~$0.15/run), `.eval.ts` para que el `bun test` normal lo omita
│   └── skill-e2e-*.eval.ts       # Nivel 2: E2E vía claude -p (pagado, dividido por grupo de skills), mismo glob
├── bin/                       # Utilidades de CLI (rhstack-config, rhstack-slug)
├── examples/                  # Dataset sintético de empleados, sin datos reales, nunca
├── .github/                   # Workflows de CI + imagen Docker
│   ├── workflows/              # skill-docs.yml, evals.yml, actionlint.yml
│   └── docker/                 # Dockerfile.ci (Bun + Python3, sin navegador necesario)
├── setup                     # Configuración de una sola vez: symlink de skills a ~/.claude/skills/
├── ETHOS.md                  # Filosofía de construcción para trabajo de RR. HH.
├── TODOS.md                  # Backlog de skills
├── CHANGELOG.md / VERSION    # Notas de lanzamiento por rama
└── package.json               # Scripts de build
```

## Flujo de trabajo de SKILL.md

Los archivos SKILL.md se **generan** a partir de plantillas `.tmpl`. Para actualizar una skill:

1. Edita el archivo `.tmpl` (p. ej. `skills/comp-bands/SKILL.md.tmpl`)
2. Corre `bun run gen:skill-docs` (o `bun run build`, que lo hace automáticamente)
3. Haz commit tanto del `.tmpl` como del archivo `.md` generado

Para agregar una skill nueva: crea `skills/<name>/SKILL.md.tmpl` con frontmatter (`name`,
`description`) siguiendo el estilo de la casa en CONTRIBUTING.md, luego corre `gen-skill-docs`.

**Conflictos de merge en archivos SKILL.md:** NUNCA resuelvas conflictos en archivos SKILL.md
generados aceptando cualquiera de los dos lados. En su lugar: (1) resuelve los conflictos en las
plantillas `.tmpl`, (2) corre `bun run gen:skill-docs` para regenerar, (3) agrega al staging los
archivos regenerados. Aceptar la salida generada de un solo lado descarta silenciosamente los
cambios de plantilla del otro lado.

## Distribución como plugin de Claude Code

rhstack se distribuye a usuarios finales como **plugin de Claude Code**, no como un repo para
clonar: `.claude-plugin/plugin.json` y `.claude-plugin/marketplace.json` en la raíz del repo son
lo que hace que `/plugin marketplace add luisgalvan/rhstack` + `/plugin install rhstack@luisgalvan`
funcione sin que nadie clone nada ni corra `./setup`. El repo completo sigue siendo público (así
es como se hospeda el marketplace), pero el HR funcional nunca navega el repo: solo instala el
plugin desde dentro de Claude Code y usa los comandos con prefijo (`/rhstack:comp-bands`).

`./setup` (symlink manual a `~/.claude/skills/`, sin prefijo de plugin) sigue existiendo para
desarrollo local: así se prueba una skill antes de publicarla, sin depender de que el
marketplace ya tenga la versión nueva.

**Scripts Python:** cada script en `skills/<dominio>/<skill>/scripts/*.py` requiere Python 3.11+
instalado en la máquina del usuario final, sin importar qué CLI de IA orquesta la skill (Claude
Code, Codex, Antigravity, Cursor…) — el script corre como proceso del sistema operativo, no dentro del
CLI. Cada `SKILL.md.tmpl` que invoca un script debe indicar, si el comando falla por Python
ausente, que el usuario corra una sola vez `winget install Python.Python.3.12` (Windows) o la
instalación equivalente de su plataforma. rhstack **no distribuye binarios compilados**: un
binario sin firma de código dispara advertencias de SmartScreen que confunden exactamente a la
audiencia no técnica que esto busca servir, y compilarlo en una máquina de desarrollo introduce
drift frente al entorno del usuario final que un `.py` interpretado no tiene.

## Diseño agnóstico de plataforma

Las skills NUNCA deben hardcodear la jurisdicción, moneda, formato de HRIS o estructura
organizacional de una empresa. En su lugar:

1. **Leer CLAUDE.md** para la configuración específica del proyecto (la jurisdicción de la sede de
   esta empresa, moneda, año fiscal, formato de exportación de HRIS, configurado una vez vía
   `hris-connect`)
2. **Si falta, usar AskUserQuestion**: dejar que el usuario lo indique, o pedirle que apunte al
   archivo/dataset fuente
3. **Persistir la respuesta en CLAUDE.md** para que rhstack nunca tenga que volver a preguntar

Esto aplica a la lógica legal dependiente de jurisdicción, moneda, fuentes de datos de benchmark, y
cualquier otro comportamiento específico de la empresa. La empresa es dueña de su configuración,
rhstack la lee.

## Escribir plantillas de SKILL

Los archivos SKILL.md.tmpl son **prompts que lee Claude**, no scripts. Reglas:

- **Usa lenguaje natural para lógica y estado.** No inventes una máquina de estados para pasar
  datos entre skills: dile a Claude qué artefacto leer (p. ej. "lee `comp-bands.csv` si existe")
  y referéncialo en prosa.
- **No hardcodees una jurisdicción, moneda o régimen legal.** Las obligaciones estatutarias
  (transparencia salarial, comités de empresa, tributación de beneficios) varían según el país.
  Expresa la lógica dependiente de jurisdicción como pasos de decisión numerados explícitos ("1.
  Si la jurisdicción requiere rangos publicados, haz X. 2. De lo contrario, pregunta si publicar
  de todos modos.") y siempre recomienda asesoría legal local calificada para cualquier cosa
  estatutaria: nunca falles tú mismo sobre derecho laboral.
- **Mantén cada skill autocontenida.** Si una skill necesita un artefacto de otra skill, indica la
  entrega explícitamente en prosa ("si `job-architecture.md` no existe, recomienda correr
  `job-architecture` primero") en lugar de asumir un orden de ejecución fijo.
- **Nunca fabriques datos de mercado.** Toda skill que toque compensación debe citar la fuente de
  cualquier número de mercado o atribuirlo explícitamente a datos que el usuario proporcionó: esta
  es una regla no negociable de CONTRIBUTING.md, no una preferencia de estilo.

## Datos y privacidad

Los datos de compensación y de People están entre los más sensibles que posee una empresa. Las
skills de rhstack deben:

- trabajar solo con archivos que el usuario proporcione explícitamente en la sesión,
- nunca fabricar cifras de benchmark de mercado (citar fuentes o pedir datos de encuesta),
- señalar cuándo un dataset es demasiado pequeño (n<5 por grupo) para conclusiones
  estadísticamente significativas.

**Nunca hacer commit de datos reales de empleados en ningún lugar de este repositorio**, ni en
`examples/`, ni en `test/fixtures/`, ni en baselines de evals. Todo dataset aquí debe ser
sintético. Un PR que contenga algo que parezca un nombre real, un salario real, o un ID de empleado
real se cierra, sin excepciones.

## Estilo de commits

**Siempre bisecta los commits.** Cada commit debe ser un único cambio lógico. Cuando hayas hecho
múltiples cambios (p. ej., un rename + una reescritura + pruebas nuevas), sepáralos en commits
distintos antes de hacer push. Cada commit debe ser entendible y reversible de forma independiente.

Ejemplos de buena bisección:
- Rename/mover separado de cambios de comportamiento
- Infraestructura de pruebas (touchfiles, helpers) separada de implementaciones de pruebas
- Cambios de plantilla separados de la regeneración de archivos generados
- Refactors mecánicos separados de skills nuevas

Cuando el usuario diga "bisect commit" o "bisecta y haz push," divide los cambios en staging/sin
staging en commits lógicos y haz push.

## Estilo de CHANGELOG + VERSION

**VERSION y CHANGELOG están acotados por rama.** Cada feature branch que se lanza obtiene su
propio incremento de versión y entrada de CHANGELOG. La entrada describe lo que ESTA rama agrega,
no lo que ya estaba en main.

**Cuándo escribir la entrada de CHANGELOG:**
- Al momento de `cycle-ship`, no durante el desarrollo ni a mitad de rama.
- La entrada cubre TODOS los commits de esta rama contra la rama base.
- Nunca mezcles trabajo nuevo en una entrada de CHANGELOG existente de una versión anterior que
  ya llegó a main. Incrementa la versión y crea una entrada nueva en lugar de editar una ya
  lanzada.

CHANGELOG.md es **para el equipo de People que usa rhstack**, no para contribuyentes. Escríbelo
como notas de lanzamiento de un producto:

- Empieza con lo que el usuario ahora puede **hacer** que antes no podía. Vende la skill.
- Usa lenguaje llano, no detalles de implementación. "Ahora puedes modelar un ciclo de mérito
  completo con escenarios de presupuesto..." no "Se refactorizó el simulador de mérito."
- **Nunca menciones TODOS.md, infraestructura de pruebas interna, ni detalles orientados a
  contribuyentes.** Estos son invisibles para los equipos de People y no significan nada para
  ellos.
- Pon los cambios de contribuyentes/internos en una sección separada "Para contribuyentes" al
  final.
- Sin jerga: di "las auditorías de equidad salarial ahora señalan cuando un grupo tiene muy pocas
  personas para sacar conclusiones" no "se agregó guardia de n<5 a pay_equity.py."

## Compresión de esfuerzo por IA

Al estimar o discutir esfuerzo, siempre muestra tanto el tiempo del equipo humano como el de
rhstack:

| Tipo de tarea | Equipo humano de People | rhstack | Compresión |
|-----------|-------------------|---------|--------------|
| Construir banda salarial (una familia de puestos) | 3-5 días | 20 min | ~150x |
| Auditoría de equidad salarial (un dataset) | 1-2 semanas | 30 min | ~250x |
| Simulación de presupuesto de ciclo de mérito | 3 días | 20 min | ~100x |
| Descripción de puesto (nivelada, sin sesgos) | 3 horas | 10 min | ~15x |
| Auditoría de paquete de beneficios | 1 semana | 45 min | ~60x |
| Diseño de arquitectura de puestos | 2-3 semanas | 3 horas | ~40x |
| Diseño de filosofía de Total Rewards | 1 mes | 1 día | ~20x |

La completitud es barata. No recomiendes atajos (p. ej., "solo calcula a ojo los valores
atípicos") cuando el análisis completo es un "lago" (alcanzable en una sesión) y no un "océano"
(necesita un contrato con un proveedor de encuestas o una migración de HRIS de varios trimestres).
Ver ETHOS.md para la filosofía completa.

## Buscar antes de construir

Antes de diseñar cualquier skill o método de análisis nuevo:

1. Busca si ya existe una metodología de RR. HH./comp que resuelva esto (compa-ratio, penetración
   de rango, nivelación de puestos estilo Mercer/Radford, modelos de equidad salarial basados en
   regresión), no inventes un método estadístico novedoso cuando ya existe uno estándar y
   defendible ante auditoría.
2. Verifica si ya existe una skill adyacente que produzca el artefacto que necesitas (p. ej., no
   reconstruyas la lógica de bandas dentro de `pay-equity-audit`, lee `comp-bands.csv`).
3. Revisa CLAUDE.md y TODOS.md antes de proponer una skill nueva: puede que ya esté planeada o
   explícitamente fuera de alcance.

Tres capas de conocimiento: metodología de RR. HH./comp probada y verdadera (Capa 1), práctica
emergente como directivas de transparencia salarial y nivelación basada en habilidades (Capa 2),
razonamiento desde primeros principios sobre los datos específicos de esta empresa (Capa 3). Da
prioridad a la Capa 3 solo después de descartar la 1 y la 2: las audiencias de comp y legal
confían mucho más en una metodología estándar que en una novedosa. Ver ETHOS.md.
