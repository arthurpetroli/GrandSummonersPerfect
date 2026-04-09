import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getUnit } from "@/lib/api";

interface UnitDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function UnitDetailPage({ params }: UnitDetailPageProps) {
  const { slug } = await params;

  try {
    const { item, substitutes, synergies } = await getUnit(slug);

    return (
      <main>
        <Shell>
          <SectionTitle
            eyebrow={`Unit | ${item.server_region}`}
            title={item.name}
            subtitle={`${item.role} | ${item.element} | ${item.race} | Rarity ${item.rarity}`}
          />
        </Shell>

        <Shell>
          <section className="grid gap-4 lg:grid-cols-3">
            <article className="rounded-xl border border-line bg-panel p-4 lg:col-span-2">
              <h3 className="text-sm font-semibold text-text">Skill</h3>
              <p className="mt-2 text-sm text-textSoft">{item.skill.name}: {item.skill.description}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Arts</h3>
              <p className="mt-2 text-sm text-textSoft">{item.arts.name}: {item.arts.description}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">True Arts</h3>
              <p className="mt-2 text-sm text-textSoft">{item.true_arts.name}: {item.true_arts.description}</p>

              {item.super_arts ? (
                <>
                  <h3 className="mt-5 text-sm font-semibold text-text">Super Arts</h3>
                  <p className="mt-2 text-sm text-textSoft">{item.super_arts.name}: {item.super_arts.description}</p>
                </>
              ) : null}

              <h3 className="mt-5 text-sm font-semibold text-text">Passivas</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.passives.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="text-sm font-semibold text-text">Strengths</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.strengths.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Limitations</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.limitations.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Context Ratings</h3>
              <div className="mt-2 grid gap-2 sm:grid-cols-2">
                {Object.entries(item.values).map(([key, value]) => (
                  <div key={key} className="rounded-lg border border-line bg-bgSoft px-3 py-2 text-sm">
                    <span className="capitalize text-textSoft">{key}</span>
                    <span className="float-right text-text">{value}</span>
                  </div>
                ))}
              </div>

              <h3 className="mt-5 text-sm font-semibold text-text">Conteudos onde se destaca</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.best_use.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Conteudos onde rende menos</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.weak_in.map((value) => (
                  <li key={value}>- {value}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Dependencias</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.team_dependencies.map((value) => (
                  <li key={value}>- Team: {value}</li>
                ))}
                {item.equip_dependencies.map((value) => (
                  <li key={value}>- Equip: {value}</li>
                ))}
              </ul>
            </article>

            <article className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Tags</h3>
              <div className="mt-2 flex flex-wrap gap-1">
                {item.tags.map((tag) => (
                  <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
                    {tag}
                  </span>
                ))}
              </div>

              <h3 className="mt-5 text-sm font-semibold text-text">Substitutes</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {substitutes.map((sub) => (
                  <li key={sub.id}>- {sub.name}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Synergies</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {synergies.map((syn) => (
                  <li key={syn.id}>- {syn.name}</li>
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
