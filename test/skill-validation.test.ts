import { describe, expect, test } from "bun:test";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
  PYTHON_STDLIB_ALLOWLIST,
  listSkillDirs,
  parseSkill,
  scriptImports,
} from "./helpers/skill-parser.ts";

const REPO_ROOT = join(import.meta.dir, "..");
const REQUIRED_SECTIONS = ["Method", "Output", "Rules"];

describe("skill-validation (Tier 1, free)", () => {
  const names = listSkillDirs(REPO_ROOT);

  test("at least one skill exists", () => {
    expect(names.length).toBeGreaterThan(0);
  });

  for (const name of names) {
    describe(name, () => {
      const skill = parseSkill(REPO_ROOT, name);

      test("has SKILL.md.tmpl with name + description frontmatter", () => {
        expect(skill.frontmatter.name).toBe(name);
        expect(skill.frontmatter.description).toBeTruthy();
      });

      test("description is written to trigger, not just to describe", () => {
        expect(skill.frontmatter.description!.length).toBeGreaterThan(40);
      });

      for (const section of REQUIRED_SECTIONS) {
        test(`has "## ${section}" section`, () => {
          const hasSection = skill.sections.some((s) => s === section || s.startsWith(`${section}:`));
          expect(hasSection).toBe(true);
        });
      }

      test("every referenced script exists and is stdlib-only", () => {
        for (const ref of skill.scriptRefs) {
          const scriptPath = join(skill.dir, ref);
          expect(existsSync(scriptPath)).toBe(true);
          const source = readFileSync(scriptPath, "utf-8");
          for (const mod of scriptImports(source)) {
            expect(PYTHON_STDLIB_ALLOWLIST.has(mod)).toBe(true);
          }
        }
      });

      test("has a generated SKILL.md", () => {
        expect(existsSync(skill.generatedPath)).toBe(true);
      });
    });
  }
});
