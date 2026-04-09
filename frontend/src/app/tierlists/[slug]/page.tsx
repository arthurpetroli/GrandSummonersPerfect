import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getTierlist } from "@/lib/api";

interface TierlistDetailPageProps {
  params: Promise<{ slug: string }>;
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
            subtitle="Explicacao por entrada, com dependencias, contexto de forca e historico de mudancas."
          />
        </Shell>

        <Shell>
          <section className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Metodologia</h3>
            <ul className="mt-2 space-y-1 text-sm text-textSoft">
              {data.methodology.criteria.map((item) => (
                <li key={item}>- {item}</li>
              ))}
            </ul>
            <ul className="mt-3 space-y-1 text-xs text-textSoft">
              {data.methodology.notes.map((item) => (
                <li key={item}>- {item}</li>
              ))}
            </ul>
          </section>
        </Shell>

        <Shell>
          <section className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Historico de mudancas</h3>
            <div className="mt-3 space-y-2">
              {data.change_history.map((change) => (
                <article key={`${change.version}-${change.change}`} className="rounded-lg border border-line bg-bgSoft p-3">
                  <p className="text-xs text-accent">v{change.version}</p>
                  <p className="mt-1 text-sm text-text">{change.change}</p>
                  <p className="mt-1 text-xs text-textSoft">{change.reason}</p>
                </article>
              ))}
            </div>
          </section>
        </Shell>

        <Shell>
          <section className="space-y-4">
            {Object.entries(data.grouped_entries).map(([tier, entries]) => (
              <article key={tier} className="rounded-xl border border-line bg-panel p-4">
                <h3 className="text-lg font-semibold text-text">Tier {tier}</h3>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  {entries.map((entry) => {
                    const item = entry as {
                      entity_id: string;
                      reason: string;
                      strong_in: string[];
                      weak_in: string[];
                      dependencies: string[];
                      substitutes: string[];
                      beginner_value: number;
                      veteran_value: number;
                      ease_of_use: number;
                      consistency: number;
                      niche_or_generalist: string;
                      requires_specific_team?: boolean;
                      requires_specific_equips?: boolean;
                    };
                    return (
                      <article key={item.entity_id} className="rounded-lg border border-line bg-bgSoft p-3">
                        <p className="text-sm font-semibold text-text">{item.entity_id}</p>
                        <p className="mt-1 text-sm text-textSoft">{item.reason}</p>
                        <p className="mt-2 text-xs text-textSoft">Forte em: {item.strong_in.join(", ")}</p>
                        <p className="text-xs text-textSoft">Fraco em: {item.weak_in.join(", ")}</p>
                        <p className="text-xs text-textSoft">Dependencias: {item.dependencies.join(", ")}</p>
                        <p className="text-xs text-textSoft">Substitutes: {item.substitutes.join(", ")}</p>
                        <p className="text-xs text-textSoft">Beginner/Veteran: {item.beginner_value}/{item.veteran_value}</p>
                        <p className="text-xs text-textSoft">Facilidade/Consistencia: {item.ease_of_use}/{item.consistency}</p>
                        <p className="text-xs text-textSoft">Perfil: {item.niche_or_generalist}</p>
                        <p className="text-xs text-textSoft">Exige equipe especifica? {item.requires_specific_team ? "Sim" : "Nao"}</p>
                        <p className="text-xs text-textSoft">Exige equips especificos? {item.requires_specific_equips ? "Sim" : "Nao"}</p>
                      </article>
                    );
                  })}
                </div>
              </article>
            ))}
          </section>
        </Shell>
      </main>
    );
  } catch {
    notFound();
  }
}
