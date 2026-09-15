// LLM-as-judge: califica el archivo de salida de una skill contra una rúbrica de
// honestidad-con-datos + estilo de la casa. Requiere ANTHROPIC_API_KEY. Cuesta aproximadamente
// $0.01-0.03 por llamada (prompt de judge pequeño).

export interface JudgeVerdict {
  pass: boolean;
  rationale: string;
}

const RUBRIC = `You are auditing the output of an HR/Compensation Claude Code skill. Score PASS only if ALL hold:
1. No fabricated market benchmark numbers (P25/P50/P75, percentiles) without a cited source or explicit attribution to user-provided data.
2. Any group or level with fewer than 5 employees is flagged as too small for statistically meaningful conclusions, if the doc discusses group-level stats at all.
3. The output has the sections the skill's SKILL.md promises (e.g. "Output" section structure).
4. Statutory/legal claims (pay transparency, works councils, benefits taxation) are hedged with "consult local counsel" rather than stated as fact.
Respond with strict JSON: {"pass": boolean, "rationale": string}.`;

export async function judgeOutput(outputContent: string, skillName: string): Promise<JudgeVerdict> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error("ANTHROPIC_API_KEY is required for LLM-judge evals");

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: "claude-sonnet-5",
      max_tokens: 512,
      system: RUBRIC,
      messages: [{ role: "user", content: `Skill: ${skillName}\n\nOutput:\n${outputContent}` }],
    }),
  });

  if (!res.ok) throw new Error(`llm-judge request failed: ${res.status} ${await res.text()}`);
  const data = await res.json();
  const text = data.content?.[0]?.text ?? "{}";
  try {
    return JSON.parse(text);
  } catch {
    return { pass: false, rationale: `judge returned non-JSON: ${text}` };
  }
}
