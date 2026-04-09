import Link from "next/link";

const NAV_ITEMS = [
  { href: "/units", label: "Units" },
  { href: "/equips", label: "Equips" },
  { href: "/tierlists", label: "Tier Lists" },
  { href: "/bosses", label: "Boss Solver" },
  { href: "/comps", label: "Comps" },
  { href: "/team-builder", label: "Team Builder" },
  { href: "/modes", label: "Modes" },
  { href: "/ai-presets", label: "AI Presets" },
  { href: "/progression", label: "Progression" },
  { href: "/guides", label: "Guides" },
  { href: "/admin", label: "Admin" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 border-b border-line/80 bg-bg/85 backdrop-blur-md">
      <div className="container-shell flex h-16 items-center justify-between">
        <Link href="/" className="text-sm font-semibold tracking-wide text-text md:text-base">
          GS Companion
        </Link>
        <nav className="hidden items-center gap-4 md:flex">
          {NAV_ITEMS.map((item) => (
            <Link key={item.href} href={item.href} className="text-sm text-textSoft transition hover:text-text">
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="rounded-md border border-line bg-panel px-2 py-1 text-xs text-textSoft">Global / JP</div>
      </div>
    </header>
  );
}
