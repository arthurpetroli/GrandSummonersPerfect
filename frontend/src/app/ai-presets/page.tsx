import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getAIPresets } from "@/lib/api";

interface AIPresetsPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function AIPresetsPage({ searchParams }: AIPresetsPageProps) {
  const params = await searchParams;
  const purpose = typeof params.purpose === "string" ? params.purpose : undefined;

  const presets = await getAIPresets({ ...(purpose ? { purpose } : {}) });

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="AI Presets"
          title="Biblioteca de presets"
          subtitle="Presets para auto-safe, nuke opener, sustain loop e respostas anti-mecanica."
        />
      </Shell>

      <Shell>
        <div className="rounded-xl border border-line bg-panel p-4 text-xs text-textSoft">
          <a href="/ai-presets" className="mr-2 rounded-md border border-line px-2 py-1 hover:text-text">
            Todos
          </a>
          <a href="/ai-presets?purpose=Farm" className="mr-2 rounded-md border border-line px-2 py-1 hover:text-text">
            Farm
          </a>
          <a href="/ai-presets?purpose=Nuke opener" className="mr-2 rounded-md border border-line px-2 py-1 hover:text-text">
            Nuke opener
          </a>
          <a href="/ai-presets?purpose=Sustain" className="rounded-md border border-line px-2 py-1 hover:text-text">
            Sustain
          </a>
        </div>
      </Shell>

      <Shell>
        <div className="grid gap-4 md:grid-cols-2">
          {presets.items.map((preset) => (
            <article key={preset.id} className="rounded-xl border border-line bg-panel p-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-text">{preset.name}</h3>
                <span className="text-xs text-accent">{preset.purpose}</span>
              </div>
              <ul className="mt-3 space-y-1 text-sm text-textSoft">
                {preset.steps.map((step) => (
                  <li key={step}>- {step}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </Shell>
    </main>
  );
}
