import { EquipCard } from "@/components/cards/equip-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getEquips } from "@/lib/api";

interface EquipsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function EquipsPage({ searchParams }: EquipsPageProps) {
  const params = await searchParams;
  const query = {
    ...(typeof params.server_region === "string" ? { server_region: params.server_region } : {}),
    ...(typeof params.slot_type === "string" ? { slot_type: params.slot_type } : {}),
    ...(typeof params.category === "string" ? { category: params.category } : {}),
    ...(typeof params.max_cooldown === "string" ? { max_cooldown: params.max_cooldown } : {}),
    ...(typeof params.min_cooldown === "string" ? { min_cooldown: params.min_cooldown } : {}),
    ...(typeof params.tier === "string" ? { tier: params.tier } : {}),
    ...(typeof params.context === "string" ? { context: params.context } : {}),
    ...(typeof params.tag === "string" ? { tag: params.tag } : {}),
    ...(typeof params.tags_any === "string" ? { tags_any: params.tags_any } : {}),
  };

  const equips = await getEquips(query);

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Database"
          title="Equips"
          subtitle="Filtros por slot, cooldown, utilidade, tier geral e tier por contexto (sustain/nuke/farm/arena)."
        />
      </Shell>

      <Shell>
        <FilterBar title="Filtros rapidos (MVP)">
          <a href="/equips" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Todos
          </a>
          <a href="/equips?tags_any=cleanse,barrier" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Cleanse/Barreira
          </a>
          <a href="/equips?tags_any=art_gen,crit" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Art Gen/Crit
          </a>
          <a href="/equips?context=sustain&tier=SSS" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Sustain SSS
          </a>
          <a href="/equips?context=nuke&tier=SSS" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Nuke SSS
          </a>
          <a href="/equips?max_cooldown=30" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            CD &lt;= 30
          </a>
          <a href="/equips?server_region=GLOBAL" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Global
          </a>
          <a href="/equips?server_region=JP" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            JP
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <p className="mb-3 text-xs uppercase tracking-[0.2em] text-textSoft">{equips.count} resultados</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {equips.items.map((equip) => (
            <EquipCard key={equip.id} equip={equip} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
