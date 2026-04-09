import Link from "next/link";

import { CompCard } from "@/components/cards/comp-card";
import { FadeIn } from "@/components/motion/fade-in";
import { TierlistCard } from "@/components/cards/tierlist-card";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getHome } from "@/lib/api";

export default async function HomePage() {
  const home = await getHome();

  return (
    <main>
      <Shell>
        <FadeIn>
          <section className="rounded-2xl border border-line bg-panel/80 p-5 shadow-glow md:p-8">
            <p className="text-xs uppercase tracking-[0.2em] text-accent">Grand Summoners Companion</p>
            <h1 className="mt-2 text-3xl font-semibold leading-tight md:text-5xl">Decisao pratica para cada boss, comp e investimento.</h1>
            <p className="mt-3 max-w-3xl text-sm text-textSoft md:text-base">{home.hero_message}</p>

            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <form action="/search" className="rounded-xl border border-line bg-bgSoft p-3">
                <input
                  name="q"
                  placeholder="Buscar unit, equip, boss, guide ou comp..."
                  className="w-full rounded-md border border-line bg-panel px-3 py-2 text-sm text-text"
                />
              </form>
              <div className="rounded-xl border border-line bg-bgSoft p-3 text-xs text-textSoft">
                <p className="text-text">Regiao visivel</p>
                <p>- Global / JP com diferencas de disponibilidade</p>
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2 md:grid-cols-3">
              {home.quick_links.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="rounded-xl border border-line bg-bgSoft px-4 py-3 text-sm text-textSoft transition hover:border-accent/40 hover:text-text"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </section>
        </FadeIn>
      </Shell>

      <Shell>
        <FadeIn delay={0.08}>
          <section className="space-y-4">
          <SectionTitle eyebrow="Meta" title="Tier Lists em destaque" subtitle="Ranking contextual com explicacao, dependencia e substitute." />
          <div className="grid gap-4 md:grid-cols-2">
            {home.featured_tierlists.map((tier) => (
              <TierlistCard key={tier.id} tierlist={tier} />
            ))}
          </div>
          </section>
        </FadeIn>
      </Shell>

      <Shell>
        <FadeIn delay={0.12}>
          <section className="space-y-4">
          <SectionTitle eyebrow="Comps" title="Composicoes em alta" subtitle="Opcoes seguras, budget e nuke para conteudos populares." />
          <div className="grid gap-4 md:grid-cols-3">
            {home.trending_comps.map((comp) => (
              <CompCard key={comp.id} comp={comp} />
            ))}
          </div>
          </section>
        </FadeIn>
      </Shell>

      <Shell>
        <FadeIn delay={0.16}>
          <section className="space-y-4 rounded-2xl border border-line bg-panel p-5 md:p-6">
            <SectionTitle eyebrow="Updates" title="Mudancas recentes" subtitle="Leituras rapidas para entender shifts de meta." />
            <div className="space-y-3">
              {home.recent_updates.map((update) => (
                <article key={update.id} className="rounded-xl border border-line bg-bgSoft p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-text md:text-base">{update.title}</h3>
                    <span className="text-xs text-accent">{update.patch_version}</span>
                  </div>
                  <p className="mt-2 text-sm text-textSoft">{update.summary}</p>
                </article>
              ))}
            </div>
          </section>
        </FadeIn>
      </Shell>
    </main>
  );
}
