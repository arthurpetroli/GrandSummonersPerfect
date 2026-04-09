import Link from "next/link";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getModes } from "@/lib/api";

export default async function ModesPage() {
  const modes = await getModes();

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Mode Hubs"
          title="Hubs por modo"
          subtitle="Cada modo organiza units, equips, comps, bosses e guias para decisao rapida."
        />
      </Shell>

      <Shell>
        <div className="grid gap-4 md:grid-cols-2">
          {modes.items.map((mode) => (
            <article key={mode.slug} className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-base font-semibold text-text">{mode.name}</h3>
              <p className="mt-2 text-sm text-textSoft">{mode.overview}</p>
              <div className="mt-4 flex gap-2 text-xs text-textSoft">
                <a href={`/units?mode=${mode.mode}`} className="rounded-md border border-line px-2 py-1 hover:text-text">
                  Units
                </a>
                <a href={`/tierlists?mode=${mode.mode}`} className="rounded-md border border-line px-2 py-1 hover:text-text">
                  Tier List
                </a>
                <a href={`/bosses?mode=${mode.mode}`} className="rounded-md border border-line px-2 py-1 hover:text-text">
                  Bosses
                </a>
              </div>

              <Link href={`/modes/${mode.mode}`} className="mt-4 inline-flex rounded-md border border-accent/40 bg-accent/10 px-3 py-1 text-xs text-text hover:bg-accent/20">
                Abrir hub detalhado
              </Link>
            </article>
          ))}
        </div>
      </Shell>
    </main>
  );
}
