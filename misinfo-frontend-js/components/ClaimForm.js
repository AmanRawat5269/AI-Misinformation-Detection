"use client";

const EXAMPLES = [
  "Drinking hot water cures COVID-19",
  "The Great Wall of China is visible from space",
  "India became the most populous country in 2023",
];

export default function ClaimForm({ value, onChange, onSubmit, loading }) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!loading) onSubmit();
      }}
    >
      <label htmlFor="claim" className="font-display text-sm font-semibold text-muted">
        Claim or news headline
      </label>
      <textarea
        id="claim"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && !loading) onSubmit();
        }}
        rows={4}
        maxLength={600}
        placeholder="Paste a statement you want verified"
        className="mt-2 w-full resize-y rounded-md border border-line bg-sheet p-4 text-lg leading-relaxed placeholder:text-muted/60"
      />
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => onChange(ex)}
              className="rounded-full border border-line px-3 py-1 text-sm text-muted hover:border-ink hover:text-ink"
            >
              {ex}
            </button>
          ))}
        </div>
        <button
          type="submit"
          disabled={loading || value.trim().length < 5}
          className="rounded-md bg-ink px-5 py-2.5 font-display font-semibold text-sheet disabled:opacity-40"
        >
          {loading ? "Checking…" : "Check claim"}
        </button>
      </div>
    </form>
  );
}
