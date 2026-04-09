import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getEquip } from "@/lib/api";

interface EquipDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function EquipDetailPage({ params }: EquipDetailPageProps) {
  const { slug } = await params;

  try {
    const { item, substitutes } = await getEquip(slug);
    return (
      <main>
        <Shell>
          <SectionTitle
            eyebrow={`Equip | ${item.server_region}`}
            title={item.name}
            subtitle={`${item.slot_type} | ${item.category} | Cooldown ${item.cooldown_seconds}s`}
          />
        </Shell>
        <Shell>
          <section className="grid gap-4 lg:grid-cols-3">
            <article className="rounded-xl border border-line bg-panel p-4 lg:col-span-2">
              <h3 className="text-sm font-semibold text-text">Skill ativa</h3>
              <p className="mt-2 text-sm text-textSoft">{item.active_skill}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Passiva</h3>
              <p className="mt-2 text-sm text-textSoft">{item.passive}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Stats</h3>
              <p className="mt-2 text-sm text-textSoft">
                HP {item.stats.hp ?? 0} | ATK {item.stats.atk ?? 0} | DEF {item.stats.def ?? 0}
              </p>

              <h3 className="text-sm font-semibold text-text">Tags utilitarias</h3>
              <div className="mt-2 flex flex-wrap gap-1">
                {item.tags.map((tag) => (
                  <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
                    {tag}
                  </span>
                ))}
              </div>
              <h3 className="mt-5 text-sm font-semibold text-text">Uso recomendado</h3>
              <p className="mt-2 text-sm text-textSoft">
                Este equip aparece na categoria {item.category} com ranking {item.ranking_overall}, normalmente usado em setups de {item.tags.join(", ")}.
              </p>

              <h3 className="mt-5 text-sm font-semibold text-text">Composicoes e bosses onde ajuda</h3>
              <p className="mt-2 text-sm text-textSoft">Comps: {item.comp_notes.join(" | ")}</p>
              <p className="mt-1 text-sm text-textSoft">Bosses: {item.boss_help.join(" | ")}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Ranking por contexto</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {Object.entries(item.ranking_by_context).map(([key, value]) => (
                  <li key={key}>- {key}: {value}</li>
                ))}
              </ul>
            </article>
            <article className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Substitutos</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {substitutes.map((sub) => (
                  <li key={sub.id}>- {sub.name}</li>
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
