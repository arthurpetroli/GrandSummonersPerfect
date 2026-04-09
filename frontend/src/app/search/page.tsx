import Link from "next/link";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getSearchResults } from "@/lib/api";

interface SearchPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const params = await searchParams;
  const q = typeof params.q === "string" ? params.q.trim() : "";
  const server_region = typeof params.server_region === "string" ? params.server_region : "BOTH";

  const results = q
    ? await getSearchResults({
        q,
        server_region,
        limit: "12",
      })
    : {
        units: [],
        equips: [],
        bosses: [],
        guides: [],
        comps: [],
      };

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Busca"
          title="Busca global"
          subtitle="Busca unificada por units, equips, bosses, guides e comps com recorte por regiao."
        />
      </Shell>

      <Shell>
        <form action="/search" className="rounded-xl border border-line bg-panel p-4">
          <div className="grid gap-3 md:grid-cols-[1fr_180px]">
            <input
              name="q"
              defaultValue={q}
              placeholder="Buscar por unit, equip, boss, guide ou comp..."
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            />
            <select
              name="server_region"
              defaultValue={server_region}
              className="rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            >
              <option value="BOTH">Global + JP</option>
              <option value="GLOBAL">Global</option>
              <option value="JP">JP</option>
            </select>
          </div>
        </form>
      </Shell>

      <Shell>
        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Units</h3>
            <ul className="mt-2 space-y-1 text-sm text-textSoft">
              {results.units.map((item) => (
                <li key={item.id}>
                  <Link href={`/units/${item.slug}`} className="hover:text-text">
                    - {item.name}
                  </Link>
                </li>
              ))}
              {!results.units.length ? <li>- sem resultados</li> : null}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Equips</h3>
            <ul className="mt-2 space-y-1 text-sm text-textSoft">
              {results.equips.map((item) => (
                <li key={item.id}>
                  <Link href={`/equips/${item.slug}`} className="hover:text-text">
                    - {item.name}
                  </Link>
                </li>
              ))}
              {!results.equips.length ? <li>- sem resultados</li> : null}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Bosses</h3>
            <ul className="mt-2 space-y-1 text-sm text-textSoft">
              {results.bosses.map((item) => (
                <li key={item.id}>
                  <Link href={`/bosses/${item.slug}`} className="hover:text-text">
                    - {item.name}
                  </Link>
                </li>
              ))}
              {!results.bosses.length ? <li>- sem resultados</li> : null}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Guides</h3>
            <ul className="mt-2 space-y-1 text-sm text-textSoft">
              {results.guides.map((item) => (
                <li key={item.id}>
                  <Link href={`/guides/${item.slug}`} className="hover:text-text">
                    - {item.name}
                  </Link>
                </li>
              ))}
              {!results.guides.length ? <li>- sem resultados</li> : null}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Comps</h3>
            <ul className="mt-2 space-y-1 text-sm text-textSoft">
              {results.comps.map((item) => (
                <li key={item.id}>
                  <Link href={`/comps/${item.slug}`} className="hover:text-text">
                    - {item.name}
                  </Link>
                </li>
              ))}
              {!results.comps.length ? <li>- sem resultados</li> : null}
            </ul>
          </article>
        </section>
      </Shell>
    </main>
  );
}
