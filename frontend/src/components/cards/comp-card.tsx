import Link from "next/link";

import { TeamComp } from "@/lib/types";

interface CompCardProps {
  comp: TeamComp;
}

export function CompCard({ comp }: CompCardProps) {
  return (
    <Link href={`/comps/${comp.slug}`} className="block rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:border-accent/40">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-base font-semibold text-text">{comp.name}</h3>
        <span className="rounded bg-bgSoft px-2 py-1 text-[10px] uppercase tracking-wide text-accent">{comp.style}</span>
      </div>
      <p className="text-sm text-textSoft">{comp.summary}</p>
      <ul className="mt-3 space-y-1 text-xs text-textSoft">
        {comp.why_it_works.slice(0, 2).map((reason) => (
          <li key={reason}>- {reason}</li>
        ))}
      </ul>
    </Link>
  );
}
