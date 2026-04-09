"use client";

import { FormEvent, useState } from "react";

import { postTeamRecommendations } from "@/lib/api";
import { TeamRecommendation } from "@/lib/types";

const DEFAULT_UNITS = "unit_hart,unit_cestina,unit_vox,unit_fen";
const DEFAULT_EQUIPS = "equip_true_flambardo,equip_lesser_demonheart,equip_goku_uniform";

export function RecommendationForm() {
  const [mode, setMode] = useState("CREST_PALACE");
  const [bossId, setBossId] = useState("boss_crest_nova_ashdrake");
  const [desiredStyle, setDesiredStyle] = useState("SUSTAIN");
  const [unitsRaw, setUnitsRaw] = useState(DEFAULT_UNITS);
  const [equipsRaw, setEquipsRaw] = useState(DEFAULT_EQUIPS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ recommendations: TeamRecommendation[] } | null>(null);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const unit_ids = unitsRaw
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);

    const equip_ids = equipsRaw
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);

    try {
      const response = await postTeamRecommendations({
        mode,
        boss_id: bossId,
        desired_style: desiredStyle,
        roster: {
          unit_ids,
          equip_ids,
        },
      });
      setResult(response);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Falha ao gerar recomendacoes");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={onSubmit} className="rounded-xl border border-line bg-panel p-4">
        <div className="grid gap-3 md:grid-cols-2">
          <label className="space-y-1 text-xs text-textSoft">
            Modo
            <select
              value={mode}
              onChange={(event) => setMode(event.target.value)}
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            >
              <option value="CREST_PALACE">Crest Palace</option>
              <option value="SUMMONERS_ROAD">Summoners Road</option>
              <option value="RAID">Raid</option>
              <option value="ARENA">Arena</option>
            </select>
          </label>

          <label className="space-y-1 text-xs text-textSoft">
            Estilo desejado
            <select
              value={desiredStyle}
              onChange={(event) => setDesiredStyle(event.target.value)}
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            >
              <option value="SUSTAIN">Sustain</option>
              <option value="NUKE">Nuke</option>
              <option value="AUTO_FARM">Auto Farm</option>
              <option value="BREAKER">Breaker</option>
              <option value="SUPPORT_CENTRIC">Support-centric</option>
            </select>
          </label>

          <label className="space-y-1 text-xs text-textSoft md:col-span-2">
            Boss ID (MVP)
            <input
              value={bossId}
              onChange={(event) => setBossId(event.target.value)}
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            />
          </label>

          <label className="space-y-1 text-xs text-textSoft md:col-span-2">
            Sua box de units (IDs separados por virgula)
            <input
              value={unitsRaw}
              onChange={(event) => setUnitsRaw(event.target.value)}
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            />
          </label>

          <label className="space-y-1 text-xs text-textSoft md:col-span-2">
            Seus equips (IDs separados por virgula)
            <input
              value={equipsRaw}
              onChange={(event) => setEquipsRaw(event.target.value)}
              className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-4 rounded-md border border-accent/40 bg-accent/10 px-4 py-2 text-sm text-text transition hover:bg-accent/20 disabled:opacity-60"
        >
          {loading ? "Calculando..." : "Recomendar composicoes"}
        </button>
      </form>

      {error ? <p className="text-sm text-red-300">{error}</p> : null}

      {result ? (
        <section className="space-y-3">
          {result.recommendations.map((item) => (
            <article key={item.comp_id} className="rounded-xl border border-line bg-panel p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-text">{item.comp_id}</p>
                <p className="text-xs text-accent">
                  Score {item.score} | Fit {item.fit}
                </p>
              </div>

              <p className="mt-2 text-xs text-text">{item.strategy_summary}</p>

              <ul className="mt-2 space-y-1 text-xs text-textSoft">
                {item.reasons.map((reason) => (
                  <li key={reason.label}>
                    - {reason.label}: {reason.detail}
                  </li>
                ))}
              </ul>

              {item.synergy_notes.length ? (
                <p className="mt-2 text-xs text-emerald-300">Synergy: {item.synergy_notes.join(" | ")}</p>
              ) : null}

              {item.conflict_notes.length ? (
                <p className="mt-2 text-xs text-yellow-300">Conflitos: {item.conflict_notes.join(" | ")}</p>
              ) : null}

              {item.missing_requirements.length ? (
                <p className="mt-2 text-xs text-red-300">Missing: {item.missing_requirements.join(", ")}</p>
              ) : null}

              {Object.keys(item.equip_suggestions).length ? (
                <div className="mt-2 text-xs text-textSoft">
                  {Object.entries(item.equip_suggestions).map(([unitId, equips]) => (
                    <p key={unitId}>
                      - Equips {unitId}: {equips.join(", ")}
                    </p>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </section>
      ) : null}
    </div>
  );
}
