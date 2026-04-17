import { TierlistCard } from "@/components/cards/tierlist-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getTierlists } from "@/lib/api";

interface TierlistsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

function filterPill(active: boolean): string {
  if (active) {
    return "rounded-md border border-accent/60 bg-accent/10 px-3 py-1 text-xs font-medium text-accent";
  }
  return "rounded-md border border-line px-3 py-1 text-xs text-textSoft transition hover:border-accent/30 hover:text-text";
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

  const sortedTierlists = [...tierlists.items].sort((left, right) => left.title.localeCompare(right.title));

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
        <FilterBar title="Filtros de Tierlist">
          <a href="/tierlists" className={filterPill(!category && !mode && !server_region)}>
            Todas
          </a>
          <a href="/tierlists?category=overall_units" className={filterPill(category === "overall_units")}>
            Overall Units
          </a>
          <a href="/tierlists?category=beginner_units" className={filterPill(category === "beginner_units")}>
            Beginner
          </a>
          <a href="/tierlists?category=endgame_units" className={filterPill(category === "endgame_units")}>
            Endgame
          </a>
          <a href="/tierlists?category=sustain_units" className={filterPill(category === "sustain_units")}>
            Sustain
          </a>
          <a href="/tierlists?category=nuke_units" className={filterPill(category === "nuke_units")}>
            Nuke
          </a>
          <a href="/tierlists?category=arena_units" className={filterPill(category === "arena_units")}>
            Arena Units
          </a>
          <a href="/tierlists?category=farming_units" className={filterPill(category === "farming_units")}>
            Farming
          </a>
          <a href="/tierlists?category=bossing_units" className={filterPill(category === "bossing_units")}>
            Bossing
          </a>
          <a href="/tierlists?category=support_units" className={filterPill(category === "support_units")}>
            Support
          </a>
          <a href="/tierlists?category=mode_specific_units" className={filterPill(category === "mode_specific_units")}>
            Mode Specific
          </a>
          <a href="/tierlists?category=overall_equips" className={filterPill(category === "overall_equips")}>
            Overall Equips
          </a>
          <a href="/tierlists?mode=CREST_PALACE" className={filterPill(mode === "CREST_PALACE")}>
            Crest
          </a>
          <a href="/tierlists?mode=SUMMONERS_ROAD" className={filterPill(mode === "SUMMONERS_ROAD")}>
            Road
          </a>
          <a href="/tierlists?mode=ARENA" className={filterPill(mode === "ARENA")}>
            Arena
          </a>
          <a href="/tierlists?server_region=GLOBAL" className={filterPill(server_region === "GLOBAL")}>
            Global
          </a>
          <a href="/tierlists?server_region=JP" className={filterPill(server_region === "JP")}>
            JP
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <div className="mb-3 text-xs text-textSoft">{sortedTierlists.length} tierlists encontradas</div>
        <div className="grid gap-4 md:grid-cols-2">
          {sortedTierlists.map((tier) => (
            <TierlistCard key={tier.id} tierlist={tier} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
