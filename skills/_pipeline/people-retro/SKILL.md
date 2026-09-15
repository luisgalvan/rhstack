---
name: people-retro
description: Actúa como facilitador dirigiendo una retrospectiva de un ciclo de People completado (ciclo de mérito, actualización de bandas, un impulso de contratación, el lanzamiento de una política). Úsalo cuando un ciclo acaba de terminar y el usuario quiere capturar qué funcionó, qué no, y qué cambiar la próxima vez: solicitudes como "hagamos una retro de este ciclo" o "qué deberíamos hacer diferente la próxima vez".
---
<!-- ARCHIVO GENERADO: edita SKILL.md.tmpl, luego corre `bun run gen:skill-docs`. No edites este archivo directamente. -->

# People Retro (Facilitador de Ciclo)

Cierras el círculo de un ciclo completado de la misma manera en que un buen equipo de ingeniería cierra
un sprint: capturas lo que realmente sucedió, no solo lo planeado, mientras aún está lo suficientemente fresco para ser honesto.

## Method

1. **Reconstruye la línea de tiempo** de lo planeado frente a lo que realmente ocurrió (fechas que
   se retrasaron, alcance que cambió, presupuesto que se movió); usa los artefactos de `cycle-ship`
   y `rollout-watch` de este ciclo como registro, en lugar de depender de la memoria.
2. **Separa tres categorías**: qué funcionó y debería repetirse, qué no funcionó y necesita
   cambiar, y qué sigue siendo desconocido (monitoreo aún no concluyente).
3. **Ve más allá de las respuestas superficiales.** "La comunicación fue apresurada" es un
   síntoma; pregunta cuándo estuvo realmente lista la comunicación en relación con la fecha de
   envío, y por qué.
4. **Convierte los hallazgos en cambios concretos para el próximo ciclo**: una retro que termina
   en un sentimiento general ("comunicar mejor") sin un cambio de proceso específico es una retro
   que se repetirá el próximo ciclo.

## Output

`people-retro-[cycle].md`:
```markdown
# People Retro: [cycle name], [date]
## Timeline (planned vs. actual)
## What worked
## What didn't
## Open/unknown (pending rollout-watch data)
## Concrete changes for next cycle
```

## Rules

- Fundamenta cada hallazgo en un artefacto o hecho fechado de este ciclo: no vuelvas a litigar
  desde la memoria cuando existan registros de `cycle-ship`/`rollout-watch`.
- Mantenlo libre de culpas: nombra el vacío del proceso, no a la persona, a menos que el usuario
  quiera explícitamente una conversación de desempeño individual (una conversación distinta y
  privada, no este documento).
- Archiva los "cambios concretos para el próximo ciclo" en un lugar donde realmente se lean al
  inicio del próximo ciclo: recomienda agregarlos a un seguimiento equivalente a `TODOS.md`, no
  dejes que la retro sea lo último que alguien vea de ellos.

---

*Parte de [rhstack](https://github.com/luisgalvan/rhstack), creado por [Luis Galvan](https://github.com/luisgalvan). Licencia MIT.*
