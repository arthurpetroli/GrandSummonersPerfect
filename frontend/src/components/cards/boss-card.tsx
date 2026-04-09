import Link from "next/link";

import { BossProfile } from "@/lib/types";

interface BossCardProps {
  boss: BossProfile;
}

export function BossCard({ boss }: BossCardProps) {
  return (
    <Link href={`/bosses/${boss.slug}`} className="rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:border-accent/50">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-base font-semibold text-text">{boss.name}</h3>
        <span className="text-xs text-textSoft">{boss.difficulty}</span>
      </div>
      <p className="text-sm text-textSoft">{boss.stage_name}</p>
      <p className="mt-2 line-clamp-2 text-sm text-textSoft">{boss.overview}</p>
      <div className="mt-3 flex flex-wrap gap-1">
        {boss.required_tags.map((tag) => (
          <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
