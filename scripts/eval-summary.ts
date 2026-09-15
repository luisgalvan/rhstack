#!/usr/bin/env bun
import { listRuns } from "../test/helpers/eval-store.ts";

const runs = listRuns();
const totals = new Map<string, { pass: number; fail: number }>();
for (const run of runs) {
  for (const r of run.results) {
    const t = totals.get(r.test) ?? { pass: 0, fail: 0 };
    if (r.pass) t.pass++;
    else t.fail++;
    totals.set(r.test, t);
  }
}
console.log(`${runs.length} corrida(s) registrada(s).\n`);
for (const [test, t] of totals) {
  const total = t.pass + t.fail;
  console.log(`${test}: ${t.pass}/${total} tasa de aprobación (${((t.pass / total) * 100).toFixed(0)}%)`);
}
