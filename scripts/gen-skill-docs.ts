#!/usr/bin/env bun
// Regenera cada skills/<name>/SKILL.md a partir de su SKILL.md.tmpl fuente de verdad, más el
// espejo de plataforma que se deriva de esa misma fuente (ver AGENTS.md): el mirror plano de
// Cursor en .cursor/skills/<name>/SKILL.md. SKILL.md.tmpl es lo que editan los contribuyentes;
// SKILL.md y el espejo son lo que cada agente realmente carga. AGENTS.md no tiene espejo propio:
// Antigravity CLI (agy) lo lee directo desde la raíz del repo, sin manifiesto ni copia aparte.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { parseAllSkills } from "../test/helpers/skill-parser.ts";

const REPO_ROOT = join(import.meta.dir, "..");
const GENERATED_MARKER =
  "<!-- ARCHIVO GENERADO: edita SKILL.md.tmpl, luego corre `bun run gen:skill-docs`. No edites este archivo directamente. -->\n\n";

// Cada SKILL.md puede terminar viéndose de forma aislada (un contribuyente que solo abre este
// archivo, un plugin cacheado en la máquina de alguien) sin pasar nunca por el README del repo;
// este footer deja la autoría/licencia visible ahí también, sin que cada plantilla tenga que
// repetirlo a mano en las 26+ skills.
const AUTHORSHIP_FOOTER =
  "\n---\n\n*Parte de [rhstack](https://github.com/luisgalvan/rhstack), creado por " +
  "[Luis Galvan](https://github.com/luisgalvan). Licencia MIT.*\n";

export function render(templateRaw: string): string {
  const match = templateRaw.match(/^(---\r?\n[\s\S]*?\r?\n---\r?\n)([\s\S]*)$/);
  if (!match) throw new Error("a la plantilla le falta el bloque de frontmatter");
  const [, frontmatterBlock, body] = match;
  const trimmedBody = body.replace(/^\r?\n/, "").replace(/\r?\n+$/, "\n");
  return frontmatterBlock + GENERATED_MARKER + trimmedBody + AUTHORSHIP_FOOTER;
}

// Cursor espera un directorio plano .cursor/skills/<name>/SKILL.md (sin subcarpetas de dominio),
// a diferencia de skills/<dominio>/<skill>/SKILL.md. El contenido es idéntico: es un espejo de
// distribución, no una segunda fuente de verdad.
export function cursorMirrorPath(repoRoot: string, skillName: string): string {
  return join(repoRoot, ".cursor", "skills", skillName, "SKILL.md");
}

function writeIfChanged(path: string, contents: string): boolean {
  let existing = "";
  try {
    existing = readFileSync(path, "utf-8");
  } catch {
    // aún no existe
  }
  if (existing === contents) return false;
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, contents, "utf-8");
  return true;
}

function main() {
  const skills = parseAllSkills(REPO_ROOT);
  let changed = 0;
  for (const skill of skills) {
    if (!skill.frontmatter.name || !skill.frontmatter.description) {
      throw new Error(`${skill.name}: el frontmatter de SKILL.md.tmpl debe tener name y description`);
    }
    if (skill.frontmatter.name !== skill.name) {
      throw new Error(`${skill.name}: el name del frontmatter "${skill.frontmatter.name}" debe coincidir con el nombre del directorio`);
    }
    const templateRaw = readFileSync(skill.templatePath, "utf-8");
    const rendered = render(templateRaw);
    if (writeIfChanged(skill.generatedPath, rendered)) {
      changed++;
      console.log(`ESCRITO ${skill.name}/SKILL.md`);
    }
    const mirrorPath = cursorMirrorPath(REPO_ROOT, skill.name);
    if (writeIfChanged(mirrorPath, rendered)) {
      changed++;
      console.log(`ESCRITO .cursor/skills/${skill.name}/SKILL.md`);
    }
  }

  console.log(`\n${skills.length} skill(s) verificada(s), ${changed} archivo(s) regenerado(s).`);
}

if (import.meta.main) main();
