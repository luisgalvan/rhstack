import { describe, expect, test } from "bun:test";
import { cleanupSession, currentBackend, requiresAnthropicKey, runSkillSession } from "./helpers/session-runner.ts";
import { saveRun, type EvalResult } from "./helpers/eval-store.ts";

const backend = currentBackend();

// Nivel 2 (pagado, E2E): corridas completas de claude -p para las skills de artefactos de
// compensación, verificando que se produzcan los archivos de salida correctos. Separado de
// skill-e2e-people para que un cambio en un grupo no fuerce el re-run del otro (ver
// test/helpers/touchfiles.ts).

const CASES: { skill: string; prompt: string; expectFiles: string[] }[] = [
  { skill: "comp-bands", prompt: "/comp-bands analyze examples/sample_employees.csv and propose bands for Engineering", expectFiles: ["comp-bands.md", "comp-bands.csv"] },
  { skill: "pay-equity-audit", prompt: "/pay-equity-audit audit examples/sample_employees.csv by gender", expectFiles: ["pay-equity-report.md"] },
  { skill: "merit-cycle", prompt: "/merit-cycle model a 4% budget merit cycle for examples/sample_employees.csv", expectFiles: ["merit-cycle-plan.md", "merit-increases.csv"] },
  { skill: "offer-builder", prompt: "/offer-builder build an offer for an L4 Engineering candidate using examples/sample_employees.csv as internal peers", expectFiles: ["offer-l4-engineering.md"] },
  { skill: "survey-analysis", prompt: "/survey-analysis fit a linear market model to examples/sample_survey_points.csv (x=years_experience, y=survey_median) and compare examples/sample_market_employees.csv against it", expectFiles: ["survey-analysis-report.md"] },
];

const results: EvalResult[] = [];

describe.skipIf(requiresAnthropicKey(backend) && !process.env.ANTHROPIC_API_KEY)(`skill-e2e-comp (Tier 2, paid, backend=${backend})`, () => {
  for (const c of CASES) {
    test(c.skill, () => {
      const session = runSkillSession(c.prompt);
      try {
        for (const f of c.expectFiles) {
          const created = session.filesCreated.some((name) => name.toLowerCase() === f.toLowerCase());
          results.push({ test: `skill-e2e-comp:${c.skill}:${f}`, skill: c.skill, pass: created, backend });
          expect(created, `expected ${f} among [${session.filesCreated.join(", ")}]`).toBe(true);
        }
      } finally {
        cleanupSession(session);
      }
    }, 120_000);
  }
});

process.on("exit", () => {
  if (results.length > 0) saveRun({ timestamp: new Date().toISOString(), results });
});
