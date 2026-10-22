"use client";
import Link from "next/link";
import { useResult } from "@/lib/ResultContext";
import { hostOf } from "@/lib/normalize";
import { VERDICT_STYLE, isTrusted } from "@/lib/verdict";

export default function Result() {
  const { entry, ready } = useResult();

  if (!ready) return null;

  if (!entry) {
    return (
      <div>
        <h1 className="font-display text-4xl font-extrabold tracking-tight">No result yet</h1>
        <p className="mb-6 mt-3 text-lg text-muted">Check a claim first and its full breakdown will appear here.</p>
        <Link href="/check" className="inline-block rounded-md bg-ink px-5 py-2.5 font-display font-semibold text-sheet">
          Check a claim
        </Link>
      </div>
    );
  }

  const { claim, result } = entry;
  const s = VERDICT_STYLE[result.verdict] ?? VERDICT_STYLE.Unverified;
  const pct = Math.round(result.confidence * 100);
  const trustedCount = result.sources.filter((x) => isTrusted(x.url)).length;
  const siteCount = new Set(result.sources.map((x) => hostOf(x.url))).size;

  return (
    <article className="space-y-10">
      <section className={`rounded-md border-l-4 bg-sheet p-6 ${s.border}`}>
        <p className="font-display text-sm text-muted">You asked</p>
        <p className="mt-1 text-lg leading-snug">{claim}</p>

        <h1 className={`mt-6 font-display text-6xl font-extrabold tracking-tight sm:text-7xl ${s.text}`}>
          {result.verdict}
        </h1>
        <p className="mt-1 text-muted">{s.blurb}</p>

        <div className="mt-6">
          <div className="flex justify-between font-display text-sm">
            <span className="text-muted">Confidence</span>
            <span className="font-semibold">{pct}%</span>
          </div>
          <div
            role="meter"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={pct}
            aria-label="Confidence"
            className="relative mt-1 h-3 rounded-sm bg-line/60"
          >
            <div className={`gauge-fill h-full rounded-sm ${s.bar}`} style={{ width: `${pct}%` }} />
            {[25, 50, 75].map((t) => (
              <span key={t} aria-hidden className="absolute top-0 h-full w-px bg-sheet" style={{ left: `${t}%` }} />
            ))}
          </div>
          <p className="mt-2 text-sm text-muted">This is the model&apos;s own estimate, not a guarantee.</p>
        </div>
      </section>

      {result.explanation && (
        <section>
          <h2 className="font-display text-2xl font-bold">Why this verdict</h2>
          <p className="mt-3 max-w-[68ch] whitespace-pre-line text-lg leading-8">{result.explanation}</p>
        </section>
      )}

      <section>
        <h2 className="font-display text-2xl font-bold">Evidence at a glance</h2>
        <dl className="mt-3 grid grid-cols-3 divide-x divide-line rounded-md border border-line bg-sheet text-center">
          {[
            ["Sources cited", result.sources.length],
            ["Different sites", siteCount],
            ["Trusted domains", trustedCount],
          ].map(([label, n]) => (
            <div key={label} className="p-4">
              <dd className="font-display text-3xl font-extrabold">{n}</dd>
              <dt className="text-sm text-muted">{label}</dt>
            </div>
          ))}
        </dl>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold">Sources</h2>
        {result.sources.length === 0 ? (
          <p className="mt-2 text-muted">The backend returned no sources for this claim.</p>
        ) : (
          <ul className="mt-3 divide-y divide-line rounded-md border border-line bg-sheet">
            {result.sources.map((src, i) => (
              <li key={`${src.url}-${i}`} className="p-5">
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-display text-lg font-semibold underline-offset-4 hover:underline"
                >
                  {src.title}
                </a>
                <div className="mt-0.5 flex flex-wrap items-center gap-2 text-sm text-muted">
                  <span>{hostOf(src.url)}</span>
                  {isTrusted(src.url) && (
                    <span className="rounded-full border border-verdict-true px-2 text-verdict-true">Trusted domain</span>
                  )}
                </div>
                {src.snippet && <p className="mt-3 max-w-[68ch] leading-7 text-muted">{src.snippet}</p>}
              </li>
            ))}
          </ul>
        )}
      </section>

      <Link href="/check" className="inline-block rounded-md bg-ink px-5 py-2.5 font-display font-semibold text-sheet">
        Check another claim
      </Link>
    </article>
  );
}
