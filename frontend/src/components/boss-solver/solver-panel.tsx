"use client";

import { FormEvent, useState } from "react";

import { postBossSolver } from "@/lib/api";
import { BossSolverResponse } from "@/lib/types";

interface SolverPanelProps {
  bossSlug: string;
}

export function SolverPanel({ bossSlug }: SolverPanelProps) {
  const [unitsRaw, setUnitsRaw] = useState("unit_hart,unit_cestina,unit_vox,unit_fen");
  const [equipsRaw, setEquipsRaw] = useState("equip_true_flambardo,equip_lesser_demonheart");
  const [style, setStyle] = useState("SUSTAIN");
  const [result, setResult] = useState<BossSolverResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);

    const unit_ids = unitsRaw
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    const equip_ids = equipsRaw
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);

    try {
      const response = await postBossSolver(bossSlug, {
        desired_style: style,
        prefer_safe_clear: true,
        roster: {
          unit_ids,
          equip_ids,
        },
      });
      setResult(response);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-xl border border-line bg-panel p-4">
      <h3 className="text-sm font-semibold text-text">Boss Solver - com minha box</h3>
      <form onSubmit={onSubmit} className="mt-3 space-y-2">
        <select
          value={style}
          onChange={(event) => setStyle(event.target.value)}
          className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
        >
          <option value="SUSTAIN">Sustain</option>
          <option value="NUKE">Nuke</option>
          <option value="AUTO_FARM">Auto Farm</option>
        </select>

        <input
          value={unitsRaw}
          onChange={(event) => setUnitsRaw(event.target.value)}
          className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
          placeholder="Units IDs"
        />

        <input
          value={equipsRaw}
          onChange={(event) => setEquipsRaw(event.target.value)}
          className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
          placeholder="Equip IDs"
        />

        <button
          type="submit"
          disabled={loading}
          className="rounded-md border border-accent/40 bg-accent/10 px-4 py-2 text-sm text-text hover:bg-accent/20 disabled:opacity-60"
        >
          {loading ? "Analisando..." : "Resolver boss"}
        </button>
      </form>

      {result ? (
        <div className="mt-4 space-y-3 text-sm text-textSoft">
          <p className="text-xs text-accent">Utilidades: {result.required_utilities.join(", ")}</p>

          <div className="space-y-1">
            {result.answers.map((answer) => (
              <p key={answer.question}>
                - {answer.question} <span className="text-text">{answer.answer}</span>
              </p>
            ))}
          </div>

          <div className="space-y-1">
            {result.recommended.map((bucket) => (
              <p key={bucket.label}>
                - {bucket.label}: {bucket.comp_ids.join(", ") || "sem comp dedicada"}
              </p>
            ))}
          </div>

          <div className="space-y-1">
            {result.with_my_box.map((item) => (
              <p key={item.comp_id}>
                - Box fit {item.comp_id}: {item.score}
              </p>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}
