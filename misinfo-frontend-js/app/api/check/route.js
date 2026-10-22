import { NextResponse } from "next/server";
import { normalize } from "@/lib/normalize";

// The RAG pipeline scrapes pages and calls LLMs, so it can be slow.
export const maxDuration = 120;

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";
const CHECK_PATH = process.env.BACKEND_CHECK_PATH ?? "/check";

export async function POST(req) {
  const body = await req.json().catch(() => null);
  const claim = typeof body?.claim === "string" ? body.claim.trim() : "";

  if (claim.length < 5) {
    return NextResponse.json({ error: "Enter a claim of at least a few words." }, { status: 400 });
  }

  try {
    const res = await fetch(`${BACKEND}${CHECK_PATH}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim }),
      cache: "no-store",
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: `The backend answered with status ${res.status}. Check the route in .env.local.` },
        { status: 502 }
      );
    }
    return NextResponse.json(normalize(await res.json()));
  } catch {
    return NextResponse.json(
      { error: `Can't reach the backend at ${BACKEND}. Is docker compose running?` },
      { status: 502 }
    );
  }
}
