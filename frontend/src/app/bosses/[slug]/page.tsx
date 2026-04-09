import { notFound } from "next/navigation";

import { SolverPanel } from "@/components/boss-solver/solver-panel";
import { CompCard } from "@/components/cards/comp-card";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getBoss } from "@/lib/api";

interface BossDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function BossDetailPage({ params }: BossDetailPageProps) {
  const { slug } = await params;

  try {
    const data = await getBoss(slug);

    return (
      <main>
        <Shell>
          <SectionTitle
            eyebrow={`Boss Solver | ${data.item.mode}`}
            title={data.item.stage_name}
            subtitle={`${data.item.name} | Dificuldade ${data.item.difficulty}`}
          />
        </Shell>

        <Shell>
          <section className="grid gap-4 lg:grid-cols-3">
            <article className="rounded-xl border border-line bg-panel p-4 lg:col-span-2">
              <h3 className="text-sm font-semibold text-text">Visao geral</h3>
              <p className="mt-2 text-sm text-textSoft">{data.item.overview}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Mecanicas obrigatorias</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {data.item.required_tags.map((tag) => (
                  <li key={tag}>- {tag}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Ameacas principais</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {data.item.threats.map((threat) => (
                  <li key={threat}>- {threat}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Resistencias e gimmicks</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {data.item.resistances.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
                {data.item.gimmicks.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Condicoes especiais e utilidades necessarias</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {data.item.special_conditions.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
                {data.item.mechanics.map((mechanic) => (
                  <li key={mechanic.id}>
                    - {mechanic.description} [{mechanic.required_utilities.join(", ")}]
                  </li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Notas estrategicas e ordem de execucao</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {data.item.strategy_notes.map((note) => (
                  <li key={note}>- {note}</li>
                ))}
                <li>- {data.item.break_recommendation}</li>
              </ul>
            </article>

            <article className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Checks de solver</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                <li>- Precisa accuracy? {data.item.required_tags.includes("accuracy") ? "Sim" : "Nao"}</li>
                <li>- Precisa disease? {data.item.required_tags.includes("disease") ? "Sim" : "Nao"}</li>
                <li>- Precisa mitigacao? {data.item.required_tags.includes("mitigation") ? "Sim" : "Nao"}</li>
                <li>- Precisa cleanse? {data.item.required_tags.includes("cleanse") ? "Sim" : "Nao"}</li>
                <li>- Precisa taunt? {data.item.required_tags.includes("taunt") ? "Sim" : "Nao"}</li>
                <li>- Melhor abordagem: {data.item.required_tags.includes("nuke_core") ? "Nuke/Hibrida" : "Sustain"}</li>
              </ul>

              <div className="mt-4 rounded-lg border border-line bg-bgSoft p-3 text-xs text-textSoft">
                <p className="text-text">Crests sugeridas</p>
                <p>- Atk/Crit DMG para finisher</p>
                <p>- Skill CT para suporte</p>
                <p>- HP/DEF para clear seguro</p>
              </div>
            </article>
          </section>
        </Shell>

        <Shell>
          <SolverPanel bossSlug={slug} />
        </Shell>

        <Shell>
          <section className="space-y-4">
            <SectionTitle
              eyebrow="Comps recomendadas"
              title="Safe, Auto, Nuke e Budget"
              subtitle="Cada opcao inclui papel por slot e caminho de substitutes."
            />
            <div className="grid gap-4 md:grid-cols-2">
              {data.recommended_comps.map((comp) => (
                <CompCard key={comp.id} comp={comp} />
              ))}
            </div>
          </section>
        </Shell>
      </main>
    );
  } catch {
    notFound();
  }
}
