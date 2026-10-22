import { Bricolage_Grotesque, Source_Serif_4 } from "next/font/google";
import "./globals.css";
import Nav from "@/components/Nav";
import { ResultProvider } from "@/lib/ResultContext";

const display = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-display" });
const body = Source_Serif_4({ subsets: ["latin"], variable: "--font-body" });

export const metadata = {
  title: "Claim Check: AI misinformation detection",
  description: "Check a claim against trusted sources and get a verdict with citations.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${display.variable} ${body.variable}`}>
      <body className="min-h-screen">
        <ResultProvider>
          <Nav />
          <main className="mx-auto max-w-3xl px-5 pb-20 pt-10 sm:pt-16">{children}</main>
        </ResultProvider>
      </body>
    </html>
  );
}
