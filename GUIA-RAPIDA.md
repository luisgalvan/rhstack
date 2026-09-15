# Guía rápida para RH (sin experiencia técnica)

Esta guía es para ti si trabajas en Recursos Humanos / Compensaciones y nunca has usado una
terminal, no sabes programar, y solo conoces lo básico de escribirle a una IA. No necesitas saber
más que eso. Si ya eres una persona técnica, usa el [README](README.md) en su lugar: es más
denso y va directo al grano.

## ¿Qué es rhstack, en una frase?

rhstack convierte a Claude Code en un equipo de especialistas de People que puedes invocar
escribiendo en español normal (un analista de compensación, un auditor de equidad salarial, un
redactor de descripciones de puesto), cada uno sabe hacer una cosa y la hace siguiendo una
metodología ya definida. Tú no "programas" nada: **escribes lo que necesitas, como si le
escribieras a un colega**, y el especialista hace el trabajo y te entrega un documento.

## Antes de empezar: instalación de un solo comando

1. Que te instalen **[Claude Code](https://docs.claude.com/en/docs/claude-code)** en tu
   computadora (es la aplicación que vas a usar para chatear).
2. Dentro de Claude Code, escribe estos dos comandos (los puedes escribir tú misma/o, no
   requieren saber programar):
   ```
   /plugin marketplace add luisgalvan/rhstack
   /plugin install rhstack@luisgalvan
   ```
   Esto deja disponibles todos los comandos (`/rhstack:comp-bands`, `/rhstack:people-office-hours`,
   etc.): no hay que clonar ningún repositorio ni tocar una terminal fuera de Claude Code.
3. Cuando salga una versión nueva, actualiza con `/plugin marketplace update`: tampoco requiere
   volver a instalar nada a mano.

Si ya te dijeron "listo, ya está instalado", puedes saltarte todo lo anterior. Nota: los comandos
llevan el prefijo `rhstack:` (p. ej. `/rhstack:comp-bands`) porque así el plugin evita choques de
nombre con otros plugins que tengas instalados; el resto de esta guía los escribe sin el prefijo
por brevedad, pero funcionan igual con él.

## Tu primera vez: 3 pasos

### Paso 1: Dile a rhstack cómo se ve tu información de empleados (solo una vez)

Antes de pedir cualquier análisis, rhstack necesita entender cómo exporta tu empresa los datos de
People (qué columna es el salario, cuál es el nivel, en qué moneda están, etc.). Esto se hace
**una sola vez**, y luego nunca más te lo vuelve a preguntar.

Abre Claude Code y escribe:

```
/hris-connect aquí está una muestra de nuestra exportación de empleados: [adjunta o pega tu archivo]
```

Te va a hacer un par de preguntas si algo no es obvio (por ejemplo "¿esta columna es el salario
base o el total con bono?"). Contesta con lo que tú sabes; no necesitas saber nada técnico, solo
conocer tus propios datos.

### Paso 2: Pide lo que necesitas, en tus propias palabras

No necesitas memorizar comandos exactos. La forma más simple es escribir `/front-desk` y contarle
tu problema como si le escribieras a la recepción de un equipo de People: él identifica qué
especialista necesitas y te responde directamente como ese especialista, sin que tengas que saber
cómo se llama ningún otro comando. Por ejemplo:

> "/front-desk estamos perdiendo mucha gente del equipo de Ventas y no sé por qué, ayúdame a
> entender qué está pasando."

También puedes escribir directamente lo que te preocupa sin el `/front-desk`: Claude Code suele
identificar solo qué especialista necesitas. Por ejemplo:

> "Estamos perdiendo mucha gente del equipo de Ventas y no sé por qué, ayúdame a entender qué está
> pasando."

Eso activa al CHRO (`/people-office-hours`), que es el punto de entrada recomendado cuando **no
tienes claro cuál es el problema real**: te va a hacer preguntas antes de proponerte una
solución, igual que lo haría un buen director de RH.

Si ya sabes exactamente qué necesitas, puedes ser directo:

> "/comp-bands analiza nuestro archivo de empleados y arma bandas salariales para el equipo de
> Ingeniería"

> "/pay-equity-audit revisa si hay brechas salariales por género en este archivo"

> "/jd-writer escríbeme la descripción de puesto para un Gerente de Producto Senior"

### Paso 3: Revisa el documento que te entrega

Cada especialista termina su trabajo con un archivo (por ejemplo `comp-bands.md` o
`pay-equity-report.md`) que puedes abrir, leer y compartir con tu equipo o con Finanzas/Legal.
Estos documentos citan de dónde salió cada número; rhstack nunca se inventa cifras de mercado.

## Prueba sin riesgo primero

Antes de usar datos reales de tu empresa, puedes practicar con un archivo de ejemplo que ya
incluye rhstack (son datos inventados, ninguna persona real):

```
/comp-bands analiza examples/sample_employees.csv y propón bandas para la familia de Ingeniería
```

Así ves cómo se ve un resultado real antes de arriesgar información sensible.

## ¿Cuál especialista uso para qué? (los más comunes)

| Si tu problema es... | Escribe... |
|---|---|
| No sé qué está pasando, algo anda mal en People | `/people-office-hours [describe el problema]` |
| Necesito ordenar niveles y títulos | `/job-architecture` |
| Necesito bandas salariales / saber si pagamos justo | `/comp-bands` |
| Sospecho una brecha salarial (género, etc.) | `/pay-equity-audit` |
| Voy a hacer la revisión anual de sueldos | `/merit-cycle` |
| Tengo que armar una oferta para un candidato | `/offer-builder` |
| Necesito revisar nuestros beneficios | `/benefits-review` |
| Necesito escribir una descripción de puesto | `/jd-writer` |
| Ya tengo un plan y quiero que alguien lo revise antes de publicarlo | `/plan-review` |
| Voy a lanzar un cambio de comp/política | `/cycle-ship` |

La tabla completa de los 26 especialistas está en el [README](README.md#el-equipo-virtual-de-people)
, pero para el 90% de las tareas del día a día, esta tabla corta es suficiente.

## Glosario de 5 palabras que vas a ver

- **Skill (habilidad):** un especialista con una tarea específica. `/comp-bands` es una skill.
- **Comando / slash command:** la forma de invocar a un especialista, siempre empieza con `/`.
  Pero no es obligatorio saberte el nombre exacto: puedes describir tu problema en texto normal
  y Claude Code te sugiere cuál usar.
- **Artefacto:** el documento que produce un especialista (un `.md` o `.csv`): es lo que le
  compartes a otras personas.
- **CLAUDE.md:** el archivo donde rhstack recuerda la configuración de tu empresa (moneda,
  columnas de tu HRIS, jurisdicción) para no tener que volver a preguntarte.
- **Ciclo:** la secuencia completa desde diagnosticar un problema hasta lanzarlo y monitorearlo:
  como un proyecto de principio a fin.

## Cosas que rhstack SIEMPRE hace por ti (para que no te preocupes)

- Nunca se inventa un número de mercado: o cita su fuente, o te pide que le des los datos de
  encuesta.
- Te avisa si tu grupo de datos es muy pequeño para sacar una conclusión confiable (menos de 5
  personas por grupo).
- Nunca da la última palabra en temas legales; siempre te recuerda consultar con asesoría legal
  calificada para temas de transparencia salarial, comités de empresa, etc.

## Sobre la privacidad de tus datos

Los datos de compensación son de los más sensibles que maneja una empresa.

- rhstack solo trabaja con los archivos que tú le entregas explícitamente en la conversación;
  nunca busca datos por su cuenta.
- **Antes de pegar datos reales de empleados**, confirma con tu equipo de IT/Legal que está
  permitido según la política de datos de tu empresa.
- Si tienes dudas, empieza siempre con el archivo de ejemplo (`examples/sample_employees.csv`)
  hasta que te sientas cómoda/o con cómo funciona.

## Si algo no funciona

- **"No reconoce el comando `/algo`"** → confirma que el plugin esté instalado (`/plugin list` lo
  muestra), o prueba con el prefijo completo (`/rhstack:comp-bands` en vez de `/comp-bands`).
- **"No sé qué columna es cuál en mi archivo"** → no adivines, dile a Claude "no estoy segura/o
  de qué es esta columna" y te va a preguntar en vez de asumir.
- **"El resultado no cuadra con lo que esperaba"** → pídele a otro especialista que lo revise:
  escribe `/plan-review revisa este análisis` y te dará una segunda opinión antes de que lo uses.
- **Cualquier otra duda** → pregúntale directamente a Claude Code en español, con tus propias
  palabras. No hay una forma "incorrecta" de pedir ayuda.
