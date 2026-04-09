import { ManualClassifier } from "@/components/team-builder/manual-classifier";
import { RecommendationForm } from "@/components/team-builder/recommendation-form";
import { SectionTitle } from "@/components/ui/section-title";
import { Shell } from "@/components/ui/shell";

export default function TeamBuilderPage() {
  return (
    <main>
      <Shell>
        <SectionTitle
          eyebrow="Team Builder"
          title="Monte manualmente ou use sua box"
          subtitle="Valide sinergias, identifique gaps e receba recomendacoes com explicabilidade e substitutes."
        />
      </Shell>

      <Shell>
        <section className="rounded-xl border border-line bg-panel p-4 text-xs text-textSoft">
          <p className="text-text">Modos de uso</p>
          <p>- Modo 1: montar manualmente e validar arquetipo, sinergias, lacunas e conflitos.</p>
          <p>- Modo 2: informar roster para receber comps validas por modo/boss com substitutes e equips.</p>
        </section>
      </Shell>

      <Shell>
        <section className="grid gap-4 lg:grid-cols-2">
          <RecommendationForm />
          <ManualClassifier />
        </section>
      </Shell>
    </main>
  );
}
