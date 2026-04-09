import { UnitCard } from "@/components/cards/unit-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getUnits } from "@/lib/api";

interface UnitsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function UnitsPage({ searchParams }: UnitsPageProps) {
  const params = await searchParams;
  const query = {
    ...(typeof params.server_region === "string" ? { server_region: params.server_region } : {}),
    ...(typeof params.mode === "string" ? { mode: params.mode } : {}),
    ...(typeof params.role === "string" ? { role: params.role } : {}),
    ...(typeof params.element === "string" ? { element: params.element } : {}),
    ...(typeof params.race === "string" ? { race: params.race } : {}),
    ...(typeof params.damage_type === "string" ? { damage_type: params.damage_type } : {}),
    ...(typeof params.slot === "string" ? { slot: params.slot } : {}),
    ...(typeof params.tier === "string" ? { tier: params.tier } : {}),
    ...(typeof params.tierlist_slug === "string" ? { tierlist_slug: params.tierlist_slug } : {}),
    ...(typeof params.focus === "string" ? { focus: params.focus } : {}),
    ...(typeof params.min_value === "string" ? { min_value: params.min_value } : {}),
    ...(typeof params.tag === "string" ? { tag: params.tag } : {}),
    ...(typeof params.tags_any === "string" ? { tags_any: params.tags_any } : {}),
  };

  const units = await getUnits(query);

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Database"
          title="Units"
          subtitle="Filtros completos para contexto real: modo, role, dano, slots, utilidade, tier e regiao."
        />
      </Shell>

      <Shell>
        <FilterBar title="Filtros rapidos (MVP)">
          <a href="/units" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Todos
          </a>
          <a href="/units?mode=SUMMONERS_ROAD" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Summoners Road
          </a>
          <a href="/units?focus=sustain&min_value=90" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Sustain 90+
          </a>
          <a href="/units?focus=nuke&min_value=90" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Nuke 90+
          </a>
          <a href="/units?tags_any=cleanse,mitigation" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Cleanse/Mitigation
          </a>
          <a href="/units?tags_any=art_gen,crit" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Art Gen/Crit
          </a>
          <a href="/units?server_region=GLOBAL" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Global
          </a>
          <a href="/units?server_region=JP" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            JP
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <p className="mb-3 text-xs uppercase tracking-[0.2em] text-textSoft">{units.count} resultados</p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {units.items.map((unit) => (
            <UnitCard key={unit.id} unit={unit} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
