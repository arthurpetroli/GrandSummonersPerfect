import Link from "next/link";

import { Tierlist } from "@/lib/types";

interface TierlistCardProps {
  tierlist: Tierlist;
}

const CATEGORY_LABELS: Record<string, string> = {
  overall_units: "Overall Units",
  beginner_units: "Beginner",
  endgame_units: "Endgame",
  sustain_units: "Sustain",
  nuke_units: "Nuke",
  arena_units: "Arena",
  farming_units: "Farming",
  bossing_units: "Bossing",
  support_units: "Support",
  mode_specific_units: "Mode Specific",
  overall_equips: "Equips",
};

const MODE_LABELS: Record<string, string> = {
  STORY: "Story",
  ARENA: "Arena",
  DUNGEON_OF_TRIALS: "Trials",
  CREST_PALACE: "Crest",
  SUMMONERS_ROAD: "Road",
  MAGICAL_MINES: "Mines",
  GRAND_CRUSADE: "Crusade",
  RAID: "Raid",
  COLLAB: "Collab",
};

export function TierlistCard({ tierlist }: TierlistCardProps) {
  const tierCounts = tierlist.entries.reduce<Record<string, number>>((acc, entry) => {
    const grade = String(entry.tier).toUpperCase();
    acc[grade] = (acc[grade] ?? 0) + 1;
    return acc;
  }, {});

  const topTierPreview = ["SSS", "SS", "S", "A"]
    .filter((grade) => (tierCounts[grade] ?? 0) > 0)
    .slice(0, 3)
    .map((grade) => `${grade} ${tierCounts[grade]}`)
    .join(" | ");

  const categoryLabel = CATEGORY_LABELS[tierlist.category] ?? tierlist.category;
  const modeLabel = tierlist.mode ? MODE_LABELS[tierlist.mode] ?? tierlist.mode : null;

  return (
    <Link
      href={`/tierlists/${tierlist.slug}`}
      className="group rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:-translate-y-[1px] hover:border-accent/50"
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full border border-accent/40 bg-accent/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-accent">
          {categoryLabel}
        </span>
        {modeLabel ? (
          <span className="rounded-full border border-line bg-bgSoft px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-textSoft">
            {modeLabel}
          </span>
        ) : null}
        {tierlist.server_region ? (
          <span className="rounded-full border border-line bg-bgSoft px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-textSoft">
            {tierlist.server_region}
          </span>
        ) : null}
      </div>

      <h3 className="mt-3 text-base font-semibold text-text transition group-hover:text-accent">{tierlist.title}</h3>

      <div className="mt-2 flex items-center justify-between text-xs text-textSoft">
        <span>v{tierlist.version}</span>
        <span>{tierlist.entries.length} entries</span>
      </div>

      <p className="mt-3 text-xs text-textSoft">
        {topTierPreview || "Tier distribution available in detailed view."}
      </p>
    </Link>
  );
}
