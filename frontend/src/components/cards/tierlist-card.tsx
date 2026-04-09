import Link from "next/link";

import { Tierlist } from "@/lib/types";

interface TierlistCardProps {
  tierlist: Tierlist;
}

export function TierlistCard({ tierlist }: TierlistCardProps) {
  return (
    <Link href={`/tierlists/${tierlist.slug}`} className="rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:border-accent/50">
      <h3 className="text-base font-semibold text-text">{tierlist.title}</h3>
      <p className="mt-1 text-sm text-textSoft">
        {tierlist.category} | v{tierlist.version}
      </p>
      <p className="mt-3 text-xs text-textSoft">{tierlist.entries.length} evaluated entries with contextual explanation.</p>
    </Link>
  );
}
