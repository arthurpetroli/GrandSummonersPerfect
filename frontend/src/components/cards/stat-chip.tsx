interface StatChipProps {
  label: string;
  value: string | number;
}

export function StatChip({ label, value }: StatChipProps) {
  return (
    <div className="rounded-lg border border-line bg-bgSoft px-2 py-1 text-xs text-textSoft">
      <span className="mr-1 text-text">{value}</span>
      {label}
    </div>
  );
}
