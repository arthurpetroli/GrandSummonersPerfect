import Link from "next/link";

import { StatChip } from "@/components/cards/stat-chip";
import { UnitProfile } from "@/lib/types";

interface UnitCardProps {
  unit: UnitProfile;
}

export function UnitCard({ unit }: UnitCardProps) {
  return (
    <Link
      href={`/units/${unit.slug}`}
      className="group rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:-translate-y-0.5 hover:border-accent/40"
    >
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-base font-semibold text-text">{unit.name}</h3>
        <span className="rounded bg-bgSoft px-2 py-1 text-[10px] uppercase tracking-wide text-textSoft">{unit.server_region}</span>
      </div>
      <div className="mb-3 flex flex-wrap gap-2">
        <StatChip label="Role" value={unit.role} />
        <StatChip label="Element" value={unit.element} />
        <StatChip label="Rarity" value={`*${unit.rarity}`} />
      </div>
      <p className="line-clamp-2 text-sm text-textSoft">{unit.strengths.join(" | ")}</p>
      <div className="mt-3 flex flex-wrap gap-1">
        {unit.tags.slice(0, 4).map((tag) => (
          <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
