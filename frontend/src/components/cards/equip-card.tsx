import Link from "next/link";

import { EquipProfile } from "@/lib/types";

interface EquipCardProps {
  equip: EquipProfile;
}

export function EquipCard({ equip }: EquipCardProps) {
  return (
    <Link href={`/equips/${equip.slug}`} className="block rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:border-accent/40">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-base font-semibold text-text">{equip.name}</h3>
        <span className="text-xs text-accent">{equip.ranking_overall}</span>
      </div>
      <p className="mb-2 text-sm text-textSoft">
        {equip.slot_type} | {equip.category} | CD {equip.cooldown_seconds}s
      </p>
      <div className="flex flex-wrap gap-1">
        {equip.tags.slice(0, 5).map((tag) => (
          <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
