"use client";

import { FormEvent, useState } from "react";

import { postTeamClassification } from "@/lib/api";

export function ManualClassifier() {
  const [unitIds, setUnitIds] = useState("unit_hart,unit_vox,unit_fen,unit_cestina");
  const [result, setResult] = useState<{
    archetype: string;
    strengths: string[];
    gaps: string[];
    conflicts: string[];
    tag_coverage: string[];
  } | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const ids = unitIds
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    const response = await postTeamClassification({ unit_ids: ids });
    setResult(response);
  }

  return (
    <div className="rounded-xl border border-line bg-panel p-4">
      <h3 className="text-sm font-semibold text-text">Modo manual: validar comp</h3>
      <form onSubmit={onSubmit} className="mt-3 space-y-2">
        <input
          value={unitIds}
          onChange={(event) => setUnitIds(event.target.value)}
          className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
        />
        <button type="submit" className="rounded-md border border-accent/40 bg-accent/10 px-4 py-2 text-sm text-text hover:bg-accent/20">
          Classificar time
        </button>
      </form>

      {result ? (
        <div className="mt-4 space-y-2 text-sm text-textSoft">
          <p>
            Arquitetipo: <span className="text-text">{result.archetype}</span>
          </p>
          <p>Forcas: {result.strengths.join(", ")}</p>
          <p>Lacunas: {result.gaps.join(", ") || "nenhuma"}</p>
          <p>Conflitos: {result.conflicts.join(", ") || "nenhum"}</p>
          <p className="text-xs">Cobertura de tags: {result.tag_coverage.join(", ")}</p>
        </div>
      ) : null}
    </div>
  );
}
