import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import {
  getAdminGsinfoUnitsStatus,
  getAdminEditorialHistory,
  getAdminOverview,
  getAdminReviewQueue,
  getAdminSourceMappings,
  getAdminSources,
  getAdminSyncStatus,
  getAdminTierlistDrafts,
} from "@/lib/api";

import {
  publishDraftAction,
  refreshGsinfoStatusAction,
  runAutoSyncAction,
  runGsinfoUnitsSyncAction,
  runImageSyncAction,
  runTierlistSheetApplyAction,
  runTierlistSheetImportAction,
} from "./actions";

function readRecord(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null) {
    return {};
  }
  return value as Record<string, unknown>;
}

export default async function AdminPage() {
  const [overview, reviewQueue, sources, sourceMappings, history, tierDrafts, syncStatus, gsinfoStatus] = await Promise.all([
    getAdminOverview(),
    getAdminReviewQueue(),
    getAdminSources(),
    getAdminSourceMappings(),
    getAdminEditorialHistory(),
    getAdminTierlistDrafts(),
    getAdminSyncStatus(),
    getAdminGsinfoUnitsStatus(),
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
        <section className="rounded-xl border border-line bg-panel p-4">
          <h3 className="text-sm font-semibold text-text">Ingestao de Tierlist (Google Sheet)</h3>
          <p className="mt-2 text-xs text-textSoft">
            Executa importacao em modo preview para validar o parse da planilha comunitaria e registrar mappings da pipeline.
          </p>

          <form action={runTierlistSheetImportAction} className="mt-3 grid gap-3 md:grid-cols-3">
            <input
              name="spreadsheet_url"
              defaultValue="https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit"
              className="rounded-md border border-line bg-bgSoft px-3 py-2 text-xs text-text"
            />
            <input
              name="gid"
              defaultValue="116729514"
              className="rounded-md border border-line bg-bgSoft px-3 py-2 text-xs text-text"
            />
            <button
              type="submit"
              className="rounded-md border border-accent/60 bg-accent/10 px-3 py-2 text-xs font-semibold text-accent"
            >
              Rodar Preview Import
            </button>
          </form>

          <form action={runTierlistSheetApplyAction} className="mt-2 grid gap-3 md:grid-cols-3">
            <input
              name="spreadsheet_url"
              defaultValue="https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit"
              className="rounded-md border border-line bg-bgSoft px-3 py-2 text-xs text-text"
            />
            <input
              name="gid"
              defaultValue="116729514"
              className="rounded-md border border-line bg-bgSoft px-3 py-2 text-xs text-text"
            />
            <button
              type="submit"
              className="rounded-md border border-emerald-500/60 bg-emerald-500/10 px-3 py-2 text-xs font-semibold text-emerald-300"
            >
              Aplicar Sync no Sistema
            </button>
          </form>

          <div className="mt-3 grid gap-2 md:grid-cols-2">
            <form action={runAutoSyncAction}>
              <input type="hidden" name="force" value="0" />
              <button
                type="submit"
                className="w-full rounded-md border border-accent/60 bg-accent/10 px-3 py-2 text-xs font-semibold text-accent"
              >
                Rodar Auto Sync (somente se mudou)
              </button>
            </form>
            <form action={runAutoSyncAction}>
              <input type="hidden" name="force" value="1" />
              <button
                type="submit"
                className="w-full rounded-md border border-fuchsia-500/60 bg-fuchsia-500/10 px-3 py-2 text-xs font-semibold text-fuchsia-300"
              >
                Forcar Sync Completo
              </button>
            </form>
          </div>

          <form action={runImageSyncAction} className="mt-2">
            <button
              type="submit"
              className="w-full rounded-md border border-line px-3 py-2 text-xs font-semibold text-text"
            >
              Atualizar Imagens de Units (GSInfo)
            </button>
          </form>

          <div className="mt-2 grid gap-2 md:grid-cols-2">
            <form action={runGsinfoUnitsSyncAction}>
              <button
                type="submit"
                className="w-full rounded-md border border-line px-3 py-2 text-xs font-semibold text-text"
              >
                Reindexar Base GSInfo Units
              </button>
            </form>
            <form action={refreshGsinfoStatusAction}>
              <button
                type="submit"
                className="w-full rounded-md border border-line px-3 py-2 text-xs font-semibold text-text"
              >
                Atualizar Status GSInfo
              </button>
            </form>
          </div>

          <div className="mt-3 rounded-md border border-line bg-bgSoft p-3 text-xs text-textSoft">
            {(() => {
              const tierSync = readRecord(readRecord(syncStatus.sync).tier_sync);
              return (
                <>
                  <p>Ultimo tier sync: {String(readRecord(syncStatus.sync).last_tier_sync_at ?? "-")}</p>
                  <p>Ultimo image sync: {String(readRecord(syncStatus.sync).last_image_sync_at ?? "-")}</p>
                  <p>Signature: {String(readRecord(syncStatus.sync).last_sync_signature ?? "-")}</p>
                  <p>Sheet last updated: {String(tierSync.sheet_last_updated ?? "-")}</p>
                  <p>GSInfo indexed units: {String(readRecord(gsinfoStatus).store ? readRecord(readRecord(gsinfoStatus).store).count : "-")}</p>
                  <p>GSInfo store updated: {String(readRecord(gsinfoStatus).store ? readRecord(readRecord(gsinfoStatus).store).updated_at : "-")}</p>
                </>
              );
            })()}
            <p className="mt-1">Nota legal: imagens e assets de Grand Summoners pertencem aos respectivos proprietarios.</p>
          </div>
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
                  - {String(item.name)} [{String(item.kind)}] - {String(item.last_synced_at ?? "-")}
                </li>
              ))}
            </ul>
          </article>
        </section>
      </Shell>

      <Shell>
        <section className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Tierlist Drafts</h3>
            <ul className="mt-3 space-y-2 text-sm text-textSoft">
              {tierDrafts.items.length === 0 ? <li>- Sem drafts no momento</li> : null}
              {tierDrafts.items.map((draft) => (
                <li key={String(draft.id)} className="rounded-md border border-line bg-bgSoft p-2">
                  <p>
                    - {String(draft.tierlist_slug)} :: {String(draft.entity_id)} -&gt; {String(draft.proposed_tier)} ({String(draft.status)})
                  </p>
                  {String(draft.status) !== "published" ? (
                    <form action={publishDraftAction} className="mt-2">
                      <input type="hidden" name="draft_id" value={String(draft.id)} />
                      <button
                        type="submit"
                        className="rounded-md border border-accent/50 bg-accent/10 px-2 py-1 text-[11px] font-semibold text-accent"
                      >
                        Publicar Draft
                      </button>
                    </form>
                  ) : null}
                </li>
              ))}
            </ul>
          </article>

          <article className="rounded-xl border border-line bg-panel p-4">
            <h3 className="text-sm font-semibold text-text">Source Mappings</h3>
            <ul className="mt-3 space-y-2 text-sm text-textSoft">
              {sourceMappings.items.length === 0 ? <li>- Sem mappings registrados</li> : null}
              {sourceMappings.items.slice(0, 12).map((item) => (
                <li key={String(item.id)}>
                  - {String(item.source_id)} :: {String(item.entity_type)} :: {String(item.entity_id ?? item.source_entity_key)} [{String(item.validation_status ?? "pending")}]
                </li>
              ))}
            </ul>
          </article>
        </section>
      </Shell>

      <Shell>
        <article className="rounded-xl border border-line bg-panel p-4">
          <h3 className="text-sm font-semibold text-text">Sync Jobs Recentes</h3>
          <ul className="mt-3 space-y-2 text-sm text-textSoft">
            {syncStatus.recent_jobs.length === 0 ? <li>- Sem jobs executados</li> : null}
            {syncStatus.recent_jobs.map((job) => (
              <li key={String(job.id)}>
                - {String(job.source_id)} | {String(job.status)} | {String(job.created_at)}
              </li>
            ))}
          </ul>
        </article>
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
