"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";

// Carries the latest check from /check to /result. Mirrored into
// sessionStorage so a page refresh on /result keeps the result.
const KEY = "claimcheck:last";
const Ctx = createContext(null);

export function ResultProvider({ children }) {
  const [entry, setEntry] = useState(null); // { claim, result }
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const saved = sessionStorage.getItem(KEY);
      if (saved) setEntry(JSON.parse(saved));
    } catch {}
    setReady(true);
  }, []);

  const save = useCallback((next) => {
    setEntry(next);
    try {
      sessionStorage.setItem(KEY, JSON.stringify(next));
    } catch {}
  }, []);

  return <Ctx.Provider value={{ entry, ready, save }}>{children}</Ctx.Provider>;
}

export const useResult = () => useContext(Ctx);
