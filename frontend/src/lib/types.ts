export type ServerRegion = "GLOBAL" | "JP" | "BOTH";
export type ContentMode =
  | "STORY"
  | "ARENA"
  | "DUNGEON_OF_TRIALS"
  | "CREST_PALACE"
  | "SUMMONERS_ROAD"
  | "MAGICAL_MINES"
  | "GRAND_CRUSADE"
  | "RAID"
  | "COLLAB";

export type CompStyle = "SUSTAIN" | "NUKE" | "AUTO_FARM" | "ARENA" | "BREAKER" | "SUPPORT_CENTRIC";

export interface UnitSkill {
  name: string;
  description: string;
  cooldown_seconds?: number | null;
}

export interface UnitProfile {
  id: string;
  slug: string;
  name: string;
  rarity: number;
  element: string;
  race: string;
  role: string;
  damage_type: string;
  equip_slots: string[];
  tags: string[];
  server_region: ServerRegion;
  skill: UnitSkill;
  arts: UnitSkill;
  true_arts: UnitSkill;
  super_arts?: UnitSkill | null;
  passives: string[];
  strengths: string[];
  limitations: string[];
  best_use: string[];
  weak_in: string[];
  team_dependencies: string[];
  equip_dependencies: string[];
  values: Record<string, number>;
  content_ratings: Record<string, string>;
  image_url?: string | null;
  image_thumb_url?: string | null;
  source_updated_at?: string | null;
  source_refs?: string[];
  external_metrics?: Record<string, number>;
}

export interface EquipProfile {
  id: string;
  slug: string;
  name: string;
  slot_type: string;
  category: string;
  cooldown_seconds: number;
  active_skill: string;
  passive: string;
  stats: Record<string, number>;
  tags: string[];
  best_use: string[];
  comp_notes: string[];
  boss_help: string[];
  substitute_equip_ids: string[];
  ranking_overall: string;
  ranking_by_context: Record<string, string>;
  server_region: ServerRegion;
}

export interface TeamComp {
  id: string;
  slug: string;
  name: string;
  content_mode: ContentMode;
  target_boss_id?: string;
  style: CompStyle;
  summary: string;
  why_it_works: string[];
  weaknesses: string[];
  required_tags: string[];
  unit_slots: Array<{
    position: number;
    unit_id: string;
    role_in_comp: string;
    substitutes: string[];
  }>;
  equip_suggestions: Array<{
    unit_id: string;
    equip_ids: string[];
  }>;
  beginner_friendly?: boolean;
}

export interface TierlistEntry {
  entity_type: string;
  entity_id: string;
  entity_name?: string;
  entity_slug?: string | null;
  entity_href?: string | null;
  tier: string;
  context_score: number;
  reason: string;
  strong_in: string[];
  weak_in: string[];
  dependencies: string[];
  substitutes: string[];
  beginner_value: number;
  veteran_value: number;
  ease_of_use: number;
  consistency: number;
  niche_or_generalist: string;
  requires_specific_team?: boolean;
  requires_specific_equips?: boolean;
}

export interface TierlistGroupedEntry {
  entity_type: string;
  entity_id: string;
  entity_name: string;
  entity_slug?: string | null;
  entity_href?: string | null;
  context_score: number;
  reason: string;
  strong_in: string[];
  weak_in: string[];
  dependencies: string[];
  substitutes: string[];
  substitute_entities: Array<{ id: string; name: string; href: string }>;
  beginner_value: number;
  veteran_value: number;
  ease_of_use: number;
  consistency: number;
  niche_or_generalist: string;
  requires_specific_team?: boolean;
  requires_specific_equips?: boolean;
}

export interface TierlistMethodology {
  category: string;
  criteria: string[];
  notes: string[];
}

export interface TierlistChangeLog {
  version: string;
  change: string;
  reason: string;
}

export interface TierlistDetailResponse {
  item: Tierlist;
  grouped_entries: Record<string, TierlistGroupedEntry[]>;
  change_history: TierlistChangeLog[];
  methodology: TierlistMethodology;
}

export interface Tierlist {
  id: string;
  slug: string;
  title: string;
  category: string;
  version: string;
  server_region?: ServerRegion;
  mode?: ContentMode;
  entries: TierlistEntry[];
}

export interface BossMechanic {
  id: string;
  key: string;
  description: string;
  required_utilities: string[];
}

export interface BossProfile {
  id: string;
  slug: string;
  name: string;
  mode: ContentMode;
  stage_name: string;
  difficulty: string;
  overview: string;
  threats: string[];
  resistances: string[];
  gimmicks: string[];
  special_conditions: string[];
  mechanics: BossMechanic[];
  strategy_notes: string[];
  break_recommendation: string;
  required_tags: string[];
  recommended_comp_ids: string[];
}

export interface Guide {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  tags: string[];
  updated_at: string;
  body_markdown?: string;
}

export interface HomePayload {
  hero_message: string;
  featured_tierlists: Tierlist[];
  trending_comps: TeamComp[];
  recent_updates: Array<{ id: string; title: string; summary: string; patch_version: string; published_at: string }>;
  quick_links: Array<{ label: string; href: string }>;
}

export interface TeamRecommendation {
  comp_id: string;
  score: number;
  fit: string;
  reasons: Array<{ label: string; detail: string }>;
  missing_requirements: string[];
  substitutes: Record<string, string[]>;
  strategy_summary: string;
  synergy_notes: string[];
  conflict_notes: string[];
  equip_suggestions: Record<string, string[]>;
}

export interface BossSolverResponse {
  boss_id: string;
  required_utilities: string[];
  answers: Array<{ question: string; answer: string; reason: string }>;
  recommended: Array<{ label: string; comp_ids: string[] }>;
  with_my_box: TeamRecommendation[];
  crest_recommendations: string[];
  equip_recommendations: string[];
  execution_order: string[];
}

export interface ModeHubPayload {
  slug: string;
  name: string;
  mode: ContentMode;
  overview: string;
  top_units: string[];
  top_equips: string[];
  common_comp_ids: string[];
  important_boss_ids: string[];
  strategy_tips: string[];
  tierlist_slugs: string[];
  guide_slugs: string[];
}

export interface ApiCollection<T> {
  items: T[];
  count: number;
}
