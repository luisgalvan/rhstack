// Lanza una CLI de IA en modo print (`claude -p "/<skill> ..."` o, con
// RHSTACK_E2E_BACKEND=agy, `agy -p` apuntando a un modelo Gemini) en un directorio temporal
// poblado con el dataset sintético, luego reporta qué archivos produjo la sesión para que las
// pruebas puedan verificar la forma de la salida.
//
// El backend es intercambiable porque el contrato de la prueba (un prompt de skill entra, unos
// archivos de salida con nombres esperados salen) no depende de qué modelo interpretó el
// SKILL.md: eso es justo lo que valida "¿corren las skills en Gemini?".
import { cpSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

export type SessionBackend = "claude" | "agy";

const DEFAULT_AGY_MODEL = "gemini-3.5-flash-high";

export interface SessionResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  filesCreated: string[];
  cwd: string;
  backend: SessionBackend;
}

export function currentBackend(): SessionBackend {
  return process.env.RHSTACK_E2E_BACKEND === "agy" ? "agy" : "claude";
}

// La clave de Anthropic solo es obligatoria cuando el backend habla con la API de Claude
// directamente (backend "claude", o cualquier eval de tipo llm-eval que use el juez LLM).
export function requiresAnthropicKey(backend: SessionBackend = currentBackend()): boolean {
  return backend === "claude";
}

function commandFor(backend: SessionBackend, prompt: string, cwd: string): string[] {
  if (backend === "agy") {
    const model = process.env.RHSTACK_E2E_MODEL || DEFAULT_AGY_MODEL;
    // agy (Antigravity CLI) trata el directorio de trabajo como un workspace explícito, no
    // implícito: sin --add-dir escribe los artefactos bajo ~/.gemini/antigravity-cli/{scratch,brain}/
    // en vez del cwd de la sesión, así que cualquier verificación basada en archivos creados fallaría.
    return ["agy", "-p", prompt, "--model", model, "--output-format", "text", "--dangerously-skip-permissions", "--add-dir", cwd];
  }
  return ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"];
}

export function runSkillSession(prompt: string, opts: { seedExamples?: boolean; backend?: SessionBackend } = {}): SessionResult {
  const backend = opts.backend ?? currentBackend();
  const cwd = mkdtempSync(join(tmpdir(), "rhstack-e2e-"));
  if (opts.seedExamples !== false) {
    cpSync(join(import.meta.dir, "..", "..", "examples"), join(cwd, "examples"), { recursive: true });
  }
  const before = new Set(readdirSync(cwd));

  const proc = Bun.spawnSync(commandFor(backend, prompt, cwd), {
    cwd,
    stdout: "pipe",
    stderr: "pipe",
  });

  const after = readdirSync(cwd);
  const filesCreated = after.filter((f) => !before.has(f));

  const result: SessionResult = {
    stdout: proc.stdout.toString(),
    stderr: proc.stderr.toString(),
    exitCode: proc.exitCode ?? 1,
    filesCreated,
    cwd,
    backend,
  };
  return result;
}

export function cleanupSession(result: SessionResult) {
  rmSync(result.cwd, { recursive: true, force: true });
}
