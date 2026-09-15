#!/usr/bin/env bun
// Modo watch: regenera los docs SKILL.md y corre el health check en cada cambio bajo skills/.
import { watch } from "node:fs";
import { join } from "node:path";

const REPO_ROOT = join(import.meta.dir, "..");
const SKILLS_DIR = join(REPO_ROOT, "skills");

async function runOnce() {
  console.log("\n--- regenerando + verificando skills ---");
  const gen = Bun.spawnSync(["bun", "run", join(REPO_ROOT, "scripts/gen-skill-docs.ts")], { stdout: "inherit", stderr: "inherit" });
  if (gen.exitCode !== 0) return;
  Bun.spawnSync(["bun", "run", join(REPO_ROOT, "scripts/skill-check.ts")], { stdout: "inherit", stderr: "inherit" });
}

let timer: ReturnType<typeof setTimeout> | undefined;
function schedule() {
  clearTimeout(timer);
  timer = setTimeout(runOnce, 200);
}

console.log(`Observando ${SKILLS_DIR} en busca de cambios (Ctrl+C para detener)...`);
runOnce();
watch(SKILLS_DIR, { recursive: true }, () => schedule());
