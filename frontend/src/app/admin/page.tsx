import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import {
  getAdminEditorialHistory,
  getAdminOverview,
  getAdminReviewQueue,
  getAdminSources,
} from "@/lib/api";

export default async function AdminPage() {
  const [overview, reviewQueue, sources, history] = await Promise.all([
    getAdminOverview(),
    getAdminReviewQueue(),
    getAdminSources(),
    getAdminEditorialHistory(),
  ]);

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Admin"
          title="Painel editorial"
          subtitle="Curadoria de units/equips/bosses/tiers/comps/guides com fluxo staged -> review -> publish e rastreio de fontes."
        />
      </Shell>

      <Shell>
        <section className="grid gap-4 md:grid-cols-2">
          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Inventario</h3>
            <ul className="mt-3 space-y-1 text-sm text-textSoft">
              {Object.entries(overview.counts).map(([key, value]) => (
                <li key={key}>
                  - {key}: {value}
                </li>
              ))}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Fila de revisao</h3>
            <ul className="mt-3 space-y-1 text-sm text-textSoft">
              {Object.entries(overview.pending_reviews).map(([key, value]) => (
                <li key={key}>
                  - {key}: {value}
                </li>
              ))}
            </ul>
          </article>
        </section>
      </Shell>

      <Shell>
        <section className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Review Queue</h3>
            <ul className="mt-3 space-y-2 text-sm text-textSoft">
              {reviewQueue.items.map((item) => (
                <li key={String(item.id)}>
                  - [{String(item.type)}] {String(item.title)} ({String(item.status)})
                </li>
              ))}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Sources</h3>
            <ul className="mt-3 space-y-2 text-sm text-textSoft">
              {sources.items.map((item) => (
                <li key={String(item.id)}>
                  - {String(item.name)} [{String(item.kind)}]
                </li>
              ))}
            </ul>
          </article>
        </section>
      </Shell>

      <Shell>
        <article className="rounded-xl border border-line bg-panel p-4">
          <h3 className="text-sm font-semibold text-text">Historico editorial</h3>
          <ul className="mt-3 space-y-2 text-sm text-textSoft">
            {history.items.map((item) => (
              <li key={String(item.id)}>
                - [{String(item.entity_type)}] {String(item.entity_id)} | {String(item.action)} | {String(item.published_at)}
              </li>
            ))}
          </ul>
        </article>
      </Shell>
    </main>
  );
}
