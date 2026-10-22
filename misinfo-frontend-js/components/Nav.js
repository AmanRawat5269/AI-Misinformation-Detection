"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "About" },
  { href: "/check", label: "Check a claim" },
  { href: "/result", label: "Result" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <header className="border-b border-line">
      <nav aria-label="Main" className="mx-auto flex max-w-3xl items-center justify-between px-5 py-4">
        <Link href="/" className="font-display text-lg font-extrabold tracking-tight">
          Claim Check
        </Link>
        <ul className="flex gap-5 font-display text-sm font-semibold">
          {LINKS.map((l) => {
            const active = pathname === l.href;
            return (
              <li key={l.href}>
                <Link
                  href={l.href}
                  aria-current={active ? "page" : undefined}
                  className={`border-b-2 pb-1 ${active ? "border-ink text-ink" : "border-transparent text-muted hover:text-ink"}`}
                >
                  {l.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}
