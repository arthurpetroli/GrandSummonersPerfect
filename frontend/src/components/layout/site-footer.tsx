export function SiteFooter() {
  return (
    <footer className="mt-12 border-t border-line/70 py-8">
      <div className="container-shell space-y-2 text-xs text-textSoft">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <p>Grand Summoners Companion MVP</p>
          <p>Built for practical decisions: comps, mechanics, substitutes.</p>
        </div>
        <p>
          Este projeto e uma plataforma companion nao oficial da comunidade. Grand Summoners e seus assets pertencem aos respectivos proprietarios.
          Fontes publicas utilizadas para curadoria e referencia incluem guides e sheets comunitarias.
        </p>
      </div>
    </footer>
  );
}
