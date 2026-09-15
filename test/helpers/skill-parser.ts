import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";

export interface ParsedSkill {
  dir: string;
  name: string;
  templatePath: string;
  generatedPath: string;
  frontmatter: { name?: string; description?: string };
  body: string;
  sections: string[];
  scriptRefs: string[];
}

const FRONTMATTER_RE = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/;
const SECTION_RE = /^##\s+(.+)$/gm;
const SCRIPT_REF_RE = /scripts\/[\w-]+\.py/g;

export function skillsRoot(repoRoot: string): string {
  return join(repoRoot, "skills");
}

// skills/ está organizado por dominio (skills/<dominio>/<skill>/, p. ej. skills/comp-ben/,
// skills/_pipeline/): cada skill se identifica por su nombre de directorio hoja (que debe
// coincidir con el `name` de su frontmatter), sin importar bajo qué dominio viva. Esta función
// recorre el árbol y devuelve la ruta relativa a skills/ de cada directorio que contenga un
// SKILL.md.tmpl.
function findSkillPaths(repoRoot: string): string[] {
  const root = skillsRoot(repoRoot);
  const out: string[] = [];
  function walk(dir: string, rel: string) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (!entry.isDirectory()) continue;
      const full = join(dir, entry.name);
      const relPath = rel ? join(rel, entry.name) : entry.name;
      if (existsSync(join(full, "SKILL.md.tmpl"))) {
        out.push(relPath);
      } else {
        walk(full, relPath);
      }
    }
  }
  walk(root, "");
  return out;
}

export function listSkillDirs(repoRoot: string): string[] {
  return findSkillPaths(repoRoot).map((relPath) => relPath.split(/[\\/]/).pop()!);
}

function parseFrontmatter(raw: string): { frontmatter: { name?: string; description?: string }; body: string } {
  const match = raw.match(FRONTMATTER_RE);
  if (!match) return { frontmatter: {}, body: raw };
  const [, fm, body] = match;
  const frontmatter: { name?: string; description?: string } = {};
  for (const line of fm.split(/\r?\n/)) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) frontmatter[kv[1] as "name" | "description"] = kv[2].trim();
  }
  return { frontmatter, body };
}

export function parseSkill(repoRoot: string, name: string): ParsedSkill {
  const relPath = findSkillPaths(repoRoot).find((p) => p.split(/[\\/]/).pop()! === name);
  if (!relPath) throw new Error(`skill no encontrada bajo skills/: "${name}"`);
  const dir = join(skillsRoot(repoRoot), relPath);
  const templatePath = join(dir, "SKILL.md.tmpl");
  const generatedPath = join(dir, "SKILL.md");
  const raw = readFileSync(templatePath, "utf-8");
  const { frontmatter, body } = parseFrontmatter(raw);
  const sections = [...body.matchAll(SECTION_RE)].map((m) => m[1].trim());
  const scriptRefs = [...new Set([...body.matchAll(SCRIPT_REF_RE)].map((m) => m[0]))];
  return { dir, name, templatePath, generatedPath, frontmatter, body, sections, scriptRefs };
}

export function parseAllSkills(repoRoot: string): ParsedSkill[] {
  return listSkillDirs(repoRoot).map((name) => parseSkill(repoRoot, name));
}

// Módulos stdlib de Python 3 referenciados por los scripts de análisis de rhstack. Los scripts
// nunca deben importar fuera de esta lista: el cómputo determinístico y sin dependencias es un
// requisito de estilo de la casa.
export const PYTHON_STDLIB_ALLOWLIST = new Set([
  "argparse", "collections", "csv", "dataclasses", "datetime", "itertools", "json", "math",
  "os", "re", "statistics", "sys", "typing", "functools", "pathlib", "enum", "textwrap",
  "__future__",
]);

export function scriptImports(scriptSource: string): string[] {
  const modules: string[] = [];
  for (const line of scriptSource.split(/\r?\n/)) {
    const imp = line.match(/^\s*import\s+([\w.]+)/) || line.match(/^\s*from\s+([\w.]+)\s+import/);
    if (imp) modules.push(imp[1].split(".")[0]);
  }
  return modules;
}
