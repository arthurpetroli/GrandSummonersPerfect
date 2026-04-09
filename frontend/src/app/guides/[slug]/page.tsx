import { notFound } from "next/navigation";

import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";
import { getGuide } from "@/lib/api";

interface GuideDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default async function GuideDetailPage({ params }: GuideDetailPageProps) {
  const { slug } = await params;

  try {
    const { item } = await getGuide(slug);
    return (
      <main>
        <Shell>
          <SectionTitle eyebrow="Guide" title={item.title} subtitle={item.excerpt} />
        </Shell>

        <Shell>
          <article className="rounded-xl border border-line bg-panel p-4 md:p-6">
            <div className="mb-4 flex flex-wrap gap-1">
              {item.tags.map((tag) => (
                <span key={tag} className="rounded-md border border-line px-2 py-0.5 text-[10px] uppercase tracking-wide text-textSoft">
                  {tag}
                </span>
              ))}
            </div>
            <pre className="whitespace-pre-wrap text-sm leading-7 text-textSoft">{item.body_markdown ?? "Conteudo em atualizacao."}</pre>
          </article>
        </Shell>
      </main>
    );
  } catch {
    notFound();
  }
}
