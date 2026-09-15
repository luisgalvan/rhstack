#!/usr/bin/env bun
// Dashboard de salud para cada skill: frontmatter, secciones requeridas, higiene de scripts, drift de docs.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { parseAllSkills, scriptImports, PYTHON_STDLIB_ALLOWLIST } from "../test/helpers/skill-parser.ts";

const REPO_ROOT = join(import.meta.dir, "..");
const REQUIRED_SECTIONS = ["Method", "Output", "Rules"];

function main() {
  const skills = parseAllSkills(REPO_ROOT);
  let failures = 0;

  for (const skill of skills) {
    const problems: string[] = [];

    if (!skill.frontmatter.name) problems.push("falta `name` en el frontmatter");
    if (!skill.frontmatter.description) problems.push("falta `description` en el frontmatter");
    if (skill.frontmatter.name && skill.frontmatter.name !== skill.name) {
      problems.push(`el name del frontmatter "${skill.frontmatter.name}" != directorio "${skill.name}"`);
    }

    for (const section of REQUIRED_SECTIONS) {
      if (!skill.sections.some((s) => s === section || s.startsWith(`${section}:`))) {
        problems.push(`falta la sección "## ${section}"`);
      }
    }

    for (const ref of skill.scriptRefs) {
      const scriptPath = join(skill.dir, ref.replace(/^scripts\//, "scripts/"));
      if (!existsSync(scriptPath)) {
        problems.push(`referencia a ${ref} pero el archivo no existe`);
        continue;
      }
      const source = readFileSync(scriptPath, "utf-8");
      for (const mod of scriptImports(source)) {
        if (!PYTHON_STDLIB_ALLOWLIST.has(mod)) {
          problems.push(`${ref} importa un módulo que no es stdlib: "${mod}"`);
        }
      }
    }

    if (existsSync(skill.generatedPath)) {
      const generated = readFileSync(skill.generatedPath, "utf-8");
      const expectedBody = skill.body.trim();
      if (!generated.includes(expectedBody.slice(0, 40))) {
        problems.push("el SKILL.md generado parece desactualizado respecto al SKILL.md.tmpl: corre `bun run gen:skill-docs`");
      }
    } else {
      problems.push("no hay SKILL.md generado: corre `bun run gen:skill-docs`");
    }

    if (problems.length === 0) {
      console.log(`OK    ${skill.name}`);
    } else {
      failures++;
      console.log(`FAIL  ${skill.name}`);
      for (const p of problems) console.log(`        - ${p}`);
    }
  }

  console.log(`\n${skills.length} skill(s) verificada(s), ${failures} con problemas.`);
  if (failures > 0) process.exit(1);
}

main();
