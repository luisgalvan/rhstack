# backlog y roadmap de rhstack

rhstack apunta a cubrir cinco dominios de RR. HH. Hoy solo uno está construido: **Compensación y
Beneficios**. Los otros cuatro (Gestión de Talento, Desarrollo Organizacional, Clima y Cultura,
Comunicación Interna) están en roadmap y no tienen ninguna skill todavía.

Este documento tiene dos partes: el **backlog de Comp & Ben** (lo que falta en el dominio maduro) y
el **roadmap de nuevos dominios** (lo que aún no existe). El roadmap comunica orden, no plazos: no
hay fechas de entrega comprometidas para ninguna skill nueva.

Abre un issue antes de empezar trabajo grande para que podamos alinear el alcance (ver
CONTRIBUTING.md).

---

# Backlog de Comp & Ben

## Construido recientemente

- `survey-analysis`: **construida.** Ajusta modelos de mercado (lineal, exponencial, power,
  y una aproximación cúbica a maturity curve) a datos de encuesta y compara pago de empleados
  contra el modelo o contra medianas de encuesta directas (Job Pricing Market Model: Group of
  Jobs). Metodología: los cinco métodos estándar de análisis de encuestas de compensación.
  `merit-cycle` ganó `market_budget.py` (fórmula de presupuesto de incremento basado en mercado)
  para consumir su salida. `pay-equity-audit` ganó un análisis de regresión lineal múltiple
  opcional (`--regression`) además de la comparación por nivel existente, y detección de
  Paradoja de Simpson. `comp-bands` ganó desviación estándar, coeficiente de variación, P90/P10,
  percentil interno por empleado y forma de distribución. `offer-builder` ganó proyección de
  vesting de equity con interés compuesto.

## Skills deseadas

- `workforce-planning`: planeación de headcount + presupuesto ligada a los niveles de
  `job-architecture`.
- `severance-calculator`: estimación de indemnización sensible a la jurisdicción (delega la
  interpretación legal a asesoría, solo calcula la aritmética una vez confirmada la fórmula).
- `hris-migration`: versión más profunda de `hris-connect`: asistente de mapeo de campos para
  migrar entre plataformas de HRIS.
- Variantes localizadas de skills existentes adaptando el *contexto legal*, no solo el idioma:
  `pay-equity-audit-es`, `comp-bands-de`, `benefits-review-fr`, paquetes de contexto laboral
  LATAM.

## Infraestructura deseada

- Expansión de macros en `gen-skill-docs.ts` (actualmente passthrough 1:1 de plantilla): p. ej.,
  un fragmento compartido de "humildad legal" incluido por referencia en cada skill que toca
  temas estatutarios, de modo que el texto solo necesite cambiar en un lugar.
- Política de retención de `eval-store.ts` (actualmente crecimiento sin límite bajo
  `~/.rhstack-dev/evals/`).
- Nivel de evals pagados protegido por clave de CI (`evals.yml` actualmente omite
  `test:evals` cuando `ANTHROPIC_API_KEY` no está configurada; necesita una clave real
  configuradoconfigurada una vez que este repositorio tenga un remoto de GitHub).

---

# Roadmap de nuevos dominios

Ninguno de estos dominios existe todavía. Las tablas describen los especialistas *propuestos*, con
la metodología base sobre la que se construiría cada uno (Capa 1 del ETHOS: metodología reconocida
antes que invención propia).

## Estructura de repo prevista

Cuando exista más de un dominio, `skills/` se organizará por dominio en lugar de una lista plana:

```
skills/
├── comp-ben/          # Dominio existente: análisis de Comp & Ben
├── talent/            # Nuevo: Gestión de Talento
├── culture/           # Nuevo: Clima y Cultura
├── comms/             # Nuevo: Comunicación Interna
├── org-dev/           # Nuevo: Desarrollo Organizacional
└── _pipeline/         # Capa de proceso agnóstica al dominio (ya existente, generalizar naming)
    ├── plan-review, plan-cfo-review, plan-legal-review, auto-people-review
    ├── cycle-ship, publish-and-monitor, rollout-watch, market-drift-check
    ├── people-investigate, people-retro, document-cycle
    ├── compliance-audit, second-opinion, hris-connect, policy-qa, plan-policy-review
```

La capa `_pipeline/` ya es agnóstica al dominio en su diseño actual (revisa "cualquier plan", no
solo planes de compensación); solo necesita generalizar el lenguaje de sus plantillas para que no
asuma que el artefacto de entrada es siempre de Comp & Ben.

## Dominio: Gestión de Talento

| Comando propuesto | Especialista | Qué hace | Metodología base (Capa 1 del ETHOS) |
|---|---|---|---|
| `/talent-acquisition-audit` | Recruiting Partner | Audita el embudo de reclutamiento: tiempo de contratación, calidad de fuente, tasa de conversión por etapa | Funnel de reclutamiento estándar de la industria |
| `/performance-calibration` | Performance Analyst | Calibra evaluaciones de desempeño entre equipos para detectar sesgo de evaluador | Distribución forzada / calibración por comité, según lo que ya use la empresa |
| `/succession-planning` | Succession Strategist | Mapea riesgo de vacancia en posiciones clave y candidatos internos listos | Matriz 9-box |
| `/onboarding-design` | Onboarding Architect | Diseña el plan de incorporación de 30/60/90 días por rol o nivel | Marco 30-60-90 |

## Dominio: Desarrollo Organizacional

| Comando propuesto | Especialista | Qué hace | Metodología base |
|---|---|---|---|
| `/org-design-review` | Org Design Consultant | Analiza spans of control, capas jerárquicas, duplicidad de reportes | Principios estándar de diseño organizacional |
| `/training-needs-analysis` | L&D Analyst | Identifica brechas de habilidades por rol/nivel a partir de evaluaciones de desempeño | Análisis de brechas de competencias |
| `/change-management-plan` | Change Management Partner | Estructura un plan de gestión del cambio para una iniciativa organizacional | Modelo ADKAR o Kotter, citado explícitamente |
| `/org-health-diagnostic` | OD Diagnostician | Diagnóstico integral: cruza clima, rotación y desempeño para detectar salud organizacional | Se apoya en artefactos de `culture/` y `comp-ben/`; no duplica el cálculo |

## Dominio: Clima y Cultura

| Comando propuesto | Especialista | Qué hace | Metodología base |
|---|---|---|---|
| `/climate-survey-analysis` | Climate Analyst | Procesa resultados de encuesta de clima, segmenta por equipo/nivel, señala outliers | Escalas validadas (ej. Gallup Q12); nunca inventa un índice propio |
| `/engagement-diagnostics` | Engagement Specialist | Calcula eNPS y lo cruza con datos de rotación | eNPS estándar |
| `/culture-audit` | Culture Auditor | Compara valores declarados vs. señales observables (políticas, decisiones recientes) | Framework de coherencia cultural: declarado en el reporte como interpretación cualitativa, no como score numérico duro |

## Dominio: Comunicación Interna

| Comando propuesto | Especialista | Qué hace | Metodología base |
|---|---|---|---|
| `/comms-cascade-audit` | Internal Comms Auditor | Revisa si un mensaje llegó de forma consistente desde liderazgo hasta la línea de mando | Auditoría de cascada de comunicación |
| `/comms-plan-builder` | Comms Strategist | Diseña el plan de comunicación de un cambio organizacional (audiencias, canales, timing) | Modelo de comunicación de cambio (ADKAR u otro que la empresa ya use) |
| `/change-narrative-writer` | Change Communication Writer | Redacta el mensaje de un cambio sensible (reestructura, cambio de política) | Se apoya en `plan-legal-review` antes de publicar cualquier cosa sensible |

**Nota:** `comms-clarity` (edición de claridad de un borrador ya escrito; acción primero, jerga
fuera) ya está **construida**, pero vive en `skills/_pipeline/` en lugar de abrir este dominio: es
agnóstica de quién escribió el borrador (Comp & Ben hoy, cualquier dominio nuevo después), igual
que `policy-qa`/`document-cycle`, y nunca decide por su cuenta si un contenido sensible es seguro
de publicar: eso sigue siendo `plan-legal-review`. El orden de construcción de abajo (Comunicación
Interna al final) sigue vigente para los tres especialistas de la tabla de arriba, que sí requieren
la madurez legal de ese dominio.

## Reglas que se mantienen sin excepción (de ETHOS.md y CONTRIBUTING.md)

- Ningún dominio nuevo inventa su propio framework cuando ya existe uno reconocido (Capa 1 primero).
- Todo lo que sea cualitativo (cultura, clima) debe declarar explícitamente cuándo una conclusión
  es interpretación y no un cálculo; nunca presentar una lectura cualitativa con la falsa
  precisión de un número duro.
- Humildad legal se extiende a Comunicación Interna y cambios organizacionales sensibles
  (reestructuras, despidos masivos): deriva siempre a `plan-legal-review`.
- Ningún dominio nuevo se lanza con datos reales de prueba: dataset sintético propio por dominio
  en `examples/`.

---

## Orden de construcción sugerido

Primero se profundiza **Comp & Ben** (las skills del backlog de arriba), y después los dominios
nuevos en este orden:

1. **Gestión de Talento**: tiene la metodología más objetiva y cuantificable de los cuatro nuevos,
   más fácil de mantener la disciplina de "cómputo determinístico + LLM interpreta".
2. **Desarrollo Organizacional**: se apoya en artefactos que Comp & Ben y Talento ya producen
   (job-architecture, performance-calibration), tiene sinergia inmediata.
3. **Clima y Cultura**: requiere más cuidado en la capa de "honestidad con lo cualitativo".
4. **Comunicación Interna**: el dominio más dependiente de humildad legal; conviene construirlo
   último, cuando `plan-legal-review` ya esté probado en los otros tres dominios.

Es un orden, no un calendario: no hay fechas comprometidas para ninguno de estos dominios.
