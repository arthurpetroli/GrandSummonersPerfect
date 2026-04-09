import { CompCard } from "@/components/cards/comp-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getComps } from "@/lib/api";

interface CompsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function CompsPage({ searchParams }: CompsPageProps) {
  const params = await searchParams;
  const mode = typeof params.mode === "string" ? params.mode : undefined;
  const boss_id = typeof params.boss_id === "string" ? params.boss_id : undefined;
  const style = typeof params.style === "string" ? params.style : undefined;
  const beginner_friendly =
    typeof params.beginner_friendly === "string"
      ? params.beginner_friendly
      : undefined;

  const comps = await getComps({
    ...(mode ? { mode } : {}),
    ...(boss_id ? { boss_id } : {}),
    ...(style ? { style } : {}),
    ...(beginner_friendly ? { beginner_friendly } : {}),
  });

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Compositions"
          title="Comps recomendadas"
          subtitle="Acesse comps por modo, boss e estilo: sustain, nuke, auto-farm ou budget."
        />
      </Shell>

      <Shell>
        <FilterBar title="Modos (MVP)">
          <a href="/comps" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Todos
          </a>
          <a href="/comps?mode=CREST_PALACE" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Crest
          </a>
          <a href="/comps?mode=SUMMONERS_ROAD" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Road
          </a>
          <a href="/comps?mode=RAID" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Raid
          </a>
          <a href="/comps?style=SUSTAIN" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Sustain
          </a>
          <a href="/comps?style=NUKE" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Nuke
          </a>
          <a href="/comps?beginner_friendly=true" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Budget
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <div className="grid gap-4 md:grid-cols-2">
          {comps.items.map((comp) => (
            <CompCard key={comp.id} comp={comp} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
