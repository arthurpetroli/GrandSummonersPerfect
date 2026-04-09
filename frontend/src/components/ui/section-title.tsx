interface SectionTitleProps {
  eyebrow?: string;
  title: string;
  subtitle?: string;
}

export function SectionTitle({ eyebrow, title, subtitle }: SectionTitleProps) {
  return (
    <div className="space-y-2">
      {eyebrow ? <p className="text-xs uppercase tracking-[0.2em] text-accent">{eyebrow}</p> : null}
      <h2 className="text-2xl font-semibold text-text md:text-3xl">{title}</h2>
      {subtitle ? <p className="max-w-3xl text-sm text-textSoft md:text-base">{subtitle}</p> : null}
    </div>
  );
}
