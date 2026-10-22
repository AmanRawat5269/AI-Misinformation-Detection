/**
 * The only place that knows the backend's response shape.
 * If your FastAPI response uses different field names, change them here.
 */
export function normalize(input) {
  const raw = input?.result ?? input ?? {};

  const v = String(raw.verdict ?? "").toLowerCase();
  const verdict = v.includes("mislead")
    ? "Misleading"
    : v.startsWith("true")
      ? "True"
      : v.startsWith("false")
        ? "False"
        : "Unverified";

  let confidence = Number(raw.confidence ?? raw.confidence_score ?? 0);
  if (!Number.isFinite(confidence)) confidence = 0;
  if (confidence > 1) confidence /= 100;
  confidence = Math.min(1, Math.max(0, confidence));

  const list = raw.sources ?? raw.citations ?? [];
  const sources = list
    .map((s) => {
      if (typeof s === "string") return { title: hostOf(s), url: s };
      const url = String(s?.url ?? s?.source ?? s?.link ?? "");
      return {
        title: String(s?.title ?? hostOf(url)),
        url,
        snippet: s?.snippet ?? s?.content ?? undefined,
      };
    })
    .filter((s) => s.url);

  return {
    verdict,
    confidence,
    explanation: String(raw.explanation ?? raw.reasoning ?? ""),
    sources,
  };
}

export function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}
