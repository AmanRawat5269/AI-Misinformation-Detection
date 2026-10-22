"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import ClaimForm from "@/components/ClaimForm";
import PipelineProgress from "@/components/PipelineProgress";
import { useResult } from "@/lib/ResultContext";

export default function Check() {
  const router = useRouter();
  const { save } = useResult();
  const [claim, setClaim] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function run() {
    const text = claim.trim();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ claim: text }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Something went wrong.");
      save({ claim: text, result: data });
      router.push("/result");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="font-display text-4xl font-extrabold tracking-tight">Check a claim</h1>
      <p className="mb-8 mt-3 max-w-[60ch] text-lg leading-relaxed text-muted">
        Enter one statement at a time. Checking takes a short while because the agents read live sources.
      </p>

      <ClaimForm value={claim} onChange={setClaim} onSubmit={run} loading={loading} />

      <div className="mt-10">
        {loading && <PipelineProgress />}
        {error && (
          <div role="alert" className="rounded-md border border-verdict-false bg-sheet p-5">
            <p className="font-display font-semibold text-verdict-false">The check failed</p>
            <p className="mt-1">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
