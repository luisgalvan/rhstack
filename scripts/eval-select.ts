#!/usr/bin/env bun
// Selección de pruebas basada en diff: muestra (o corre) qué pruebas pagadas aplican al diff de git actual.
import { join } from "node:path";
import { affectedTests } from "../test/helpers/touchfiles.ts";

const REPO_ROOT = join(import.meta.dir, "..");

function changedFiles(): string[] {
  const base = process.env.BASE_BRANCH || "main";
  const proc = Bun.spawnSync(["git", "diff", "--name-only", `${base}...HEAD`], { cwd: REPO_ROOT });
  if (proc.exitCode !== 0) return [];
  return proc.stdout.toString().trim().split(/\r?\n/).filter(Boolean);
}

function main() {
  const args = process.argv.slice(2);
  const run = args.includes("--run");
  const onlyIdx = args.indexOf("--only");
  const only = onlyIdx !== -1 ? (args[onlyIdx + 1] as "e2e" | "llm-eval") : undefined;
  const all = process.env.EVALS_ALL === "1" || args.includes("--all");

  const files = changedFiles();
  const specs = affectedTests(files, { only, all });

  console.log(`Archivos modificados (vs ${process.env.BASE_BRANCH || "main"}): ${files.length}`);
  console.log(`${specs.length} archivo(s) de prueba seleccionado(s):`);
  for (const s of specs) console.log(`  - ${s.file} [${s.tier}]`);

  if (!run) return;
  if (specs.length === 0) {
    console.log("\nNada que correr.");
    return;
  }
  // El backend "agy" (Gemini) no habla con la API de Anthropic para las pruebas E2E, pero el
  // juez LLM (tier "llm-eval") siempre lo hace, sin importar el backend de la sesión E2E.
  const backend = process.env.RHSTACK_E2E_BACKEND === "agy" ? "agy" : "claude";
  const needsAnthropicKey = backend === "claude" || specs.some((s) => s.tier === "llm-eval");
  if (needsAnthropicKey && !process.env.ANTHROPIC_API_KEY) {
    console.error("\nANTHROPIC_API_KEY no está configurada: los evals pagados la requieren. Abortando ejecución.");
    process.exit(1);
  }
  const proc = Bun.spawnSync(["bun", "test", ...specs.map((s) => `./${s.file}`)], {
    cwd: REPO_ROOT,
    stdout: "inherit",
    stderr: "inherit",
  });
  process.exit(proc.exitCode ?? 1);
}

main();
