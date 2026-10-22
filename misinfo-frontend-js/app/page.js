import Link from "next/link";

const AGENTS = [
  {
    name: "Agent 1: Researcher",
    text: "Turns your claim into a good search query, searches the web with DuckDuckGo, reads several pages in parallel, splits them into chunks and stores them in a ChromaDB vector database. If it already has relevant material cached, it reuses it.",
  },
  {
    name: "Agent 2: Retriever",
    text: "Pulls the most relevant chunks from ChromaDB using semantic search with MMR, so the evidence is varied rather than repetitive. A CrossEncoder then re-ranks it, and trusted domains such as Reuters, AP News, Nature, CDC and WHO are prioritised.",
  },
  {
    name: "Agent 3: Fact checker",
    text: "An LLM reads the best evidence and writes the verdict, a confidence score, a plain-language explanation and the sources it relied on.",
  },
];

const VERDICTS = [
  { label: "True", color: "text-verdict-true", text: "The evidence found supports the claim." },
  { label: "False", color: "text-verdict-false", text: "The evidence found contradicts the claim." },
  { label: "Misleading", color: "text-verdict-mixed", text: "Partly accurate, but leaves out context that changes its meaning." },
];

export default function About() {
  return (
    <div className="space-y-16">
      <section>
        <h1 className="font-display text-4xl font-extrabold tracking-tight sm:text-5xl">
          A claim goes in. A verdict and its evidence come out.
        </h1>
        <p className="mt-4 max-w-[60ch] text-lg leading-relaxed text-muted">
          Claim Check is an AI fact-checker. Instead of answering from memory, it searches the web, reads what it
          finds, ranks the evidence, and only then decides. Every verdict comes with the sources behind it so you can
          check the work yourself.
        </p>
        <Link
          href="/check"
          className="mt-6 inline-block rounded-md bg-ink px-5 py-2.5 font-display font-semibold text-sheet"
        >
          Check a claim
        </Link>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold">How it works</h2>
        <p className="mt-2 text-muted">Three agents run one after another, each handing its output to the next.</p>
        <ol className="mt-6 border-l-2 border-line">
          {AGENTS.map((a) => (
            <li key={a.name} className="relative pb-8 pl-6 last:pb-0">
              <span aria-hidden className="absolute -left-[7px] top-2 h-3 w-3 rounded-full bg-ink" />
              <h3 className="font-display text-lg font-bold">{a.name}</h3>
              <p className="mt-1 max-w-[62ch] text-lg leading-8">{a.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold">Reading a result</h2>
        <dl className="mt-4 divide-y divide-line rounded-md border border-line bg-sheet">
          {VERDICTS.map((v) => (
            <div key={v.label} className="flex flex-col gap-1 p-4 sm:flex-row sm:gap-6">
              <dt className={`w-32 shrink-0 font-display text-lg font-bold ${v.color}`}>{v.label}</dt>
              <dd>{v.text}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-4 max-w-[62ch] text-muted">
          The confidence score is the model&apos;s own estimate. It is not a guarantee. Open the sources and read them
          for anything that matters.
        </p>
      </section>
    </div>
  );
}
