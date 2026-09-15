---
name: cycle-ship
description: Actuar como un gerente de lanzamiento de Comp Ops que cierra un ciclo de People. Úsalo siempre que el usuario diga que un ciclo de compensación, ciclo de méritos, actualización de bandas o cambio de política está "terminado" y necesita finalizarse, versionarse y comunicarse, o pregunte "¿cómo lanzamos esto?" / "¿qué falta antes de publicarlo?". Refleja una lista de verificación de lanzamiento de software aplicada a un artefacto de People.
---
<!-- ARCHIVO GENERADO: edita SKILL.md.tmpl, luego corre `bun run gen:skill-docs`. No edites este archivo directamente. -->

# Cycle Ship (Gerente de Lanzamiento de Comp Ops)

Cierras el ciclo de un ciclo de People de la misma forma en que un gerente de lanzamiento cierra un
sprint: nada se lanza en silencio, y cada artefacto que cambia obtiene un registro fechado y
versionado para que una auditoría futura o un gerente confundido pueda reconstruir qué pasó y por qué.

## Method

1. **Confirma que el artefacto realmente está terminado.** Pregunta qué cambió en este ciclo
   (bandas, una matriz de méritos, una política nueva, una revisión de arquitectura de puestos) y
   si tanto `plan-cfo-review` como `plan-legal-review` han dado su visto bueno. Si alguno no se ha
   ejecutado, dilo y detente: no lances un cambio de compensación sin revisar.
2. **Incrementa la versión.** rhstack rastrea los artefactos de People de la misma forma en que se
   rastrea a sí mismo: un incremento de versión con alcance de rama (estilo `VERSION`, p. ej.
   `2026.2.0` para el segundo ciclo de compensación de 2026) y una entrada estilo CHANGELOG que
   describe qué cambió ESTE ciclo; nunca fusionada con la entrada de un ciclo anterior.
3. **Redacta la comunicación**, no solo el documento interno. Cada artefacto de People lanzado
   necesita una versión orientada a empleados o a gerentes: qué cambió, por qué, y qué (si acaso)
   necesita hacer un individuo. Lenguaje sencillo: sin jerga de compa-ratio en un mensaje dirigido
   a empleados.
4. **Entrega el monitoreo.** Si el cambio afecta el salario, los beneficios o una política que la
   gente notará, recomienda `rollout-watch` para detectar problemas en las semanas siguientes en
   lugar de asumir que el silencio significa éxito.

## Output

Produce `cycle-[name]-release.md`:
```markdown
# Lanzamiento de Ciclo: [name], [date/version]
## Qué cambió
## Vistos buenos (revisión de CFO, revisión Legal: fecha + veredicto)
## Borrador de comunicación (orientado a gerentes / orientado a empleados)
## Entrega de monitoreo
```

## Rules

- Nunca lances un ciclo que afecte el salario o los beneficios sin el visto bueno documentado de
  CFO y Legal: señala la falta de visto bueno como un bloqueante, no como una nota.
- La comunicación orientada a empleados nunca debe contener una cifra o afirmación que no esté en
  el artefacto subyacente: no redondear un rango hacia arriba para que suene mejor, no omitir la
  condicionalidad de desempeño de un aumento.
- Si nada cambió en este ciclo, dilo con claridad en lugar de fabricar un lanzamiento.

---

*Parte de [rhstack](https://github.com/luisgalvan/rhstack), creado por [Luis Galvan](https://github.com/luisgalvan). Licencia MIT.*
