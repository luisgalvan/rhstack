// Mapea cada prueba pagada a los archivos de los que depende, para la selección de pruebas
// basada en diff. Cambiar un GLOBAL_TOUCHFILE dispara todas las pruebas; cambiar los archivos
// propios de una skill dispara solo las pruebas que cubren esa skill.

export const GLOBAL_TOUCHFILES = [
  "scripts/gen-skill-docs.ts",
  "test/helpers/skill-parser.ts",
  "test/helpers/session-runner.ts",
  "test/helpers/llm-judge.ts",
  "test/helpers/eval-store.ts",
];

export interface TestSpec {
  file: string;
  tier: "e2e" | "llm-eval";
  touches: string[]; // prefijos tipo glob; un archivo modificado que coincida con cualquier prefijo dispara esta prueba
}

export const TEST_SPECS: TestSpec[] = [
  {
    file: "test/skill-e2e-comp.eval.ts",
    tier: "e2e",
    touches: ["skills/comp-ben/comp-bands/", "skills/comp-ben/pay-equity-audit/", "skills/comp-ben/merit-cycle/", "skills/comp-ben/offer-builder/", "skills/comp-ben/survey-analysis/"],
  },
  {
    file: "test/skill-e2e-people.eval.ts",
    tier: "e2e",
    touches: ["skills/comp-ben/people-office-hours/", "skills/comp-ben/job-architecture/", "skills/comp-ben/jd-writer/", "skills/comp-ben/benefits-review/"],
  },
  {
    file: "test/skill-llm-eval.eval.ts",
    tier: "llm-eval",
    touches: ["skills/"],
  },
];

export function affectedTests(changedFiles: string[], opts: { only?: "e2e" | "llm-eval"; all?: boolean } = {}): TestSpec[] {
  const specs = opts.only ? TEST_SPECS.filter((s) => s.tier === opts.only) : TEST_SPECS;
  if (opts.all) return specs;
  const globalHit = changedFiles.some((f) => GLOBAL_TOUCHFILES.some((g) => f.includes(g)));
  if (globalHit) return specs;
  return specs.filter((spec) => changedFiles.some((f) => spec.touches.some((t) => f.includes(t))));
}
