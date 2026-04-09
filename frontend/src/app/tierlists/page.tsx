import { TierlistCard } from "@/components/cards/tierlist-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getTierlists } from "@/lib/api";

interface TierlistsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function TierlistsPage({ searchParams }: TierlistsPageProps) {
  const params = await searchParams;
  const category = typeof params.category === "string" ? params.category : undefined;
  const mode = typeof params.mode === "string" ? params.mode : undefined;
  const server_region = typeof params.server_region === "string" ? params.server_region : undefined;

  const tierlists = await getTierlists({
    ...(category ? { category } : {}),
    ...(mode ? { mode } : {}),
    ...(server_region ? { server_region } : {}),
  });

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Meta Intelligence"
          title="Tier Lists"
          subtitle="Estrutura de listas para overall, beginner, endgame, sustain, nuke, arena, farm, bossing, support e equips por contexto."
        />
      </Shell>

      <Shell>
        <FilterBar title="Categorias (MVP)">
          <a href="/tierlists" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Todas
          </a>
          <a href="/tierlists?category=overall_units" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Overall Units
          </a>
          <a href="/tierlists?category=mode_specific_units" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Mode Specific
          </a>
          <a href="/tierlists?category=overall_equips" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Overall Equips
          </a>
          <a href="/tierlists?mode=CREST_PALACE" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Crest
          </a>
          <a href="/tierlists?mode=SUMMONERS_ROAD" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Road
          </a>
          <a href="/tierlists?server_region=GLOBAL" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Global
          </a>
          <a href="/tierlists?server_region=JP" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            JP
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <div className="grid gap-4 md:grid-cols-2">
          {tierlists.items.map((tier) => (
            <TierlistCard key={tier.id} tierlist={tier} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
