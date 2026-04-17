import Link from "next/link";

import { UnitCard } from "@/components/cards/unit-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { UnitsSearchForm } from "@/components/units/units-search-form";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getUnits } from "@/lib/api";

interface UnitsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

type SearchParamsRecord = Record<string, string | string[] | undefined>;

const ADVANCED_FILTER_KEYS = [
  "server_region",
  "mode",
  "role",
  "element",
  "race",
  "damage_type",
  "slot",
  "tier",
  "tierlist_slug",
  "focus",
  "min_value",
  "tag",
  "tags_any",
] as const;

const FILTER_LABELS: Record<string, string> = {
  server_region: "Regiao",
  mode: "Modo",
  role: "Role",
  element: "Elemento",
  race: "Raca",
  damage_type: "Dano",
  slot: "Slot",
  tier: "Tier",
  tierlist_slug: "Tierlist",
  focus: "Foco",
  min_value: "Min score",
  tag: "Tag",
  tags_any: "Tags",
};

function toPositiveInt(value: string, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }
  return Math.floor(parsed);
}

function filterPill(active: boolean): string {
  if (active) {
    return "rounded-md border border-accent/60 bg-accent/10 px-3 py-1 text-xs font-medium text-accent";
  }
  return "rounded-md border border-line px-3 py-1 text-xs text-textSoft transition hover:border-accent/30 hover:text-text";
}

function getParam(params: SearchParamsRecord, key: string): string | undefined {
  const raw = params[key];
  if (typeof raw === "string") {
    return raw;
  }
  if (Array.isArray(raw)) {
    for (let index = raw.length - 1; index >= 0; index -= 1) {
      const value = raw[index];
      if (typeof value === "string") {
        return value;
      }
    }
  }
  return undefined;
}

function prettyValue(value: string): string {
  return value
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .split(" ")
    .filter(Boolean)
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1).toLowerCase())
    .join(" ");
}

export default async function UnitsPage({ searchParams }: UnitsPageProps) {
  const params = await searchParams;

  const q = (getParam(params, "q") || "").trim();
  const page = getParam(params, "page") || "1";
  const pageSize = getParam(params, "page_size") || "24";
  const sortBy = getParam(params, "sort_by") || "name";
  const sortDir = getParam(params, "sort_dir") || "asc";
  const includeExternalRaw = getParam(params, "include_external") || "true";
  const includeExternal = includeExternalRaw !== "false";
  const serverRegion = getParam(params, "server_region") || "BOTH";

  const hiddenParams: Record<string, string> = {};
  for (const key of ADVANCED_FILTER_KEYS) {
    const value = getParam(params, key);
    if (value && value.trim()) {
      hiddenParams[key] = value;
    }
  }

  const query: Record<string, string> = {
    ...(q ? { q } : {}),
    ...hiddenParams,
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_dir: sortDir,
    include_external: includeExternal ? "true" : "false",
  };

  const units = await getUnits(query);

  const pagination = {
    page: toPositiveInt(String(units.page ?? 1), 1),
    pageSize: toPositiveInt(String(units.page_size ?? 24), 24),
    totalPages: toPositiveInt(String(units.total_pages ?? 1), 1),
  };

  const previousPage = Math.max(1, pagination.page - 1);
  const nextPage = Math.min(pagination.totalPages, pagination.page + 1);

  const baseQuery = new URLSearchParams(query);
  baseQuery.delete("page");

  const buildPageHref = (targetPage: number) => {
    const qs = new URLSearchParams(baseQuery);
    qs.set("page", String(targetPage));
    return `/units?${qs.toString()}`;
  };

  const buildWithoutKeysHref = (keys: string[]) => {
    const qs = new URLSearchParams(query);
    for (const key of keys) {
      qs.delete(key);
    }
    qs.delete("page");
    const queryString = qs.toString();
    return queryString ? `/units?${queryString}` : "/units";
  };

  const activeFilters = ADVANCED_FILTER_KEYS.reduce<Array<{ key: (typeof ADVANCED_FILTER_KEYS)[number]; label: string }>>(
    (acc, key) => {
      const value = hiddenParams[key];
      if (!value) {
        return acc;
      }
      acc.push({
        key,
        label: `${FILTER_LABELS[key]}: ${prettyValue(value)}`,
      });
      return acc;
    },
    []
  );

  const hasResults = units.items.length > 0;

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Database"
          title="Units"
          subtitle="Busca inteligente por nome/tag/mecanica com fallback externo para abrir paginas detalhadas mesmo fora da base local."
        />
      </Shell>

      <Shell>
        <UnitsSearchForm
          initialQ={q}
          sortBy={sortBy}
          sortDir={sortDir}
          pageSize={pageSize}
          includeExternal={includeExternal}
          currentPage={pagination.page}
          serverRegion={serverRegion}
          hiddenParams={hiddenParams}
        />
      </Shell>

      {activeFilters.length > 0 || !includeExternal || q ? (
        <Shell>
          <FilterBar title="Filtros ativos (clique para remover)">
            {q ? (
              <Link
                href={buildWithoutKeysHref(["q"])}
                className="rounded-md border border-accent/40 bg-accent/10 px-2 py-1 text-xs text-accent"
              >
                Busca: {q} x
              </Link>
            ) : null}

            {activeFilters.map((filter) => (
              <Link
                key={filter.key}
                href={buildWithoutKeysHref([filter.key])}
                className="rounded-md border border-accent/40 bg-accent/10 px-2 py-1 text-xs text-accent"
              >
                {filter.label} x
              </Link>
            ))}

            {!includeExternal ? (
              <Link
                href={buildWithoutKeysHref(["include_external"])}
                className="rounded-md border border-accent/40 bg-accent/10 px-2 py-1 text-xs text-accent"
              >
                Fonte: local apenas x
              </Link>
            ) : null}
          </FilterBar>
        </Shell>
      ) : null}

      <Shell>
        <FilterBar title="Filtros rapidos">
          <a href="/units" className={filterPill(!q)}>
            Todos
          </a>
          <a
            href="/units?q=abaddon&include_external=true"
            className={filterPill(q.toLowerCase() === "abaddon")}
          >
            Abaddon
          </a>
          <a href="/units?q=hart" className={filterPill(q.toLowerCase() === "hart")}>
            Hart
          </a>
          <a
            href="/units?mode=SUMMONERS_ROAD"
            className={filterPill(getParam(params, "mode") === "SUMMONERS_ROAD")}
          >
            Summoners Road
          </a>
          <a
            href="/units?focus=sustain&min_value=90"
            className={filterPill(getParam(params, "focus") === "sustain")}
          >
            Sustain 90+
          </a>
          <a
            href="/units?focus=nuke&min_value=90"
            className={filterPill(getParam(params, "focus") === "nuke")}
          >
            Nuke 90+
          </a>
          <a
            href="/units?tags_any=cleanse,mitigation"
            className={filterPill((getParam(params, "tags_any") || "").includes("cleanse"))}
          >
            Cleanse/Mitigation
          </a>
          <a
            href="/units?tags_any=art_gen,crit"
            className={filterPill((getParam(params, "tags_any") || "").includes("art_gen"))}
          >
            Art Gen/Crit
          </a>
          <a href="/units/compare" className={filterPill(false)}>
            Comparar Units
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs uppercase tracking-[0.2em] text-textSoft">
          <span>{units.count} resultados</span>
          <span>
            pagina {pagination.page} de {pagination.totalPages}
          </span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {units.items.map((unit) => (
            <UnitCard key={unit.id} unit={unit} />
          ))}
        </div>

        {!hasResults ? (
          <div className="mt-6 rounded-xl border border-line bg-panel p-5 text-sm text-textSoft">
            Nenhuma unit encontrada para os filtros atuais. Tente reduzir filtros, trocar ordenacao, ou habilitar "Incluir units externas".
          </div>
        ) : null}

        <div className="mt-6 flex items-center justify-between">
          <Link
            href={buildPageHref(previousPage)}
            className={`rounded-md border px-3 py-2 text-xs ${pagination.page <= 1 ? "pointer-events-none border-line/40 text-textSoft/50" : "border-line text-textSoft hover:text-text"}`}
          >
            Pagina anterior
          </Link>
          <Link
            href={buildPageHref(nextPage)}
            className={`rounded-md border px-3 py-2 text-xs ${pagination.page >= pagination.totalPages ? "pointer-events-none border-line/40 text-textSoft/50" : "border-line text-textSoft hover:text-text"}`}
          >
            Proxima pagina
          </Link>
        </div>
      </Shell>
    </main>
  );
}
