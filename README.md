# rhstack

**Convierte tu CLI de IA en tu equipo completo de RR. HH.**

- **Hoy:** Compensación y Beneficios, 26 especialistas listos para usar.
- **En construcción:** Gestión de Talento, Desarrollo Organizacional, Clima y Cultura, Comunicación Interna.

rhstack es un paquete de código abierto de [skills de Claude Code](https://docs.claude.com/en/docs/claude-code) con opinión formada para trabajo de RR. HH. Cada skill es un especialista con su propia metodología (un CHRO, un Analista de Compensación, un Auditor de Equidad Salarial, un Especialista en Beneficios) que invocas como un slash command dentro de Claude Code. La misma disciplina aplica a todos los dominios: los análisis numéricos los ejecutan scripts locales determinísticos y auditables, el LLM solo orquesta e interpreta, la metodología siempre se cita y nunca se fabrican datos.

El dominio de Compensación y Beneficios ya está construido y es el que puedes usar hoy. Los otros cuatro están en el roadmap ([TODOS.md](TODOS.md)): se comunican aquí porque son la visión completa del proyecto, no porque ya existan.

> **¿No tienes trasfondo técnico?** Lee la [Guía rápida para RH](GUIA-RAPIDA.md): no asume que
> sabes programar ni usar una terminal.



## El equipo virtual de People



### Comp & Ben (disponible hoy)

Especialistas principales, el trabajo de análisis del día a día:


| Comando                 | Especialista                     | Qué hace                                                                                                                                                                                                                                             |
| ----------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/front-desk`           | Recepción de rhstack             | No sabes qué comando usar? Empieza aquí: describe tu problema en lenguaje cotidiano y te enruta al especialista correcto (o a `people-office-hours` si el problema todavía no está claro). No hace falta memorizar ningún otro nombre de esta tabla. |
| `/people-office-hours`  | CHRO                             | Punto de entrada. Interroga el problema real (¿rotación? ¿equidad interna? ¿presupuesto?) antes de que nadie proponga una solución. Produce un informe diagnóstico que consumen las demás skills.                                                    |
| `/job-architecture`     | Job Architect                    | Diseña familias de puestos, niveles y escalas de carrera. Señala títulos inflados y niveles duplicados.                                                                                                                                              |
| `/comp-bands`           | Analista de Compensación         | Construye bandas salariales por nivel y geografía, calcula compa-ratios y penetración de rango, señala compresión y valores atípicos.                                                                                                                |
| `/pay-equity-audit`     | Auditor de Equidad Salarial      | Analiza brechas salariales por género u otros grupos, controlado por nivel y función. Produce un informe con metodología documentada.                                                                                                                |
| `/merit-cycle`          | Comp Ops                         | Modela el ciclo de revisión: matrices de mérito (desempeño × posición en banda), simulación de escenarios de presupuesto, y deriva el presupuesto desde datos de mercado si se le pide.                                                              |
| `/survey-analysis`      | Analista de Encuestas de Mercado | Ajusta modelos de mercado (lineal, exponencial, power, maturity curve) a datos de encuesta y compara pago de empleados contra el modelo o contra medianas de encuesta directas.                                                                      |
| `/offer-builder`        | Recruiting Comp Partner          | Estructura ofertas: base, variable, equity (con proyección de vesting por interés compuesto), verificadas contra la banda y pares internos.                                                                                                          |
| `/benefits-review`      | Especialista en Beneficios       | Audita el paquete de beneficios contra la práctica de mercado, calcula costo por empleado, propone quick wins.                                                                                                                                       |
| `/jd-writer`            | Talent Partner                   | Redacta descripciones de puesto consistentes con la arquitectura de puestos y las bandas de compensación.                                                                                                                                            |
| `/total-rewards-design` | Total Rewards Consultant         | Diseña una filosofía de Total Rewards (posicionamiento de mercado, pay-mix) desde cero.                                                                                                                                                              |


Revisión, lanzamiento y monitoreo: el proceso alrededor de un ciclo, un pipeline de ship/review aplicado a trabajo de People. Esta capa ya es agnóstica al dominio por diseño: revisa *cualquier* plan de People, no solo los de compensación, así que servirá igual a los dominios que vienen.


| Comando                | Especialista                | Qué hace                                                                                                                                                                                                        |
| ---------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/plan-review`         | Peer Reviewer               | Revisión de consistencia interna de cualquier plan antes de que vaya a Finanzas/Legal.                                                                                                                          |
| `/plan-cfo-review`     | Finance Partner             | Aprobación de presupuesto/P&L sobre una propuesta de compensación.                                                                                                                                              |
| `/plan-legal-review`   | Employment Counsel Partner  | Checklist de cumplimiento/exposición; nunca falla sobre temas legales, deriva las preguntas a asesoría legal.                                                                                                   |
| `/auto-people-review`  | Pipeline Orchestrator       | Ejecuta plan-review → CFO review → Legal review en una sola pasada.                                                                                                                                             |
| `/cycle-ship`          | Release Manager             | Incrementa versión y finaliza un ciclo, redacta la comunicación.                                                                                                                                                |
| `/publish-and-monitor` | Release Captain             | Envía la comunicación e inicia `rollout-watch` en un solo movimiento.                                                                                                                                           |
| `/rollout-watch`       | Post-Launch Analyst         | Monitorea señales de rotación/engagement después de que se lanza un cambio.                                                                                                                                     |
| `/market-drift-check`  | Analista de Compensación    | Compara los números de este ciclo contra los del ciclo anterior, señala regresiones.                                                                                                                            |
| `/people-investigate`  | Root-Cause Analyst          | Prueba sistemáticamente hipótesis de causa raíz contra los datos.                                                                                                                                               |
| `/people-retro`        | Cycle Facilitator           | Retrospectiva de un ciclo completado.                                                                                                                                                                           |
| `/document-cycle`      | Total Rewards Writer        | Actualiza documentos vivos (filosofía, FAQ) después de que se lanza un ciclo.                                                                                                                                   |
| `/compliance-audit`    | Jurisdictional Auditor      | Checklist estructurado de transparencia salarial + derecho laboral entre jurisdicciones.                                                                                                                        |
| `/second-opinion`      | Independent Cross-Check     | Verifica la cordura de un análisis mediante una segunda CLI de IA independiente.                                                                                                                                |
| `/hris-connect`        | Configuración única         | Le enseña a rhstack el formato de exportación del HRIS de esta empresa, una sola vez.                                                                                                                           |
| `/policy-qa`           | Report-Only Reviewer        | Pasada de QA sobre un único documento de política, solo hallazgos, sin correcciones.                                                                                                                            |
| `/plan-policy-review`  | Execution-Readiness Auditor | Auditoría de solo-informe de un plan de People de varios pasos antes de su ejecución.                                                                                                                           |
| `/comms-clarity`       | Editor de Claridad          | Reescribe un borrador de comunicación de People (memo, anuncio, correo de ciclo) para que la acción y la fecha límite se entiendan en segundos, sin cambiar cifras, fechas ni compromisos legales del original. |




### Próximos dominios (en construcción)

Aún no hay comandos que instalar para estos: son la dirección del proyecto, no funcionalidad
disponible. El orden de construcción y los especialistas propuestos de cada uno están en
[TODOS.md](TODOS.md):

1. **Gestión de Talento**: reclutamiento, calibración de desempeño, sucesión, onboarding.
2. **Desarrollo Organizacional**: diseño organizacional, brechas de habilidades, gestión del cambio.
3. **Clima y Cultura**: encuestas de clima, engagement, coherencia cultural.
4. **Comunicación Interna**: cascada de comunicación, planes de comunicación de cambio.



## El ciclo

Como un sprint, pero para Total Rewards. Cada skill lee los artefactos de la anterior:

```
Diagnosticar → Diseñar arquitectura → Bandear → Auditar → Simular → Revisar → Lanzar → Monitorear
(office-hours) (job-architecture) (comp-bands) (pay-equity-audit) (merit-cycle) (auto-people-review) (cycle-ship) (rollout-watch)
```

También puedes invocar cualquier skill de forma independiente.

## Instalación

**Para usar rhstack (recomendado):** instálalo como plugin de Claude Code, sin clonar nada ni tocar una terminal. Dentro de Claude Code:

```
/plugin marketplace add luisgalvan/rhstack
/plugin install rhstack@luisgalvan
```

Los comandos quedan disponibles con el prefijo del plugin (`/rhstack:comp-bands`,
`/rhstack:people-office-hours`, etc., evita choques con otros plugins que tengas instalados). Los
scripts de análisis (`comp-bands`, `pay-equity-audit`, `merit-cycle`, `offer-builder`,
`survey-analysis`) requieren Python 3.11+ instalado en tu máquina — si no lo tienes, corre una
sola vez `winget install Python.Python.3.12` (Windows) o el instalador equivalente de tu
plataforma. Actualiza con `/plugin marketplace update` cuando salga una versión nueva.

**Para contribuir o modificar una skill:** clona el repo (necesitas [Bun](https://bun.sh) y
Python 3.11+ además de [Claude Code](https://docs.claude.com/en/docs/claude-code)):

```bash
git clone https://github.com/luisgalvan/rhstack.git
cd rhstack
./setup
```

`setup` enlaza (symlink) cada skill dentro de `~/.claude/skills/` para desarrollo local sin
prefijo de plugin. Reinicia Claude Code y los comandos quedarán disponibles.

**Con otros agentes de IA:** rhstack está pensado como un paquete de skills en texto plano, no
solo como plugin de Claude Code: el contenido ya se prueba corriendo contra un modelo Gemini vía
Antigravity CLI (`bun run test:e2e:gemini`). Clona el repo y, según tu agente:


| Agente                  | Cómo se entera de rhstack                                                                                                               |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Antigravity CLI (`agy`) | Lee `AGENTS.md` directamente desde la raíz del repo clonado, sin manifiesto aparte (sucesora de Gemini CLI, retirada en junio de 2026). |
| Codex, OpenCode         | Leen `.codex-plugin/plugin.json` / `opencode.json`, que apuntan directo a `skills/`.                                                    |
| Cursor                  | Lee `.cursor/skills/<nombre>/SKILL.md` (un espejo plano, generado, de cada skill).                                                      |
| Qwen Code, Kimi         | `qwen-extension.json` / `kimi.plugin.json`, mismo patrón, sin verificar (ver CONTRIBUTING.md).                                          |
| Cualquier otro          | Apúntalo a [AGENTS.md](AGENTS.md), la guía de entrada agnóstica de plataforma.                                                          |


Sin importar el agente, los scripts de análisis (`skills/<dominio>/<skill>/scripts/*.py`) corren
como proceso del sistema operativo: necesitan Python 3.11+ instalado en la máquina, sin excepción
por CLI de IA usado.

## Pruébalo con datos sintéticos

La carpeta `examples/` contiene un dataset de empleados totalmente sintético (`sample_employees.csv`, 60 filas). Sin personas reales, sin salarios reales. Prueba:

```
/comp-bands analiza examples/sample_employees.csv y propone bandas para la familia de Ingeniería
```



## Demo: auditoría de equidad salarial en un comando

Esto es un fragmento real de `/pay-equity-audit` ejecutado sobre `examples/sample_employees.csv` (60 empleados sintéticos):

> **Brecha mediana no ajustada: 7.2%** en favor del grupo masculino (mediana M €69.000 vs F €64.000).
>
> **Brechas ajustadas dentro de nivel** (trabajo de igual valor):
>
> - L3 (n=19): **−2.2%** a favor de las mujeres
> - L4 (n=17): **+8.0%** a favor de los hombres
> - L5 (n=12): **−6.6%** a favor de las mujeres
> - L2 y L6: excluidas por tamaño de muestra insuficiente (n < 5)
>
> **Hallazgo estructural:** la representación es ~50/50 de L2 a L5, pero cae a 25% en L6: la brecha global la impulsa la *representación*, no el pago por igual trabajo.

El informe completo incluye metodología documentada (controles aplicados, celdas excluidas y por qué), lo que se vuelve evidencia defendible bajo regímenes de transparencia salarial. Ver `output/pay-equity-report.md` tras ejecutarlo tú mismo.

## Demo: claridad de comunicación en un comando

`comms-clarity` aplica los mismos principios de reducción de carga cognitiva bajo presión de
tiempo y atención que usa el movimiento de *lenguaje claro* (*plain language*) para comunicación
organizacional, pero al artefacto que un empleado realmente lee, no a la conversación con Claude.
Esto es `/comms-clarity` ejecutado sobre `examples/sample-benefits-memo.md`, un memo sintético de
beneficios cargado de jerga corporativa:

**Antes** (fragmento: el memo completo tiene 5 párrafos, la acción real está enterrada en el
tercero):

> Esperamos que este mensaje les encuentre muy bien. Como parte de nuestro compromiso continuo con
> el bienestar integral de nuestro equipo, y luego de una revisión exhaustiva realizada en
> conjunto con nuestro proveedor de beneficios a lo largo de los últimos meses, nos complace
> compartir que estamos evolucionando nuestra oferta de beneficios [...]
>
> Como parte de este proceso de evolución [...] el beneficio de reembolso de gimnasio [...] será
> descontinuado a partir del 1 de marzo de 2026. [...]

**Después** (`sample-benefits-memo-clear.md`):

> **Qué tienes que hacer:** revisar tu plan de salud para el próximo año antes de que cierre la
> inscripción abierta; si no haces ningún cambio, quedas inscrito automáticamente en tu plan
> actual.
>
> **Qué cambia**
>
> 1. El reembolso de gimnasio ($40/mes) se descontinúa el 1 de marzo de 2026.
> 2. A partir de esa fecha, se agrega telemedicina + una app de mindfulness como reemplazo.
>
> **Próxima acción:** revisa tu plan antes de *[fecha límite de inscripción abierta, el memo
> original no la especifica; confírmala antes de enviar]*.
>
> **Contexto** (opcional): esta actualización viene de la revisión con nuestro proveedor de
> beneficios y del feedback de la última encuesta de clima.

Nota que la reescritura **no inventa** la fecha límite de inscripción abierta que el memo original
nunca especificó: la deja marcada como pregunta pendiente en vez de rellenarla para sonar más
accionable. Esa es la regla no negociable de la skill: reestructura y recorta, nunca fabrica un
hecho que no estaba en el original.

## Demo: encadenar tres skills sobre el mismo dataset

`comp-bands` → `job-architecture` → `jd-writer`, cada una leyendo el artefacto de la anterior, sobre `examples/sample_employees.csv`:

**1.** `/comp-bands` ancla bandas internamente (sin datos de mercado disponibles) y señala compresión:

> **L5**: la mediana de contrataciones nuevas (€109.500) supera en 13.5% a la mediana de empleados tenured (€96.500), señal de inversión salarial.

**2.** `/job-architecture` detecta que "Senior" no significa lo mismo entre familias, y relee esa misma señal de compresión contra los criterios de nivel:

> Senior Software Engineer = L3, pero Senior Product Manager y Senior Account Executive = L4. [...] Vale la pena releer la compresión en L5 contra el criterio de Alcance: confirmar que el personal tenured realmente sostiene "equipo de tamaño medio / mueve métricas org-wide" y no debería estar mapeado a L4.

**3.** `/jd-writer` escribe la JD del rol usando el rango de `comp-bands.csv` y el scope de `job-architecture.md`, y hereda la advertencia de anclaje interno hacia `compliance-audit`:

> ⚠️ Esta banda está anclada internamente, no contra datos de mercado. Antes de publicar esta JD [...] correr `compliance-audit` para confirmar si esa jurisdicción exige que el rango publicado esté además respaldado por datos de mercado.

Ninguna skill repite el trabajo de la anterior: cada una cita explícitamente lo que heredó, incluyendo sus límites metodológicos. Pruébalo tú mismo: `/comp-bands examples/sample_employees.csv`, luego `/job-architecture`, luego `/jd-writer`.

## Datos y privacidad

Los datos de compensación están entre los más sensibles que posee una empresa. Las skills de rhstack instruyen a Claude para que:

- trabaje solo con archivos que tú proporciones explícitamente,
- nunca fabrique cifras de benchmark de mercado (citan fuentes o te piden tus datos de encuesta),
- señale cuándo un dataset es demasiado pequeño para conclusiones estadísticamente significativas.

**Nunca pegues datos reales de empleados en ninguna herramienta sin antes verificar la política de datos de tu empresa.**

## Descargo de responsabilidad

rhstack produce análisis y borradores, no asesoría legal o financiera. Las leyes de equidad salarial, las obligaciones de comités de empresa (works councils) y las normas de transparencia salarial (p. ej., la Directiva de Transparencia Salarial de la UE) varían según la jurisdicción; siempre revisa los resultados con asesoría legal calificada antes de actuar sobre ellos.

## Contribuir

Queremos que esto se convierta en el paquete de skills de RR. HH. de la comunidad. Consulta
[TODOS.md](TODOS.md) para el backlog actual y [CONTRIBUTING.md](CONTRIBUTING.md) para saber cómo
agregar una skill. Se buscan contribuciones en dos frentes:

- **Profundizar Comp & Ben**: ingesta de encuestas de mercado, planeación de fuerza laboral,
cálculo de indemnizaciones, paquetes de contexto laboral localizados.
- **Abrir los cuatro dominios nuevos**: Gestión de Talento, Desarrollo Organizacional, Clima y
Cultura, Comunicación Interna. Cada uno tiene especialistas propuestos con su metodología base en
TODOS.md; una skill nueva ahí vale tanto como una mejora a Comp & Ben.



## Licencia

MIT. Ver [LICENSE](LICENSE).

## Autoría

Creado por [Luis Galvan](https://github.com/luisgalvan). Ver [CONTRIBUTING.md](CONTRIBUTING.md) para sumarte como contribuidor.