import { GuideCard } from "@/components/cards/guide-card";
import { FilterBar } from "@/components/filters/filter-bar";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getGuides } from "@/lib/api";

interface GuidesPageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function GuidesPage({ searchParams }: GuidesPageProps) {
  const params = await searchParams;
  const mode = typeof params.mode === "string" ? params.mode : undefined;
  const tag = typeof params.tag === "string" ? params.tag : undefined;

  const guides = await getGuides({ ...(mode ? { mode } : {}), ...(tag ? { tag } : {}) });

  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Guides"
          title="Biblioteca editorial"
          subtitle="Guias por progresso, mecanica, modo e estrategia, com curadoria e update historico."
        />
      </Shell>

      <Shell>
        <FilterBar title="Atalhos">
          <a href="/guides" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Todos
          </a>
          <a href="/guides?tag=beginner" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Beginner
          </a>
          <a href="/guides?tag=nuke" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Nuke
          </a>
          <a href="/guides?tag=boss_mechanics" className="rounded-md border border-line px-3 py-1 text-xs text-textSoft hover:text-text">
            Boss Mechanics
          </a>
        </FilterBar>
      </Shell>

      <Shell>
        <div className="grid gap-4 md:grid-cols-2">
          {guides.items.map((guide) => (
            <GuideCard key={guide.id} guide={guide} />
          ))}
        </div>
      </Shell>
    </main>
  );
}
