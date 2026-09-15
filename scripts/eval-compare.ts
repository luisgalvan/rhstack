#!/usr/bin/env bun
import { compareRuns, latestRuns } from "../test/helpers/eval-store.ts";

const runs = latestRuns(2);
if (runs.length < 2) {
  console.log("Se necesitan al menos 2 corridas de evals guardadas para comparar. Corre `bun run test:evals` primero.");
  process.exit(0);
}
const [before, after] = runs;
console.log(`Comparando ${before.timestamp} -> ${after.timestamp}\n`);
for (const row of compareRuns(before, after)) {
  const flag = row.before === row.after ? "  " : row.after ? "+ " : "- ";
  console.log(`${flag}${row.test}: ${row.before ?? "n/a"} -> ${row.after ?? "n/a"}`);
}
