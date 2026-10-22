"use client";
import { useEffect, useState } from "react";

// Mirrors the backend's three agents. Timing is indicative only: the API
// returns once, so the active step is an estimate, not a live signal.
const STEPS = [
  { label: "Searching and reading sources", after: 0 },
  { label: "Ranking the evidence", after: 12000 },
  { label: "Writing the verdict", after: 22000 },
];

export default function PipelineProgress() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const timers = STEPS.map((s, i) => setTimeout(() => setActive(i), s.after));
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <ol aria-live="polite" className="space-y-2 rounded-md border border-line bg-sheet p-5">
      {STEPS.map((s, i) => (
        <li
          key={s.label}
          className={`flex items-center gap-3 font-display ${
            i < active ? "text-muted" : i === active ? "font-semibold text-ink" : "text-muted/50"
          }`}
        >
          <span
            aria-hidden
            className={`h-2.5 w-2.5 rounded-full ${
              i < active ? "bg-verdict-true" : i === active ? "animate-pulse bg-ink" : "bg-line"
            }`}
          />
          {s.label}
        </li>
      ))}
    </ol>
  );
}
