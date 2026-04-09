import { ReactNode } from "react";

interface FilterBarProps {
  title?: string;
  children: ReactNode;
}

export function FilterBar({ title, children }: FilterBarProps) {
  return (
    <div className="rounded-xl border border-line bg-panel p-3 md:p-4">
      {title ? <p className="mb-2 text-xs uppercase tracking-[0.2em] text-textSoft">{title}</p> : null}
      <div className="flex flex-wrap items-center gap-2">{children}</div>
    </div>
  );
}
