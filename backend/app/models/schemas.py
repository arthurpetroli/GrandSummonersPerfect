from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.enums import (
    CompStyle,
    ContentMode,
    DamageType,
    EquipSlotType,
    ServerRegion,
    TierGrade,
    UnitRole,
)


class UnitSkill(BaseModel):
    name: str
    description: str
    cooldown_seconds: Optional[int] = None


class UnitProfile(BaseModel):
    id: str
    slug: str
    name: str
    rarity: int
    element: str
    race: str
    role: UnitRole
    damage_type: DamageType
    equip_slots: List[EquipSlotType]
    tags: List[str]
    server_region: ServerRegion
    skill: UnitSkill
    arts: UnitSkill
    true_arts: UnitSkill
    super_arts: Optional[UnitSkill] = None
    passives: List[str]
    strengths: List[str]
    limitations: List[str]
    best_use: List[str]
    weak_in: List[str]
    team_dependencies: List[str]
    equip_dependencies: List[str]
    values: Dict[str, int] = Field(default_factory=dict)
    content_ratings: Dict[ContentMode, TierGrade] = Field(default_factory=dict)
    synergy_units: List[str] = Field(default_factory=list)
    substitute_unit_ids: List[str] = Field(default_factory=list)


class EquipProfile(BaseModel):
    id: str
    slug: str
    name: str
    slot_type: EquipSlotType
    category: str
    cooldown_seconds: int
    active_skill: str
    passive: str
    stats: Dict[str, int]
    tags: List[str]
    best_use: List[str]
    comp_notes: List[str]
    boss_help: List[str]
    substitute_equip_ids: List[str]
    ranking_overall: TierGrade
    ranking_by_context: Dict[str, TierGrade]
    server_region: ServerRegion


class BossMechanic(BaseModel):
    id: str
    key: str
    description: str
    required_utilities: List[str]


class BossProfile(BaseModel):
    id: str
    slug: str
    name: str
    mode: ContentMode
    stage_name: str
    difficulty: str
    overview: str
    threats: List[str]
    resistances: List[str]
    gimmicks: List[str]
    special_conditions: List[str]
    mechanics: List[BossMechanic]
    strategy_notes: List[str]
    break_recommendation: str
    required_tags: List[str]
    recommended_comp_ids: List[str]


class CompUnitSlot(BaseModel):
    position: int
    unit_id: str
    role_in_comp: str
    substitutes: List[str]


class CompEquipSuggestion(BaseModel):
    unit_id: str
    equip_ids: List[str]


class TeamComp(BaseModel):
    id: str
    slug: str
    name: str
    content_mode: ContentMode
    target_boss_id: Optional[str] = None
    style: CompStyle
    summary: str
    why_it_works: List[str]
    weaknesses: List[str]
    required_tags: List[str]
    unit_slots: List[CompUnitSlot]
    equip_suggestions: List[CompEquipSuggestion]
    ai_preset_ids: List[str]
    beginner_friendly: bool = False


class TierlistEntry(BaseModel):
    entity_type: str
    entity_id: str
    tier: TierGrade
    context_score: float
    reason: str
    strong_in: List[str]
    weak_in: List[str]
    dependencies: List[str]
    substitutes: List[str]
    beginner_value: int
    veteran_value: int
    ease_of_use: int
    consistency: int
    niche_or_generalist: str
    requires_specific_team: bool = False
    requires_specific_equips: bool = False


class Tierlist(BaseModel):
    id: str
    slug: str
    title: str
    mode: Optional[ContentMode] = None
    category: str
    version: str
    server_region: ServerRegion
    entries: List[TierlistEntry]


class Guide(BaseModel):
    id: str
    slug: str
    title: str
    excerpt: str
    body_markdown: str
    tags: List[str]
    mode: Optional[ContentMode] = None
    updated_at: str


class AIPreset(BaseModel):
    id: str
    slug: str
    name: str
    purpose: str
    unit_id: Optional[str] = None
    steps: List[str]
    notes: List[str]


class ProgressionStep(BaseModel):
    stage: str
    goals: List[str]
    unit_priorities: List[str]
    equip_priorities: List[str]
    content_order: List[str]
    resource_notes: List[str]


class ProgressionPath(BaseModel):
    id: str
    title: str
    audience: str
    steps: List[ProgressionStep]


class MetaUpdate(BaseModel):
    id: str
    title: str
    summary: str
    patch_version: str
    published_at: str


class HomePayload(BaseModel):
    hero_message: str
    featured_tierlists: List[Tierlist]
    trending_comps: List[TeamComp]
    recent_updates: List[MetaUpdate]
    quick_links: List[Dict[str, str]]


class UserRosterRequest(BaseModel):
    unit_ids: List[str]
    equip_ids: List[str] = Field(default_factory=list)


class TeamBuilderRequest(BaseModel):
    mode: ContentMode
    boss_id: Optional[str] = None
    desired_style: Optional[CompStyle] = None
    roster: UserRosterRequest


class RecommendationReason(BaseModel):
    label: str
    detail: str


class TeamRecommendation(BaseModel):
    comp_id: str
    score: float
    fit: str
    reasons: List[RecommendationReason]
    missing_requirements: List[str]
    substitutes: Dict[str, List[str]]
    strategy_summary: str = ""
    synergy_notes: List[str] = Field(default_factory=list)
    conflict_notes: List[str] = Field(default_factory=list)
    equip_suggestions: Dict[str, List[str]] = Field(default_factory=dict)


class TeamBuilderResponse(BaseModel):
    recommendations: List[TeamRecommendation]


class BossSolverRequest(BaseModel):
    roster: Optional[UserRosterRequest] = None
    desired_style: Optional[CompStyle] = None
    prefer_safe_clear: bool = True


class BossSolverAnswer(BaseModel):
    question: str
    answer: str
    reason: str


class BossSolverCompBucket(BaseModel):
    label: str
    comp_ids: List[str]


class BossSolverResponse(BaseModel):
    boss_id: str
    required_utilities: List[str]
    answers: List[BossSolverAnswer]
    recommended: List[BossSolverCompBucket]
    with_my_box: List[TeamRecommendation]
    crest_recommendations: List[str]
    equip_recommendations: List[str]
    execution_order: List[str]


class ModeHubPayload(BaseModel):
    slug: str
    name: str
    mode: ContentMode
    overview: str
    top_units: List[str]
    top_equips: List[str]
    common_comp_ids: List[str]
    important_boss_ids: List[str]
    strategy_tips: List[str]
    tierlist_slugs: List[str]
    guide_slugs: List[str]
