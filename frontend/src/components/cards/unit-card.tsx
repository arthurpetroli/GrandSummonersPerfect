import Link from "next/link";
import Image from "next/image";

import { StatChip } from "@/components/cards/stat-chip";
import { UnitProfile } from "@/lib/types";

interface UnitCardProps {
  unit: UnitProfile;
}

function isExternalUnit(unit: UnitProfile): boolean {
  const refs = unit.source_refs || [];
  const tags = unit.tags || [];
  return tags.includes("external_source") || refs.some((ref) => ref.includes("grandsummoners.info"));
}

export function UnitCard({ unit }: UnitCardProps) {
  const external = isExternalUnit(unit);

  return (
    <Link
      href={`/units/${unit.slug}`}
      className="group overflow-hidden rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:-translate-y-0.5 hover:border-accent/40"
    >
      <div className="relative mb-3 h-40 w-full overflow-hidden rounded-lg border border-line bg-bgSoft">
        <Image
          src={unit.image_thumb_url || unit.image_url || "/images/placeholders/unit-placeholder.svg"}
          alt={unit.name}
          fill
          className="object-cover transition duration-300 group-hover:scale-[1.03]"
          sizes="(max-width: 768px) 100vw, 33vw"
          unoptimized
        />
      </div>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-base font-semibold text-text">{unit.name}</h3>
        <div className="flex items-center gap-1">
          <span className="rounded bg-bgSoft px-2 py-1 text-[10px] uppercase tracking-wide text-textSoft">{unit.server_region}</span>
          {external ? (
            <span className="rounded border border-accent/40 bg-accent/10 px-2 py-1 text-[10px] uppercase tracking-wide text-accent">
              External
            </span>
          ) : null}
        </div>
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
