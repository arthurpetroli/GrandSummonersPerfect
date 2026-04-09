import type { Metadata } from "next";
import { Space_Grotesk, Sora } from "next/font/google";

import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import "@/styles/globals.css";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" });
const sora = Sora({ subsets: ["latin"], variable: "--font-sora" });

export const metadata: Metadata = {
  metadataBase: new URL("https://gscompanion.example.com"),
  title: {
    default: "GS Companion | Grand Summoners",
    template: "%s | GS Companion",
  },
  description: "Companion premium para Grand Summoners com Boss Solver, Team Builder, tier lists contextuais e database inteligente.",
  openGraph: {
    title: "GS Companion",
    description: "Decisao pratica para montar comps, resolver boss e evoluir sem perder recursos.",
    type: "website",
  },
  alternates: {
    canonical: "/",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${spaceGrotesk.variable} ${sora.variable}`}>
      <body className="bg-bg text-text antialiased">
        <SiteHeader />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
