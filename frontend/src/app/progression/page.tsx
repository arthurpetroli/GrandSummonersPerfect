import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getProgressionPaths } from "@/lib/api";

interface ProgressionPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function ProgressionPage({ searchParams }: ProgressionPageProps) {
  const params = await searchParams;
  const audience = typeof params.audience === "string" ? params.audience : undefined;

  const paths = await getProgressionPaths({ ...(audience ? { audience } : {}) });

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Progression Planner"
          title="Planner de evolucao"
          subtitle="Defina prioridades de units, equips e conteudos para sair do early e entrar no endgame com eficiencia."
        />
      </Shell>

      <Shell>
        <div className="rounded-xl border border-line bg-panel p-4 text-xs text-textSoft">
          <a href="/progression" className="mr-2 rounded-md border border-line px-2 py-1 hover:text-text">
            Todos
          </a>
          <a href="/progression?audience=Beginner" className="mr-2 rounded-md border border-line px-2 py-1 hover:text-text">
            Beginner
          </a>
          <a href="/progression?audience=Endgame" className="rounded-md border border-line px-2 py-1 hover:text-text">
            Endgame
          </a>
        </div>
      </Shell>

      <Shell>
        <div className="space-y-4">
          {paths.items.map((path) => (
            <article key={path.id} className="rounded-xl border border-line bg-panel p-4">
              <h3 className="text-base font-semibold text-text">{path.title}</h3>
              <p className="mt-1 text-sm text-textSoft">Publico: {path.audience}</p>
              <div className="mt-3 space-y-2">
                {path.steps.map((step, index) => {
                  const s = step as {
                    stage: string;
                    goals: string[];
                    unit_priorities: string[];
                    equip_priorities: string[];
                    content_order: string[];
                  };
                  return (
                    <article key={`${path.id}-${index}`} className="rounded-lg border border-line bg-bgSoft p-3 text-sm text-textSoft">
                      <p className="font-semibold text-text">{s.stage}</p>
                      <p className="mt-1">Objetivos: {s.goals.join(" | ")}</p>
                      <p className="mt-1">Units: {s.unit_priorities.join(", ")}</p>
                      <p className="mt-1">Equips: {s.equip_priorities.join(", ")}</p>
                      <p className="mt-1">Ordem: {s.content_order.join(" > ")}</p>
                    </article>
                  );
                })}
              </div>
            </article>
          ))}
        </div>
      </Shell>
    </main>
  );
}
