import Link from "next/link";

import { Guide } from "@/lib/types";

interface GuideCardProps {
  guide: Guide;
}

export function GuideCard({ guide }: GuideCardProps) {
  return (
    <Link href={`/guides/${guide.slug}`} className="rounded-xl border border-line bg-panel p-4 shadow-glow transition hover:border-accent/50">
      <h3 className="text-base font-semibold text-text">{guide.title}</h3>
      <p className="mt-2 text-sm text-textSoft">{guide.excerpt}</p>
      <div className="mt-3 flex flex-wrap gap-1">
        {guide.tags.map((tag) => (
          <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
