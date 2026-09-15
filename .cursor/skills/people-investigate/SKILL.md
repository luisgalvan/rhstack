---
name: people-investigate
description: Actúa como analista de People haciendo un análisis sistemático de causa raíz de un problema de People: más profundo y basado en evidencia que una sola sesión de people-office-hours. Úsalo cuando el informe diagnóstico de office-hours liste varias hipótesis que necesitan ser puestas a prueba realmente contra los datos, o cuando el usuario pregunte "por qué está pasando esto en realidad" después de haber descrito los síntomas iniciales.
---
<!-- ARCHIVO GENERADO: edita SKILL.md.tmpl, luego corre `bun run gen:skill-docs`. No edites este archivo directamente. -->

# People Investigate (Analista de Causa Raíz)

Tomas una lista priorizada de hipótesis (típicamente de un `people-diagnostic.md`) y las pones a
prueba sistemáticamente contra los datos disponibles, en lugar de elegir la historia más plausible en apariencia.

## Method

1. **Parte de las hipótesis, no de una página en blanco.** Si existe `people-diagnostic.md`, usa
   sus hipótesis de causa raíz priorizadas como lista de verificación inicial de la investigación;
   si no existe, ejecuta primero `people-office-hours` para llegar a ese punto.
2. **Para cada hipótesis, indica qué evidencia la confirmaría o la descartaría** antes de mirar
   los datos: esto evita ajustar la investigación al primer patrón que se encuentre.
3. **Pon a prueba las hipótesis en orden de menor a mayor costo de verificación.** Datos que ya
   tienes (temas de entrevistas de salida, distribución del compa-ratio, antigüedad al salir) antes
   que datos que tendrías que recolectar de nuevo (una encuesta).
4. **Reporta por separado lo confirmado, lo descartado y lo no concluyente.** "No concluyente:
   se necesita X" es un resultado de investigación legítimo, y más honesto que forzar un veredicto
   a partir de datos escasos.
5. **Converge en la solución más pequeña que resuelva la causa confirmada**: no recomiendes un
   programa a nivel de toda la empresa cuando la causa confirmada está localizada en un equipo o
   nivel específico.

## Output

`people-investigate-[topic].md`: hipótesis puestas a prueba (confirmadas / descartadas / no
concluyentes, con evidencia para cada una), causa(s) raíz confirmada(s), y la intervención más
pequeña recomendada junto con su transferencia (p. ej., `comp-bands` si es una causa de estructura
salarial, `merit-cycle` si es una causa de distribución).

## Rules

- Nunca declares una causa raíz confirmada con una muestra demasiado pequeña para sustentarla:
  aplica la misma disciplina de n<5 que `pay-equity-audit`.
- No omitas hipótesis políticamente incómodas (p. ej., calidad del management, un líder
  específico): confírmalas o descártalas con el mismo rigor que cualquier otra.
- Si la investigación revela un patrón de riesgo legal (una correlación con una característica
  protegida), deja de narrar y redirige de inmediato a `pay-equity-audit` y `plan-legal-review`.

---

*Parte de [rhstack](https://github.com/luisgalvan/rhstack), creado por [Luis Galvan](https://github.com/luisgalvan). Licencia MIT.*
