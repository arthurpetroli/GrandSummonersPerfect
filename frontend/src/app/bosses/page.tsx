import { BossCard } from "@/components/cards/boss-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getBosses } from "@/lib/api";

interface BossesPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function BossesPage({ searchParams }: BossesPageProps) {
  const params = await searchParams;
  const mode = typeof params.mode === "string" ? params.mode : undefined;
  const required_tag = typeof params.required_tag === "string" ? params.required_tag : undefined;
  const required_tags_any = typeof params.required_tags_any === "string" ? params.required_tags_any : undefined;

  const bosses = await getBosses({
    ...(mode ? { mode } : {}),
    ...(required_tag ? { required_tag } : {}),
    ...(required_tags_any ? { required_tags_any } : {}),
  });

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Boss Solver"
          title="Bosses e Stages"
          subtitle="Cada boss com checks de mecanica, utilidades obrigatorias e comps recomendadas com substitutes."
        />
      </Shell>

      <Shell>
        <FilterBar title="Modos">
          <a href="/bosses" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Todos
          </a>
          <a href="/bosses?mode=CREST_PALACE" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Crest Palace
          </a>
          <a href="/bosses?mode=SUMMONERS_ROAD" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Summoners Road
          </a>
          <a href="/bosses?mode=RAID" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Raid
          </a>
          <a href="/bosses?required_tag=accuracy" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Accuracy check
          </a>
          <a href="/bosses?required_tags_any=cleanse,mitigation" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Cleanse/Mitigation
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {bosses.items.map((boss) => (
            <BossCard key={boss.id} boss={boss} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
