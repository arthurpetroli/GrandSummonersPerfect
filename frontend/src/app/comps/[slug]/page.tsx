import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getComp } from "@/lib/api";

interface CompDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function CompDetailPage({ params }: CompDetailPageProps) {
  const { slug } = await params;

  try {
    const data = await getComp(slug);
    const explanation = data.explanation as {
      why_it_works?: string[];
      conditions?: string[];
      weak_points?: string[];
      missing_boss_requirements?: string[];
      substitute_logic?: Record<string, string[]>;
      strategy_summary?: string;
      synergy_notes?: string[];
      conflict_notes?: string[];
    };

    return (
      <main>
        <Shell>
          <SectionTitle
            eyebrow={`Comp | ${data.item.content_mode}`}
            title={data.item.name}
            subtitle={`${data.item.style} | ${data.item.summary}`}
          />
        </Shell>

        <Shell>
          <section className="grid gap-4 lg:grid-cols-3">
            <article className="rounded-xl border border-line bg-panel p-4 lg:col-span-2">
              <h3 className="text-sm font-semibold text-text">Por que funciona</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {(explanation.why_it_works ?? data.item.why_it_works).map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Condicoes</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {(explanation.conditions ?? []).map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Pontos fracos</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {(explanation.weak_points ?? data.item.weaknesses).map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Plano estrategico</h3>
              <p className="mt-2 text-sm text-textSoft">{explanation.strategy_summary ?? "Sem resumo estrategico."}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Sinergias</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {(explanation.synergy_notes ?? []).map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Conflitos</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {(explanation.conflict_notes ?? []).map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>
            </article>

            <article className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Substitute logic</h3>
              <ul className="mt-2 space-y-1 text-xs text-textSoft">
                {Object.entries(explanation.substitute_logic ?? {}).map(([unit, subs]) => (
                  <li key={unit}>
                    - {unit}: {subs.join(", ")}
                  </li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Gaps</h3>
              <ul className="mt-2 space-y-1 text-xs text-textSoft">
                {(explanation.missing_boss_requirements ?? []).map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Equips sugeridos</h3>
              <ul className="mt-2 space-y-1 text-xs text-textSoft">
                {data.item.equip_suggestions.map((item) => (
                  <li key={item.unit_id}>- {item.unit_id}: {item.equip_ids.join(", ")}</li>
                ))}
              </ul>
            </article>
          </section>
        </Shell>
      </main>
    );
  } catch {
    notFound();
  }
}
