"use client";

import { KeyboardEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { getSearchResults } from "@/lib/api";

interface UnitsSearchFormProps {
  initialQ: string;
  sortBy: string;
  sortDir: string;
  pageSize: string;
  includeExternal: boolean;
  currentPage: number;
  serverRegion: string;
  hiddenParams: Record<string, string>;
}

interface Suggestion {
  id: string;
  slug: string;
  name: string;
  source: "local" | "external";
}

function mergeSuggestions(
  units: Array<{ id: string; slug: string; name: string }>,
  externalUnits: Array<{ id: string; slug: string; name: string }>
): Suggestion[] {
  const merged: Suggestion[] = [];
  const seen = new Set<string>();

  for (const item of units) {
    if (seen.has(item.slug)) {
      continue;
    }
    merged.push({ ...item, source: "local" });
    seen.add(item.slug);
  }

  for (const item of externalUnits) {
    if (seen.has(item.slug)) {
      continue;
    }
    merged.push({ ...item, source: "external" });
    seen.add(item.slug);
  }

  return merged.slice(0, 8);
}

export function UnitsSearchForm({
  initialQ,
  sortBy,
  sortDir,
  pageSize,
  includeExternal,
  currentPage,
  serverRegion,
  hiddenParams,
}: UnitsSearchFormProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQ);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const requestRef = useRef(0);

  useEffect(() => {
    setQuery(initialQ);
  }, [initialQ]);

  useEffect(() => {
    const token = query.trim();
    if (token.length < 2) {
      setSuggestions([]);
      setActiveIndex(-1);
      setOpen(false);
      setLoading(false);
      return;
    }

    requestRef.current += 1;
    const requestId = requestRef.current;

    const timer = window.setTimeout(async () => {
      setLoading(true);
      try {
        const results = await getSearchResults({
          q: token,
          server_region: serverRegion || "BOTH",
          limit: "8",
        });

        if (requestRef.current !== requestId) {
          return;
        }

        const merged = mergeSuggestions(results.units ?? [], results.external_units ?? []);
        setSuggestions(merged);
        setActiveIndex(-1);
        setOpen(true);
      } catch {
        if (requestRef.current !== requestId) {
          return;
        }
        setSuggestions([]);
        setActiveIndex(-1);
        setOpen(false);
      } finally {
        if (requestRef.current === requestId) {
          setLoading(false);
        }
      }
    }, 220);

    return () => {
      window.clearTimeout(timer);
    };
  }, [query, serverRegion]);

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (!wrapperRef.current) {
        return;
      }
      if (!wrapperRef.current.contains(event.target as Node)) {
        setOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, []);

  const selectSuggestion = (item: Suggestion) => {
    setOpen(false);
    setActiveIndex(-1);
    router.push(`/units/${item.slug}`);
  };

  const onInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Escape") {
      setOpen(false);
      setActiveIndex(-1);
      return;
    }

    if (!suggestions.length) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);
      setActiveIndex((previous) => (previous + 1) % suggestions.length);
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setOpen(true);
      setActiveIndex((previous) => (previous <= 0 ? suggestions.length - 1 : previous - 1));
      return;
    }

    if (event.key === "Enter" && activeIndex >= 0 && suggestions[activeIndex]) {
      event.preventDefault();
      selectSuggestion(suggestions[activeIndex]);
    }
  };

  return (
    <form action="/units" className="rounded-xl border border-line bg-panel p-4">
      {Object.entries(hiddenParams).map(([key, value]) => (
        <input key={key} type="hidden" name={key} value={value} />
      ))}

      <div className="grid gap-3 md:grid-cols-[1fr_160px_160px_140px]">
        <div ref={wrapperRef} className="relative">
          <input
            name="q"
            value={query}
            onChange={(event) => {
              setQuery(event.target.value);
              if (!open) {
                setOpen(true);
              }
            }}
            onFocus={() => {
              if (suggestions.length > 0) {
                setOpen(true);
              }
            }}
            onKeyDown={onInputKeyDown}
            placeholder="Buscar unit por nome, tag, role, modo..."
            autoComplete="off"
            className="w-full rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
          />

          {open && (loading || suggestions.length > 0) ? (
            <div className="absolute z-20 mt-1 max-h-64 w-full overflow-auto rounded-md border border-line bg-panel p-1 shadow-glow">
              {loading ? <p className="px-2 py-1 text-xs text-textSoft">Buscando...</p> : null}
              {!loading
                ? suggestions.map((item, index) => {
                    const active = index === activeIndex;
                    return (
                      <button
                        key={`${item.source}-${item.id}`}
                        type="button"
                        onMouseDown={(event) => event.preventDefault()}
                        onClick={() => selectSuggestion(item)}
                        className={`flex w-full items-center justify-between rounded px-2 py-2 text-left text-sm ${active ? "bg-accent/15 text-text" : "text-textSoft hover:bg-bgSoft hover:text-text"}`}
                      >
                        <span>{item.name}</span>
                        <span className="rounded border border-line px-1.5 py-0.5 text-[10px] uppercase tracking-wide">
                          {item.source}
                        </span>
                      </button>
                    );
                  })
                : null}
            </div>
          ) : null}
        </div>

        <select
          name="sort_by"
          defaultValue={sortBy}
          className="rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
        >
          <option value="name">Nome</option>
          <option value="beginner">Beginner</option>
          <option value="endgame">Endgame</option>
          <option value="sustain">Sustain</option>
          <option value="nuke">Nuke</option>
          <option value="arena">Arena</option>
          <option value="auto">Auto</option>
          <option value="updated">Atualizacao</option>
        </select>

        <select
          name="sort_dir"
          defaultValue={sortDir}
          className="rounded-md border border-line bg-bgSoft px-3 py-2 text-sm text-text"
        >
          <option value="asc">Asc</option>
          <option value="desc">Desc</option>
        </select>

        <button
          type="submit"
          className="rounded-md border border-accent/60 bg-accent/10 px-3 py-2 text-xs font-semibold text-accent"
        >
          Buscar
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-3 text-xs text-textSoft">
        <label className="inline-flex items-center gap-2">
          <input type="hidden" name="include_external" value="false" />
          <input type="checkbox" name="include_external" value="true" defaultChecked={includeExternal} />
          Incluir units externas
        </label>

        <label className="inline-flex items-center gap-2">
          Page size
          <select
            name="page_size"
            defaultValue={pageSize}
            className="rounded border border-line bg-bgSoft px-2 py-1 text-xs text-text"
          >
            <option value="12">12</option>
            <option value="24">24</option>
            <option value="48">48</option>
          </select>
        </label>

        <label className="inline-flex items-center gap-2">
          <span>Page</span>
          <input
            type="number"
            min={1}
            name="page"
            defaultValue={String(currentPage)}
            className="w-20 rounded border border-line bg-bgSoft px-2 py-1 text-xs text-text"
          />
        </label>
      </div>
    </form>
  );
}
