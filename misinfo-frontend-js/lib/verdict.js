import { hostOf } from "./normalize";

export const VERDICT_STYLE = {
  True: { text: "text-verdict-true", bar: "bg-verdict-true", border: "border-verdict-true", blurb: "Supported by the evidence found." },
  False: { text: "text-verdict-false", bar: "bg-verdict-false", border: "border-verdict-false", blurb: "Contradicted by the evidence found." },
  Misleading: { text: "text-verdict-mixed", bar: "bg-verdict-mixed", border: "border-verdict-mixed", blurb: "Partly accurate, but missing context." },
  Unverified: { text: "text-verdict-none", bar: "bg-verdict-none", border: "border-verdict-none", blurb: "Not enough evidence to decide." },
};

// Domains the backend prioritises (from the project README)
const TRUSTED = ["reuters.com", "apnews.com", "nature.com", "cdc.gov", "who.int"];
export const isTrusted = (url) => TRUSTED.some((d) => hostOf(url).endsWith(d));
