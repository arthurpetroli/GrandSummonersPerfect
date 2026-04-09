import {
  ApiCollection,
  BossProfile,
  BossSolverResponse,
  EquipProfile,
  Guide,
  HomePayload,
  ModeHubPayload,
  TeamComp,
  TeamRecommendation,
  Tierlist,
  UnitProfile,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const API_PREFIX = "/api/v1/public";
const USE_DYNAMIC_FETCH = API_BASE.includes("localhost") || API_BASE.includes("127.0.0.1");

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${API_PREFIX}${path}`, {
    ...(USE_DYNAMIC_FETCH ? { cache: "no-store" as const } : { next: { revalidate: 120 } }),
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API error ${response.status} for ${path}`);
  }
  return response.json() as Promise<T>;
}

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  return fetchJson<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });
}

export async function getHome(params?: Record<string, string>): Promise<HomePayload> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<HomePayload>(`/home${query}`);
}

export async function getSearchResults(params: Record<string, string>): Promise<{
  units: Array<{ id: string; slug: string; name: string; type: string }>;
  equips: Array<{ id: string; slug: string; name: string; type: string }>;
  bosses: Array<{ id: string; slug: string; name: string; type: string }>;
  guides: Array<{ id: string; slug: string; name: string; type: string }>;
  comps: Array<{ id: string; slug: string; name: string; type: string }>;
}> {
  const query = `?${new URLSearchParams(params).toString()}`;
  return fetchJson(`/search${query}`);
}

export async function getUnits(params?: Record<string, string>): Promise<ApiCollection<UnitProfile>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<ApiCollection<UnitProfile>>(`/units${query}`);
}

export async function getUnit(slug: string): Promise<{ item: UnitProfile; substitutes: UnitProfile[]; synergies: UnitProfile[] }> {
  return fetchJson<{ item: UnitProfile; substitutes: UnitProfile[]; synergies: UnitProfile[] }>(`/units/${slug}`);
}

export async function getEquip(slug: string): Promise<{ item: EquipProfile; substitutes: EquipProfile[] }> {
  return fetchJson<{ item: EquipProfile; substitutes: EquipProfile[] }>(`/equips/${slug}`);
}

export async function getEquips(params?: Record<string, string>): Promise<ApiCollection<EquipProfile>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<ApiCollection<EquipProfile>>(`/equips${query}`);
}

export async function getBosses(params?: Record<string, string>): Promise<ApiCollection<BossProfile>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<ApiCollection<BossProfile>>(`/bosses${query}`);
}

export async function getBoss(slug: string): Promise<{ item: BossProfile; recommended_comps: TeamComp[] }> {
  return fetchJson<{ item: BossProfile; recommended_comps: TeamComp[] }>(`/bosses/${slug}`);
}

export async function postBossSolver(
  slug: string,
  payload?: {
    desired_style?: string;
    prefer_safe_clear?: boolean;
    roster?: {
      unit_ids: string[];
      equip_ids?: string[];
    };
  }
): Promise<BossSolverResponse> {
  return postJson(`/bosses/${slug}/solve`, payload ?? {});
}

export async function getComps(params?: Record<string, string>): Promise<ApiCollection<TeamComp>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<ApiCollection<TeamComp>>(`/comps${query}`);
}

export async function getComp(slug: string): Promise<{ item: TeamComp; explanation: Record<string, unknown> }> {
  return fetchJson<{ item: TeamComp; explanation: Record<string, unknown> }>(`/comps/${slug}`);
}

export async function getTierlists(params?: Record<string, string>): Promise<ApiCollection<Tierlist>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<ApiCollection<Tierlist>>(`/tierlists${query}`);
}

export async function getTierlist(slug: string): Promise<{
  item: Tierlist;
  grouped_entries: Record<string, Array<Record<string, unknown>>>;
  change_history: Array<{ version: string; change: string; reason: string }>;
  methodology: {
    category: string;
    criteria: string[];
    notes: string[];
  };
}> {
  return fetchJson(`/tierlists/${slug}`);
}

export async function getGuides(params?: Record<string, string>): Promise<ApiCollection<Guide>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson<ApiCollection<Guide>>(`/guides${query}`);
}

export async function getGuide(slug: string): Promise<{ item: Guide }> {
  return fetchJson<{ item: Guide }>(`/guides/${slug}`);
}

export async function postTeamRecommendations(payload: unknown): Promise<{
  recommendations: TeamRecommendation[];
}> {
  return postJson("/team-builder/recommend", payload);
}

export async function postTeamClassification(payload: { unit_ids: string[] }): Promise<{
  archetype: string;
  strengths: string[];
  gaps: string[];
  conflicts: string[];
  tag_coverage: string[];
}> {
  return postJson("/team-builder/classify", payload);
}

export async function getProgressionPaths(
  params?: Record<string, string>
): Promise<ApiCollection<{ id: string; title: string; audience: string; steps: unknown[] }>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson(`/progression-paths${query}`);
}

export async function getAIPresets(
  params?: Record<string, string>
): Promise<ApiCollection<{ id: string; slug: string; name: string; purpose: string; steps: string[]; notes: string[] }>> {
  const query = params ? `?${new URLSearchParams(params).toString()}` : "";
  return fetchJson(`/ai-presets${query}`);
}

export async function getModes(): Promise<ApiCollection<{ slug: string; name: string; mode: string; overview: string }>> {
  return fetchJson("/modes");
}

export async function getModeHub(mode: string): Promise<{ item: ModeHubPayload }> {
  return fetchJson(`/modes/${mode}`);
}

export async function getAdminOverview(): Promise<{
  counts: Record<string, number>;
  pending_reviews: Record<string, number>;
}> {
  const response = await fetch(`${API_BASE}/api/v1/admin/overview`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch admin overview");
  }
  return response.json();
}

export async function getAdminReviewQueue(): Promise<{ items: Array<Record<string, unknown>> }> {
  const response = await fetch(`${API_BASE}/api/v1/admin/review-queue`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch admin review queue");
  }
  return response.json();
}

export async function getAdminSources(): Promise<{ items: Array<Record<string, unknown>>; count: number }> {
  const response = await fetch(`${API_BASE}/api/v1/admin/sources`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch admin sources");
  }
  return response.json();
}

export async function getAdminEditorialHistory(): Promise<{ items: Array<Record<string, unknown>>; count: number }> {
  const response = await fetch(`${API_BASE}/api/v1/admin/editorial-history`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch admin editorial history");
  }
  return response.json();
}
