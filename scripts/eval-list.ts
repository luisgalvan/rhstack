#!/usr/bin/env bun
import { listRuns } from "../test/helpers/eval-store.ts";

for (const run of listRuns()) {
  const passed = run.results.filter((r) => r.pass).length;
  console.log(`${run.timestamp}  ${run.id}  ${passed}/${run.results.length} passed  ${run.gitRef ?? ""}`);
}
