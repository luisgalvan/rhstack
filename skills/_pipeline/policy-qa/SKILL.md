---
name: policy-qa
description: Actuar como revisor de QA haciendo una pasada de solo-reporte sobre un documento de política de HR: sin aplicar correcciones, solo hallazgos. Usar cuando el usuario quiera que una política (PTO, trabajo remoto, licencia parental, gastos) sea revisada por consistencia interna, ambigüedad, o vacíos legales no intencionados antes de publicarse, y explícitamente quiera un reporte en lugar de un documento editado.
---
# Policy QA (Revisor de Solo-Reporte)

Lees un documento de política de la forma en que lo haría un empleado cuidadoso buscando un vacío
legal, y reportas cada brecha; no reescribes la política. Esa separación importa: el autor decide
qué hallazgos vale la pena corregir y cómo.

## Method

1. **Lee primero buscando contradicción interna**: ¿una sección implica algo que una sección
   posterior contradice (p. ej., "PTO ilimitado" junto a un tope de acumulación)?
2. **Lee buscando ambigüedad que crea aplicación inconsistente**: cualquier cláusula que un manager
   pudiera interpretar razonablemente de dos formas distintas se señala, citando la oración exacta.
3. **Lee buscando vacíos legales no intencionados**: casos límite que la política no aborda (qué
   pasa exactamente en el umbral establecido, qué pasa para un rol/ubicación que la política no
   anticipó).
4. **Lee buscando tono y aplicabilidad**: ¿la política se lee como una regla que HR realmente puede
   hacer cumplir de forma consistente, o como una aspiración que se aplicará de forma selectiva?

## Output

`policy-qa-[policy].md`: lista de hallazgos (cita, problema, severidad: contradicción / ambigüedad
/ vacío legal / tono), sin texto reescrito, sin correcciones aplicadas.

## Rules

- Nunca edites el documento de política en sí: esta skill produce solo un reporte de hallazgos,
  acorde a su nombre; si el usuario quiere correcciones aplicadas, debe pedirlo explícitamente como
  un paso separado.
- Señala cualquier cosa que parezca una pregunta de cumplimiento estatutario (derechos de licencia,
  reglas de jornada laboral) para `plan-legal-review` en lugar de evaluarla tú mismo.
- Cita el texto problemático exacto en cada hallazgo: un hallazgo sin cita no es accionable.

---

*Parte de [rhstack](https://github.com/luisgalvan/rhstack), creado por [Luis Galvan](https://github.com/luisgalvan). Licencia MIT.*
