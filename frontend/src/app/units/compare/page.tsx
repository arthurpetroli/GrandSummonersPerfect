import Image from "next/image";
import Link from "next/link";

import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getUnit } from "@/lib/api";
import { UnitProfile } from "@/lib/types";

interface UnitsComparePageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

interface LoadedUnit {
  item: UnitProfile;
  externalSource: boolean;
}

const CORE_METRICS = ["beginner", "endgame", "sustain", "nuke", "auto", "arena"];

const QUICK_PAIRS = [
  { label: "Hart vs Abaddon", a: "hart", b: "abaddon" },
  { label: "Vox vs Cestina", a: "vox", b: "cestina" },
  { label: "Fen vs Hart", a: "fen", b: "hart" },
  { label: "Hart vs Miranda", a: "hart", b: "miranda" },
];

function getParam(params: Record<string, string | string[] | undefined>, key: string): string {
  const value = params[key];
  if (typeof value === "string") {
    return value.trim();
  }
  if (Array.isArray(value)) {
    for (let index = value.length - 1; index >= 0; index -= 1) {
      const candidate = value[index];
      if (typeof candidate === "string" && candidate.trim()) {
        return candidate.trim();
      }
    }
  }
  return "";
}

function compareHref(a: string, b: string): string {
  const query = new URLSearchParams();
  if (a.trim()) {
    query.set("a", a.trim());
  }
  if (b.trim()) {
    query.set("b", b.trim());
  }
  const serialized = query.toString();
  return serialized ? `/units/compare?${serialized}` : "/units/compare";
}

function sortedMetricKeys(left: LoadedUnit | null, right: LoadedUnit | null): string[] {
  const set = new Set<string>(CORE_METRICS);
  for (const key of Object.keys(left?.item.values || {})) {
    set.add(key);
  }
  for (const key of Object.keys(right?.item.values || {})) {
    set.add(key);
  }

  const core = CORE_METRICS.filter((key) => set.has(key));
  const extra = Array.from(set)
    .filter((key) => !CORE_METRICS.includes(key))
    .sort();
  return [...core, ...extra];
}

function prettyKey(value: string): string {
  return value
    .replaceAll("_", " ")
    .split(" ")
    .filter(Boolean)
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1).toLowerCase())
    .join(" ");
}

async function loadUnit(slug: string): Promise<LoadedUnit | null> {
  if (!slug) {
    return null;
  }
  try {
    const response = await getUnit(slug);
    return {
      item: response.item,
      externalSource: Boolean(response.external_source),
    };
  } catch {
    return null;
  }
}

function UnitPanel({
  title,
  requestedSlug,
  data,
}: {
  title: string;
  requestedSlug: string;
  data: LoadedUnit | null;
}) {
  if (!requestedSlug) {
    return (
      <article className="rounded-xl border border-line bg-panel p-4">
        <h3 className="text-sm font-semibold text-text">{title}</h3>
        <p className="mt-3 text-sm text-textSoft">Escolha uma unit para iniciar a comparacao.</p>
      </article>
    );
  }

  if (!data) {
    return (
      <article className="rounded-xl border border-line bg-panel p-4">
        <h3 className="text-sm font-semibold text-text">{title}</h3>
        <p className="mt-3 text-sm text-textSoft">
          Nao foi possivel carregar a unit "{requestedSlug}". Confira o slug ou pesquise em `/units`.
        </p>
      </article>
    );
  }

  const { item, externalSource } = data;

  return (
    <article className="rounded-xl border border-line bg-panel p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-textSoft">{title}</p>
          <h3 className="mt-1 text-lg font-semibold text-text">{item.name}</h3>
          <p className="mt-1 text-xs text-textSoft">
            {item.role} | {item.element} | {item.race}
          </p>
        </div>
        {externalSource ? (
          <span className="rounded border border-accent/40 bg-accent/10 px-2 py-1 text-[10px] uppercase tracking-wide text-accent">
            External
          </span>
        ) : null}
      </div>

      <div className="relative mt-3 h-52 overflow-hidden rounded-lg border border-line bg-bgSoft">
        <Image
          src={item.image_url || item.image_thumb_url || "/images/placeholders/unit-placeholder.svg"}
          alt={item.name}
          fill
          className="object-cover"
          sizes="(max-width: 768px) 100vw, 50vw"
          unoptimized
        />
      </div>

      <div className="mt-3 flex flex-wrap gap-1">
        {item.tags.slice(0, 8).map((tag) => (
          <span key={tag} className="rounded border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
            {tag}
          </span>
        ))}
      </div>

      <div className="mt-3 space-y-2 text-sm text-textSoft">
        <p>
          <span className="text-text">Strengths:</span> {(item.strengths || []).slice(0, 2).join(" | ") || "sem dados"}
        </p>
        <p>
          <span className="text-text">Limitations:</span> {(item.limitations || []).slice(0, 2).join(" | ") || "sem dados"}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <Link
          href={`/units/${item.slug}`}
          className="rounded-md border border-line px-2.5 py-1 text-textSoft transition hover:border-accent/40 hover:text-text"
        >
          Ver perfil completo
        </Link>
      </div>
    </article>
  );
}

export default async function UnitsComparePage({ searchParams }: UnitsComparePageProps) {
  const params = await searchParams;
  const leftSlug = getParam(params, "a");
  const rightSlug = getParam(params, "b");

  const [leftUnit, rightUnit] = await Promise.all([loadUnit(leftSlug), loadUnit(rightSlug)]);

  const metricKeys = sortedMetricKeys(leftUnit, rightUnit);

  const leftTags = new Set(leftUnit?.item.tags || []);
  const rightTags = new Set(rightUnit?.item.tags || []);
  const sharedTags = Array.from(leftTags).filter((tag) => rightTags.has(tag)).slice(0, 12);

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Units"
          title="Comparador lado a lado"
          subtitle="Compare duas units em valores contextuais, tags, pontos fortes e limitacoes para decidir investimento e slot."
        />
      </Shell>

      <Shell>
        <form action="/units/compare" className="rounded-xl border border-line bg-panel p-4">
          <div className="grid gap-3 md:grid-cols-[1fr_1fr_140px]">
            <input
              name="a"
              defaultValue={leftSlug}
              placeholder="Slug da unit A (ex: hart)"
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            />
            <input
              name="b"
              defaultValue={rightSlug}
              placeholder="Slug da unit B (ex: abaddon)"
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            />
            <button
              type="submit"
              className="rounded-md border border-accent/60 bg-accent/10 px-3 py-2 text-xs font-semibold text-accent"
            >
              Comparar
            </button>
          </div>
          <p className="mt-2 text-xs text-textSoft">Dica: use slugs da URL de `/units/[slug]`. Exemplo: /units/hart para slug `hart`.</p>
        </form>
      </Shell>

      <Shell>
        <FilterBar title="Pares rapidos">
          {QUICK_PAIRS.map((pair) => (
            <Link
              key={pair.label}
              href={compareHref(pair.a, pair.b)}
              className="rounded-md border border-line px-3 py-1 text-xs text-textSoft transition hover:border-accent/30 hover:text-text"
            >
              {pair.label}
            </Link>
          ))}
          <Link
            href="/units"
            className="rounded-md border border-line px-3 py-1 text-xs text-textSoft transition hover:border-accent/30 hover:text-text"
          >
            Abrir lista de units
          </Link>
        </FilterBar>
      </Shell>

      <Shell>
        <section className="grid gap-4 lg:grid-cols-2">
          <UnitPanel title="Unit A" requestedSlug={leftSlug} data={leftUnit} />
          <UnitPanel title="Unit B" requestedSlug={rightSlug} data={rightUnit} />
        </section>
      </Shell>

      {leftUnit && rightUnit ? (
        <Shell>
          <section className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Comparacao de valores contextuais</h3>
            <div className="mt-3 space-y-2">
              {metricKeys.map((key) => {
                const leftValue = leftUnit.item.values[key];
                const rightValue = rightUnit.item.values[key];
                const leftWins =
                  typeof leftValue === "number" && typeof rightValue === "number" && leftValue > rightValue;
                const rightWins =
                  typeof leftValue === "number" && typeof rightValue === "number" && rightValue > leftValue;

                return (
                  <div key={key} className="grid items-center gap-2 rounded-lg border border-line bg-bgSoft px-3 py-2 md:grid-cols-[88px_1fr_auto_1fr]">
                    <span className="text-xs uppercase tracking-wide text-textSoft">{prettyKey(key)}</span>
                    <span className={`text-sm ${leftWins ? "font-semibold text-emerald-300" : "text-text"}`}>
                      {typeof leftValue === "number" ? leftValue : "-"}
                    </span>
                    <span className="text-[10px] uppercase tracking-[0.14em] text-textSoft">
                      {leftWins ? "A > B" : rightWins ? "B > A" : "Empate"}
                    </span>
                    <span className={`text-right text-sm ${rightWins ? "font-semibold text-emerald-300" : "text-text"}`}>
                      {typeof rightValue === "number" ? rightValue : "-"}
                    </span>
                  </div>
                );
              })}
            </div>

            <h3 className="mt-5 text-sm font-semibold text-text">Tags em comum</h3>
            <div className="mt-2 flex flex-wrap gap-1">
              {sharedTags.map((tag) => (
                <span key={tag} className="rounded border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
                  {tag}
                </span>
              ))}
              {!sharedTags.length ? <span className="text-xs text-textSoft">Sem tags em comum relevantes.</span> : null}
            </div>
          </section>
        </Shell>
      ) : null}
    </main>
  );
}
