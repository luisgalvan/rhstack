# Contribuir a rhstack

Gracias por ayudar a construir el paquete de skills de RR. HH. de la comunidad. Hay dos formas de
contribuir: mejorar un especialista existente, o agregar uno nuevo.

Al enviar un PR aceptás los términos de [CLA.md](CLA.md): en resumen, licenciás tu contribución
para que el proyecto pueda seguir bajo MIT o adoptar otros términos en el futuro sin tener que
volver a pedirte permiso. Conservás el copyright de lo que escribiste.

## Agregar una skill nueva

1. Crea `skills/<dominio>/<skill-name>/SKILL.md.tmpl` (la fuente de verdad; nunca edites
   `SKILL.md` a mano) con frontmatter YAML (`name`, `description`) y la metodología del
   especialista, luego corre `bun run gen:skill-docs` para producir el `SKILL.md` generado. Haz
   commit de ambos archivos.
2. El `description` es el mecanismo de activación (trigger): escríbelo "insistente": qué hace la
   skill Y cada frase/contexto que debería activarla, incluso cuando el usuario no nombra la skill.
3. Sigue el estilo de la casa, visible en cualquier skill existente:
   - Una persona especialista con nombre y un punto de vista claro.
   - Una sección **Method** (numerada, imperativa): el *cómo*, con valores por defecto y el
     razonamiento detrás de ellos.
   - Una sección **Output** con un nombre y estructura de archivo exactos.
   - Una sección **Rules** para las cosas no negociables (honestidad con los datos, límites
     legales, entregas a otras skills).
4. El cómputo determinístico va en `scripts/` (Python 3, solo stdlib; sin dependencias), invocado
   desde el SKILL.md. Mantén el juicio en Markdown, la aritmética en código. El `.py` es la única
   fuente de verdad: el SKILL.md.tmpl lo invoca por ruta relativa desde la raíz del repo
   (`python skills/<dominio>/<skill>/scripts/<script>.py`), igual sin importar qué CLI de IA
   orquesta la skill (Claude Code, Antigravity CLI, Codex, Cursor, ver AGENTS.md) — el script corre
   como proceso del sistema operativo, no dentro del CLI. rhstack **no distribuye binarios
   compilados**: un `.exe` sin firma de código dispara advertencias de SmartScreen que confunden a
   la audiencia no técnica que esto busca servir, y compilarlo en una máquina de desarrollo
   introduce drift frente al entorno del usuario final. El único prerrequisito es Python 3.11+ en
   la máquina donde corre el agente; si el SKILL.md.tmpl invoca un script, debe indicar qué hacer
   si el comando falla por Python ausente (`winget install Python.Python.3.12` en Windows).
5. Corre `bun run skill:check` para confirmar que la skill nueva pasa las verificaciones de estilo
   de la casa (frontmatter, secciones requeridas, higiene de scripts), y `bun test` para la
   suite completa del nivel gratuito.
6. Prueba con el dataset sintético en `examples/`. Nunca hagas commit de datos reales de
   empleados: los PRs que contengan algo que parezca datos personales o salariales reales serán
   cerrados.
7. Agrega la skill nueva a la tabla de comandos de `README.md` y al roster de
   `skills/_pipeline/front-desk/SKILL.md.tmpl` en el mismo PR: ambos son el mapa que le permite a
   alguien sin trasfondo técnico llegar a tu skill sin memorizar su nombre de comando. No hace
   falta tocar `AGENTS.md` en este paso: `AGENTS.md` referencia esa tabla en lugar de duplicarla,
   así que no hay una tercera lista que sincronizar. `bun run gen:skill-docs` genera además el
   espejo de la skill nueva en `.cursor/skills/<name>/SKILL.md` automáticamente; haz commit de
   ese archivo generado junto con el resto.

## No negociables para toda skill

- **Sin datos de mercado fabricados.** Las skills deben instruir a Claude para que cite fuentes o
  pida al usuario datos de benchmark; nunca que invente percentiles.
- **Humildad legal.** Todo lo que toque obligaciones estatutarias (transparencia salarial,
  despidos, comités de empresa, tributación de beneficios) debe dirigir a los usuarios hacia
  asesoría legal local calificada.
- **Honestidad con muestras pequeñas.** Los análisis deben señalar cuándo n es demasiado pequeño
  para sacar conclusiones.
- **Inglés para el núcleo**, pero las variantes localizadas son muy bienvenidas como
  `skills/<name>-es/`, `-de/`, etc., adaptando el *contexto legal*, no solo el idioma.

## Distribución en otros agentes

rhstack se distribuye también hacia Antigravity CLI (`agy`, sucesora de Gemini CLI desde junio de
2026 — lee `AGENTS.md` directo desde la raíz, sin manifiesto propio), Codex y OpenCode
(`.codex-plugin/plugin.json`, `opencode.json`; apuntan directamente a `skills/`, sin copias) y
Cursor (`.cursor/skills/<name>/SKILL.md`, espejo generado). Los manifiestos
`qwen-extension.json` y `kimi.plugin.json` siguen el mismo patrón declarativo, pero son **mejor
esfuerzo**: nadie en este proyecto tiene acceso a Qwen Code ni a Kimi para probarlos de verdad, así
que no asumas que están validados de la misma forma que Antigravity CLI (que sí tiene cobertura
E2E real vía `bun run test:e2e:gemini`, ver AGENTS.md). Si los pruebas y encuentras que el formato
no coincide con lo que esa CLI espera, abre un issue o corrígelo: son los manifiestos más fáciles
de romper por drift silencioso porque nada en `bun test` los ejercita contra un agente real.

## Buscado

Ve [TODOS.md](TODOS.md) para el backlog actual: `workforce-planning`, `severance-calculator`,
`hris-migration` (una versión más profunda de `hris-connect`), y paquetes localizados
(ES/DE/FR/LATAM) adaptando el *contexto legal*, no solo el idioma.

También se buscan las primeras skills de los cuatro dominios que aún no existen (Gestión de
Talento, Desarrollo Organizacional, Clima y Cultura, Comunicación Interna). TODOS.md lista los
especialistas propuestos de cada uno con su metodología base; las mismas reglas no negociables de
arriba aplican igual, y en los dominios cualitativos (clima, cultura) se suma una: declarar
explícitamente cuándo una conclusión es interpretación y no un cálculo.

Abre un issue antes de PRs grandes para que podamos alinear el alcance.
