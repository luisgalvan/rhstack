import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { judgeOutput } from "./helpers/llm-judge.ts";
import { cleanupSession, runSkillSession } from "./helpers/session-runner.ts";
import { saveRun, type EvalResult } from "./helpers/eval-store.ts";

// Nivel 3 (pagado, ~$0.15/run): corre cada skill basada en datos contra el dataset sintético y
// hace que un LLM judge califique la salida contra la rúbrica de honestidad-con-datos + estilo de la casa.

const SCENARIOS: { skill: string; prompt: string; outputFile: string }[] = [
  { skill: "comp-bands", prompt: "/comp-bands analyze examples/sample_employees.csv and propose bands for Engineering", outputFile: "comp-bands.md" },
  { skill: "pay-equity-audit", prompt: "/pay-equity-audit audit examples/sample_employees.csv by gender", outputFile: "pay-equity-report.md" },
  { skill: "merit-cycle", prompt: "/merit-cycle model a 4% budget merit cycle for examples/sample_employees.csv", outputFile: "merit-cycle-plan.md" },
];

const results: EvalResult[] = [];

describe.skipIf(!process.env.ANTHROPIC_API_KEY)("skill-llm-eval (Tier 3, paid)", () => {
  for (const scenario of SCENARIOS) {
    test(scenario.skill, async () => {
      const session = runSkillSession(scenario.prompt);
      try {
        expect(session.filesCreated).toContain(scenario.outputFile);
        const output = readFileSync(join(session.cwd, scenario.outputFile), "utf-8");
        const verdict = await judgeOutput(output, scenario.skill);
        results.push({ test: `skill-llm-eval:${scenario.skill}`, skill: scenario.skill, pass: verdict.pass, rationale: verdict.rationale });
        expect(verdict.pass, verdict.rationale).toBe(true);
      } finally {
        cleanupSession(session);
      }
    }, 120_000);
  }
});

process.on("exit", () => {
  if (results.length > 0) {
    saveRun({ timestamp: new Date().toISOString(), results });
  }
});
