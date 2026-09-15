import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export interface EvalResult {
  test: string;
  skill: string;
  pass: boolean;
  rationale?: string;
  costUsd?: number;
  backend?: string; // "claude" (default) o "agy": qué CLI/modelo corrió esta sesión E2E
}

export interface EvalRun {
  id: string;
  timestamp: string;
  gitRef?: string;
  results: EvalResult[];
}

export function storeDir(): string {
  const dir = join(homedir(), ".rhstack-dev", "evals");
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  return dir;
}

export function saveRun(run: Omit<EvalRun, "id">): EvalRun {
  const id = new Date(run.timestamp).getTime().toString(36);
  const full: EvalRun = { id, ...run };
  writeFileSync(join(storeDir(), `${full.timestamp.replace(/[:.]/g, "-")}-${id}.json`, ), JSON.stringify(full, null, 2));
  return full;
}

export function listRuns(): EvalRun[] {
  const dir = storeDir();
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => JSON.parse(readFileSync(join(dir, f), "utf-8")) as EvalRun)
    .sort((a, b) => a.timestamp.localeCompare(b.timestamp));
}

export function latestRuns(n: number): EvalRun[] {
  const runs = listRuns();
  return runs.slice(Math.max(0, runs.length - n));
}

export function compareRuns(a: EvalRun, b: EvalRun): { test: string; before: boolean | undefined; after: boolean | undefined }[] {
  const byTest = new Map<string, boolean>();
  for (const r of a.results) byTest.set(r.test, r.pass);
  const rows: { test: string; before: boolean | undefined; after: boolean | undefined }[] = [];
  const seen = new Set<string>();
  for (const r of b.results) {
    rows.push({ test: r.test, before: byTest.get(r.test), after: r.pass });
    seen.add(r.test);
  }
  for (const r of a.results) {
    if (!seen.has(r.test)) rows.push({ test: r.test, before: r.pass, after: undefined });
  }
  return rows;
}
