import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { listSkillDirs, parseSkill } from "./helpers/skill-parser.ts";
import { cursorMirrorPath, render } from "../scripts/gen-skill-docs.ts";

const REPO_ROOT = join(import.meta.dir, "..");

describe("gen-skill-docs drift check (Tier 1, free)", () => {
  for (const name of listSkillDirs(REPO_ROOT)) {
    test(`${name}: generated SKILL.md matches SKILL.md.tmpl`, () => {
      const skill = parseSkill(REPO_ROOT, name);
      const templateRaw = readFileSync(skill.templatePath, "utf-8");
      const expected = render(templateRaw);
      const actual = readFileSync(skill.generatedPath, "utf-8");
      expect(actual).toBe(expected);
    });

    test(`${name}: .cursor/skills mirror matches SKILL.md.tmpl`, () => {
      const skill = parseSkill(REPO_ROOT, name);
      const templateRaw = readFileSync(skill.templatePath, "utf-8");
      const expected = render(templateRaw);
      const actual = readFileSync(cursorMirrorPath(REPO_ROOT, name), "utf-8");
      expect(actual).toBe(expected);
    });
  }
});
