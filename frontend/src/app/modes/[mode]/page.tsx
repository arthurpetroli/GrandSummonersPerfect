import Link from "next/link";
import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getModeHub } from "@/lib/api";

interface ModeDetailPageProps {
  params: Promise<{ mode: string }>;
}

export default async function ModeDetailPage({ params }: ModeDetailPageProps) {
  const { mode } = await params;

  try {
    const { item } = await getModeHub(mode);

    return (
      <main>
        <Shell>
          <SectionTitle
            eyebrow={`Mode Hub | ${item.mode}`}
            title={item.name}
            subtitle={item.overview}
          />
        </Shell>

        <Shell>
          <section className="grid gap-4 lg:grid-cols-3">
            <article className="rounded-xl border border-line bg-panel p-4 lg:col-span-2">
              <h3 className="text-sm font-semibold text-text">Dicas estrategicas</h3>
              <ul className="mt-2 space-y-1 text-sm text-textSoft">
                {item.strategy_tips.map((tip) => (
                  <li key={tip}>- {tip}</li>
                ))}
              </ul>

              <h3 className="mt-5 text-sm font-semibold text-text">Melhores units (IDs)</h3>
              <p className="mt-2 text-sm text-textSoft">{item.top_units.join(", ")}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Melhores equips (IDs)</h3>
              <p className="mt-2 text-sm text-textSoft">{item.top_equips.join(", ")}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Composicoes comuns (IDs)</h3>
              <p className="mt-2 text-sm text-textSoft">{item.common_comp_ids.join(", ") || "Nenhuma"}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Bosses importantes (IDs)</h3>
              <p className="mt-2 text-sm text-textSoft">{item.important_boss_ids.join(", ") || "Nenhum"}</p>
            </article>

            <article className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-sm font-semibold text-text">Links rapidos</h3>
              <div className="mt-2 space-y-2 text-xs text-textSoft">
                <Link href={`/units?mode=${item.mode}`} className="block rounded-md border border-line px-3 py-2 hover:text-text">
                  Database de Units
                </Link>
                <Link href={`/equips`} className="block rounded-md border border-line px-3 py-2 hover:text-text">
                  Database de Equips
                </Link>
                <Link href={`/bosses?mode=${item.mode}`} className="block rounded-md border border-line px-3 py-2 hover:text-text">
                  Bosses do modo
                </Link>
                <Link href={`/tierlists?mode=${item.mode}`} className="block rounded-md border border-line px-3 py-2 hover:text-text">
                  Tier list do modo
                </Link>
                <Link href={`/guides?mode=${item.mode}`} className="block rounded-md border border-line px-3 py-2 hover:text-text">
                  Guides do modo
                </Link>
              </div>

              <h3 className="mt-5 text-sm font-semibold text-text">Tierlists sugeridas</h3>
              <p className="mt-2 text-xs text-textSoft">{item.tierlist_slugs.join(", ") || "Nenhuma"}</p>

              <h3 className="mt-5 text-sm font-semibold text-text">Guides sugeridos</h3>
              <p className="mt-2 text-xs text-textSoft">{item.guide_slugs.join(", ") || "Nenhum"}</p>
            </article>
          </section>
        </Shell>
      </main>
    );
  } catch {
    notFound();
  }
}
