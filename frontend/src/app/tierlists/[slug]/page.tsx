import Link from "next/link";
import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getTierlist } from "@/lib/api";
import { TierlistGroupedEntry } from "@/lib/types";

interface TierlistDetailPageProps {
  params: Promise<{ slug: string }>;
}

const TIER_ORDER = ["SSS", "SS", "S", "A", "B", "C"];

const TIER_STYLES: Record<string, { panel: string; badge: string; meter: string }> = {
  SSS: {
    panel: "border-amber-500/40 bg-amber-500/5",
    badge: "border-amber-400/60 bg-amber-500/20 text-amber-200",
    meter: "bg-amber-400",
  },
  SS: {
    panel: "border-fuchsia-500/40 bg-fuchsia-500/5",
    badge: "border-fuchsia-400/60 bg-fuchsia-500/20 text-fuchsia-200",
    meter: "bg-fuchsia-400",
  },
  S: {
    panel: "border-rose-500/40 bg-rose-500/5",
    badge: "border-rose-400/60 bg-rose-500/20 text-rose-200",
    meter: "bg-rose-400",
  },
  A: {
    panel: "border-cyan-500/40 bg-cyan-500/5",
    badge: "border-cyan-400/60 bg-cyan-500/20 text-cyan-200",
    meter: "bg-cyan-400",
  },
  B: {
    panel: "border-emerald-500/40 bg-emerald-500/5",
    badge: "border-emerald-400/60 bg-emerald-500/20 text-emerald-200",
    meter: "bg-emerald-400",
  },
  C: {
    panel: "border-slate-500/50 bg-slate-500/5",
    badge: "border-slate-400/60 bg-slate-500/20 text-slate-200",
    meter: "bg-slate-400",
  },
};

const CATEGORY_LABELS: Record<string, string> = {
  overall_units: "Overall Units",
  beginner_units: "Beginner",
  endgame_units: "Endgame",
  sustain_units: "Sustain",
  nuke_units: "Nuke",
  arena_units: "Arena",
  farming_units: "Farming",
  bossing_units: "Bossing",
  support_units: "Support",
  mode_specific_units: "Mode Specific",
  overall_equips: "Equips",
};

const MODE_LABELS: Record<string, string> = {
  STORY: "Story / Progression",
  ARENA: "Arena",
  DUNGEON_OF_TRIALS: "Dungeon of Trials",
  CREST_PALACE: "Crest Palace",
  SUMMONERS_ROAD: "Summoners' Road",
  MAGICAL_MINES: "Magical Mines",
  GRAND_CRUSADE: "Grand Crusade",
  RAID: "Raids / Event Bosses",
  COLLAB: "Collab",
};

function renderMetric(label: string, value: number, meterClass: string) {
  const normalized = Math.max(0, Math.min(100, value));
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px] text-textSoft">
        <span>{label}</span>
        <span className="font-semibold text-text">{normalized}</span>
      </div>
      <div className="h-1.5 rounded-full bg-bg">
        <div className={`h-1.5 rounded-full ${meterClass}`} style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
}

function fallbackHref(entry: TierlistGroupedEntry): string | null {
  if (entry.entity_href) {
    return entry.entity_href;
  }
  if (!entry.entity_slug) {
    return null;
  }
  if (entry.entity_type === "equip") {
    return `/equips/${entry.entity_slug}`;
  }
  if (entry.entity_type === "unit") {
    return `/units/${entry.entity_slug}`;
  }
  return null;
}

export default async function TierlistDetailPage({ params }: TierlistDetailPageProps) {
  const { slug } = await params;

  try {
    const data = await getTierlist(slug);

    return (
      <main>
        <Shell>
          <SectionTitle
            eyebrow={`Tier List | v${data.item.version}`}
            title={data.item.title}
            subtitle="Tier contextual com explicacao, dependencias, substitutes e sinalizacao de uso para beginner e veterano."
          />
          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-full border border-accent/40 bg-accent/10 px-2 py-1 text-accent">
              {CATEGORY_LABELS[data.item.category] ?? data.item.category}
            </span>
            {data.item.mode ? (
              <span className="rounded-full border border-line bg-panel px-2 py-1 text-textSoft">
                {MODE_LABELS[data.item.mode] ?? data.item.mode}
              </span>
            ) : null}
            {data.item.server_region ? (
              <span className="rounded-full border border-line bg-panel px-2 py-1 text-textSoft">
                {data.item.server_region}
              </span>
            ) : null}
          </div>
        </Shell>

        <Shell>
          <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
            <section className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Metodologia</h3>
              <ul className="mt-3 space-y-2 text-sm text-textSoft">
                {data.methodology.criteria.map((item) => (
                  <li key={item} className="rounded-md border border-line bg-bgSoft px-3 py-2">
                    {item}
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-xs font-semibold uppercase tracking-[0.14em] text-textSoft">Notas</p>
              <ul className="mt-2 space-y-1 text-xs text-textSoft">
                {data.methodology.notes.map((item) => (
                  <li key={item}>- {item}</li>
                ))}
              </ul>
            </section>

            <section className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Historico de mudancas</h3>
              <div className="mt-3 space-y-3">
                {data.change_history.map((change) => (
                  <article key={`${change.version}-${change.change}`} className="rounded-lg border border-line bg-bgSoft p-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.12em] text-accent">v{change.version}</p>
                    <p className="mt-1 text-sm text-text">{change.change}</p>
                    <p className="mt-1 text-xs text-textSoft">{change.reason}</p>
                  </article>
                ))}
              </div>
            </section>
          </div>
        </Shell>

        <Shell>
          <section className="space-y-4">
            {TIER_ORDER.filter((tier) => (data.grouped_entries[tier] ?? []).length > 0).map((tier) => {
              const entries = [...(data.grouped_entries[tier] ?? [])].sort(
                (left, right) => right.context_score - left.context_score
              );
              const style = TIER_STYLES[tier] ?? TIER_STYLES.C;

              return (
                <article key={tier} className={`rounded-xl border p-4 ${style.panel}`}>
                  <div className="mb-3 flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-text">Tier {tier}</h3>
                    <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${style.badge}`}>
                      {entries.length} entries
                    </span>
                  </div>
                  <div className="mt-3 grid gap-3 md:grid-cols-2">
                    {entries.map((entry) => {
                      const href = fallbackHref(entry);
                      return (
                        <article key={entry.entity_id} className="rounded-lg border border-line bg-panel p-4">
                          <div className="flex items-start justify-between gap-2">
                            {href ? (
                              <Link href={href} className="text-sm font-semibold text-text transition hover:text-accent">
                                {entry.entity_name}
                              </Link>
                            ) : (
                              <p className="text-sm font-semibold text-text">{entry.entity_name}</p>
                            )}
                            <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${style.badge}`}>
                              Score {Math.round(entry.context_score)}
                            </span>
                          </div>

                          <p className="mt-2 text-sm text-textSoft">{entry.reason}</p>

                          <div className="mt-3 grid gap-2 sm:grid-cols-2">
                            {renderMetric("Beginner", entry.beginner_value, style.meter)}
                            {renderMetric("Veteran", entry.veteran_value, style.meter)}
                            {renderMetric("Ease", entry.ease_of_use, style.meter)}
                            {renderMetric("Consistency", entry.consistency, style.meter)}
                          </div>

                          <div className="mt-3 space-y-1 text-xs text-textSoft">
                            <p>
                              <span className="text-text">Forte em:</span> {entry.strong_in.join(", ") || "-"}
                            </p>
                            <p>
                              <span className="text-text">Fraco em:</span> {entry.weak_in.join(", ") || "-"}
                            </p>
                            <p>
                              <span className="text-text">Perfil:</span> {entry.niche_or_generalist}
                            </p>
                            <p>
                              <span className="text-text">Exige equipe especifica:</span> {entry.requires_specific_team ? "Sim" : "Nao"}
                            </p>
                            <p>
                              <span className="text-text">Exige equips especificos:</span> {entry.requires_specific_equips ? "Sim" : "Nao"}
                            </p>
                          </div>

                          {entry.dependencies.length > 0 ? (
                            <div className="mt-3 flex flex-wrap gap-1">
                              {entry.dependencies.map((dependency) => (
                                <span key={dependency} className="rounded-full border border-line bg-bgSoft px-2 py-0.5 text-[11px] text-textSoft">
                                  {dependency}
                                </span>
                              ))}
                            </div>
                          ) : null}

                          {entry.substitute_entities.length > 0 ? (
                            <div className="mt-3 flex flex-wrap gap-1">
                              {entry.substitute_entities.map((substitute) =>
                                substitute.href ? (
                                  <Link
                                    key={`${entry.entity_id}-${substitute.id}`}
                                    href={substitute.href}
                                    className="rounded-full border border-accent/30 bg-accent/10 px-2 py-0.5 text-[11px] text-accent transition hover:border-accent/60"
                                  >
                                    {substitute.name}
                                  </Link>
                                ) : (
                                  <span
                                    key={`${entry.entity_id}-${substitute.id}`}
                                    className="rounded-full border border-accent/30 bg-accent/10 px-2 py-0.5 text-[11px] text-accent"
                                  >
                                    {substitute.name}
                                  </span>
                                )
                              )}
                            </div>
                          ) : null}
                        </article>
                      );
                    })}
                  </div>
                </article>
              );
            })}
          </section>
        </Shell>
      </main>
    );
  } catch {
    notFound();
  }
}
