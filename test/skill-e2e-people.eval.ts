import { describe, expect, test } from "bun:test";
import { cleanupSession, currentBackend, requiresAnthropicKey, runSkillSession } from "./helpers/session-runner.ts";
import { saveRun, type EvalResult } from "./helpers/eval-store.ts";

const backend = currentBackend();

// Nivel 2 (pagado, E2E): corridas completas de claude -p para las skills de artefactos de
// people/arquitectura. Separado de skill-e2e-comp para que un cambio en un grupo no fuerce
// el re-run del otro (ver test/helpers/touchfiles.ts).

const CASES: { skill: string; prompt: string; expectFiles: string[] }[] = [
  { skill: "people-office-hours", prompt: "/people-office-hours we're losing engineers and I don't know why", expectFiles: ["people-diagnostic.md"] },
  { skill: "job-architecture", prompt: "/job-architecture design a level spine for a 40-person Engineering org", expectFiles: ["job-architecture.md"] },
  { skill: "jd-writer", prompt: "/jd-writer write a JD for a Senior Backend Engineer", expectFiles: [] },
  { skill: "benefits-review", prompt: "/benefits-review audit our current benefits package: health insurance, 25 days PTO, no pension match", expectFiles: ["benefits-review.md"] },
];

const results: EvalResult[] = [];

describe.skipIf(requiresAnthropicKey(backend) && !process.env.ANTHROPIC_API_KEY)(`skill-e2e-people (Tier 2, paid, backend=${backend})`, () => {
  for (const c of CASES) {
    test(c.skill, () => {
      const session = runSkillSession(c.prompt);
      try {
        if (c.expectFiles.length === 0) {
          const producedSomeMd = session.filesCreated.some((f) => f.endsWith(".md"));
          results.push({ test: `skill-e2e-people:${c.skill}`, skill: c.skill, pass: producedSomeMd, backend });
          expect(producedSomeMd, `expected a .md output among [${session.filesCreated.join(", ")}]`).toBe(true);
          return;
        }
        for (const f of c.expectFiles) {
          const created = session.filesCreated.some((name) => name.toLowerCase() === f.toLowerCase());
          results.push({ test: `skill-e2e-people:${c.skill}:${f}`, skill: c.skill, pass: created, backend });
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
