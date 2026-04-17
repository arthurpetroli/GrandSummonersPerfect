from statistics import mean
from typing import Dict, List, Optional, Set

from app.data.mock_data import (
    AI_PRESETS,
    BOSSES,
    COMPS,
    EQUIPS,
    GUIDES,
    META_UPDATES,
    MODES,
    PROGRESSION_PATHS,
    TIERLISTS,
    UNITS,
)
from app.models.enums import ContentMode, ServerRegion, TierGrade, UnitRole
from app.models.schemas import (
    AIPreset,
    BossProfile,
    EquipProfile,
    Guide,
    MetaUpdate,
    ModeHubPayload,
    ProgressionPath,
    TeamComp,
    Tierlist,
    TierlistEntry,
    UnitProfile,
)


TIER_ORDER = {
    TierGrade.SSS: 6,
    TierGrade.SS: 5,
    TierGrade.S: 4,
    TierGrade.A: 3,
    TierGrade.B: 2,
    TierGrade.C: 1,
}


REQUIRED_UNIT_TIERLIST_DEFS = [
    ("beginner-unit-tier-list", "Beginner Tier List", "beginner_units", "beginner"),
    ("endgame-unit-tier-list", "Endgame Tier List", "endgame_units", "endgame"),
    ("sustain-unit-tier-list", "Sustain Tier List", "sustain_units", "sustain"),
    ("nuke-unit-tier-list", "Nuke Tier List", "nuke_units", "nuke"),
    ("arena-unit-tier-list", "Arena Tier List", "arena_units", "arena"),
    ("farming-unit-tier-list", "Farming Tier List", "farming_units", "auto"),
    ("bossing-unit-tier-list", "Bossing Tier List", "bossing_units", "endgame"),
]


MODE_TIERLIST_DEFS = [
    (ContentMode.STORY, "Story / Progression Tier List", "story-progression-tier-list"),
    (ContentMode.ARENA, "Arena Tier List", "arena-mode-tier-list"),
    (
        ContentMode.DUNGEON_OF_TRIALS,
        "Dungeon of Trials Tier List",
        "dungeon-of-trials-tier-list",
    ),
    (ContentMode.CREST_PALACE, "Crest Palace Tier List", "crest-palace-tier-list"),
    (
        ContentMode.SUMMONERS_ROAD,
        "Summoners' Road Tier List",
        "summoners-road-tier-list",
    ),
    (ContentMode.MAGICAL_MINES, "Magical Mines Tier List", "magical-mines-tier-list"),
    (ContentMode.GRAND_CRUSADE, "Grand Crusade Tier List", "grand-crusade-tier-list"),
    (ContentMode.RAID, "Raids / Event Bosses Tier List", "raids-event-tier-list"),
    (ContentMode.COLLAB, "Collab Content Tier List", "collab-content-tier-list"),
]


def region_matches(
    entity_region: ServerRegion, selected_region: Optional[ServerRegion]
) -> bool:
    if selected_region is None:
        return True
    if selected_region == ServerRegion.BOTH:
        return True
    return entity_region in (selected_region, ServerRegion.BOTH)


class MemoryRepository:
    def __init__(self) -> None:
        self.units: List[UnitProfile] = [
            UnitProfile.model_validate(item) for item in UNITS
        ]
        self.equips: List[EquipProfile] = [
            EquipProfile.model_validate(item) for item in EQUIPS
        ]
        self.bosses: List[BossProfile] = [
            BossProfile.model_validate(item) for item in BOSSES
        ]
        self.comps: List[TeamComp] = [TeamComp.model_validate(item) for item in COMPS]
        self.tierlists: List[Tierlist] = [
            Tierlist.model_validate(item) for item in TIERLISTS
        ]
        self.guides: List[Guide] = [Guide.model_validate(item) for item in GUIDES]
        self.ai_presets: List[AIPreset] = [
            AIPreset.model_validate(item) for item in AI_PRESETS
        ]
        self.progression_paths: List[ProgressionPath] = [
            ProgressionPath.model_validate(item) for item in PROGRESSION_PATHS
        ]
        self.meta_updates: List[MetaUpdate] = [
            MetaUpdate.model_validate(item) for item in META_UPDATES
        ]
        self.modes: List[Dict[str, object]] = MODES

        self.unit_by_id: Dict[str, UnitProfile] = {u.id: u for u in self.units}
        self.equip_by_id: Dict[str, EquipProfile] = {e.id: e for e in self.equips}
        self.boss_by_id: Dict[str, BossProfile] = {b.id: b for b in self.bosses}
        self.comp_by_id: Dict[str, TeamComp] = {c.id: c for c in self.comps}
        self._ensure_required_tierlists()
        self.tierlist_by_slug: Dict[str, Tierlist] = {t.slug: t for t in self.tierlists}

    def _reindex_units(self) -> None:
        self.unit_by_id = {unit.id: unit for unit in self.units}

    def _reindex_tierlists(self) -> None:
        self.tierlist_by_slug = {tier.slug: tier for tier in self.tierlists}

    def add_or_update_unit(self, unit: UnitProfile) -> UnitProfile:
        for index, existing in enumerate(self.units):
            if existing.id == unit.id or existing.slug == unit.slug:
                self.units[index] = unit
                self._reindex_units()
                return unit

        self.units.append(unit)
        self._reindex_units()
        return unit

    def upsert_tierlist(self, tierlist: Tierlist) -> Tierlist:
        for index, existing in enumerate(self.tierlists):
            if existing.slug == tierlist.slug:
                self.tierlists[index] = tierlist
                self._reindex_tierlists()
                return tierlist

        self.tierlists.append(tierlist)
        self._reindex_tierlists()
        return tierlist

    def _score_to_tier(self, score: float) -> TierGrade:
        if score >= 95:
            return TierGrade.SSS
        if score >= 88:
            return TierGrade.SS
        if score >= 80:
            return TierGrade.S
        if score >= 70:
            return TierGrade.A
        if score >= 60:
            return TierGrade.B
        return TierGrade.C

    def _build_unit_entry_from_focus(
        self,
        unit: UnitProfile,
        focus_key: str,
        mode: Optional[ContentMode] = None,
    ) -> TierlistEntry:
        context_score = float(
            unit.values.get(focus_key, unit.values.get("endgame", 70))
        )
        mode_tier = unit.content_ratings.get(mode) if mode else None
        tier = mode_tier or self._score_to_tier(context_score)

        requires_specific_team = len(unit.team_dependencies) > 0 and context_score < 90
        requires_specific_equips = (
            len(unit.equip_dependencies) > 0 and context_score < 90
        )

        if mode is not None and mode not in unit.content_ratings:
            reason = (
                "Estimated from adjacent content performance due to limited mode-specific "
                "sample size."
            )
        elif focus_key in unit.values:
            reason = f"Strong {focus_key} value with contextual utility coverage and role fit."
        else:
            reason = "Tier estimated from mode context and baseline reliability."

        return TierlistEntry(
            entity_type="unit",
            entity_id=unit.id,
            tier=tier,
            context_score=context_score,
            reason=reason,
            strong_in=list(unit.best_use[:4]),
            weak_in=list(unit.weak_in[:3]),
            dependencies=list(unit.team_dependencies[:3] + unit.equip_dependencies[:2]),
            substitutes=list(unit.substitute_unit_ids[:3]),
            beginner_value=unit.values.get("beginner", 70),
            veteran_value=unit.values.get("endgame", 70),
            ease_of_use=max(
                40,
                min(
                    100,
                    int(
                        mean(
                            [
                                unit.values.get("auto", 70),
                                unit.values.get("beginner", 70),
                            ]
                        )
                    ),
                ),
            ),
            consistency=max(
                40,
                min(
                    100,
                    int(
                        mean(
                            [
                                unit.values.get("sustain", 70),
                                unit.values.get("auto", 70),
                            ]
                        )
                    ),
                ),
            ),
            niche_or_generalist=(
                "niche"
                if unit.values.get("nuke", 0) >= 92
                and unit.values.get("sustain", 0) < 60
                else "generalist"
            ),
            requires_specific_team=requires_specific_team,
            requires_specific_equips=requires_specific_equips,
        )

    def _build_support_entries(self) -> List[TierlistEntry]:
        support_units = [unit for unit in self.units if unit.role == UnitRole.SUPPORT]
        return [
            self._build_unit_entry_from_focus(unit, "sustain") for unit in support_units
        ]

    def _build_equip_entries(self) -> List[TierlistEntry]:
        entries: List[TierlistEntry] = []
        for equip in self.equips:
            context_score = float(
                max(
                    TIER_ORDER.get(equip.ranking_overall, 1) * 16,
                    max(
                        [
                            TIER_ORDER.get(value, 1) * 16
                            for value in equip.ranking_by_context.values()
                        ]
                        or [50]
                    ),
                )
            )

            entries.append(
                TierlistEntry(
                    entity_type="equip",
                    entity_id=equip.id,
                    tier=equip.ranking_overall,
                    context_score=context_score,
                    reason="Tiered by slot impact, cooldown efficiency and context utility.",
                    strong_in=equip.best_use[:4],
                    weak_in=["Outside intended slot archetype"],
                    dependencies=equip.comp_notes[:3],
                    substitutes=equip.substitute_equip_ids[:3],
                    beginner_value=78,
                    veteran_value=92,
                    ease_of_use=85,
                    consistency=88,
                    niche_or_generalist=(
                        "niche"
                        if "nuke" in {tag.lower() for tag in equip.tags}
                        else "generalist"
                    ),
                    requires_specific_team="nuke"
                    in {tag.lower() for tag in equip.tags},
                    requires_specific_equips=False,
                )
            )
        return entries

    def _ensure_required_tierlists(self) -> None:
        existing_slugs = {tier.slug for tier in self.tierlists}

        for slug, title, category, focus in REQUIRED_UNIT_TIERLIST_DEFS:
            if slug in existing_slugs:
                continue
            entries = [
                self._build_unit_entry_from_focus(unit, focus) for unit in self.units
            ]
            self.tierlists.append(
                Tierlist(
                    id=f"tier_{slug}_v1",
                    slug=slug,
                    title=title,
                    mode=None,
                    category=category,
                    version="2026.04",
                    server_region=ServerRegion.BOTH,
                    entries=entries,
                )
            )

        for mode, title, slug in MODE_TIERLIST_DEFS:
            if slug in existing_slugs:
                continue
            mode_units = [unit for unit in self.units if mode in unit.content_ratings]
            if len(mode_units) < 6:
                used_ids = {unit.id for unit in mode_units}
                fallback_units = [
                    unit for unit in self.units if unit.id not in used_ids
                ]
                mode_units.extend(fallback_units)
            entries = [
                self._build_unit_entry_from_focus(unit, "endgame", mode=mode)
                for unit in mode_units
            ]
            self.tierlists.append(
                Tierlist(
                    id=f"tier_{slug}_v1",
                    slug=slug,
                    title=title,
                    mode=mode,
                    category="mode_specific_units",
                    version="2026.04",
                    server_region=ServerRegion.BOTH,
                    entries=entries,
                )
            )

        if "support-unit-tier-list" not in {tier.slug for tier in self.tierlists}:
            self.tierlists.append(
                Tierlist(
                    id="tier_support_unit_tier_list_v1",
                    slug="support-unit-tier-list",
                    title="Support Tier List",
                    mode=None,
                    category="support_units",
                    version="2026.04",
                    server_region=ServerRegion.BOTH,
                    entries=self._build_support_entries(),
                )
            )

        has_any_overall_equip_tierlist = any(
            tier.category == "overall_equips" for tier in self.tierlists
        )
        if not has_any_overall_equip_tierlist:
            self.tierlists.append(
                Tierlist(
                    id="tier_equip_tier_list_v1",
                    slug="equip-tier-list",
                    title="Equip Tier List",
                    mode=None,
                    category="overall_equips",
                    version="2026.04",
                    server_region=ServerRegion.BOTH,
                    entries=self._build_equip_entries(),
                )
            )

    def list_units(
        self,
        server_region: Optional[ServerRegion] = None,
        mode: Optional[ContentMode] = None,
        role: Optional[str] = None,
        element: Optional[str] = None,
        race: Optional[str] = None,
        damage_type: Optional[str] = None,
        slot: Optional[str] = None,
        tier: Optional[str] = None,
        tierlist_slug: Optional[str] = None,
        focus: Optional[str] = None,
        min_value: Optional[int] = None,
        tag: Optional[str] = None,
        tags_any: Optional[List[str]] = None,
        q: Optional[str] = None,
    ) -> List[UnitProfile]:
        result = []
        query_token = q.lower().strip() if q else None
        tags_any_set: Set[str] = {
            candidate.strip().lower()
            for candidate in (tags_any or [])
            if candidate and candidate.strip()
        }

        tier_map: Dict[str, str] = {}
        if tier is not None and tierlist_slug is not None:
            target_tierlist = self.get_tierlist(tierlist_slug)
            if target_tierlist is not None:
                tier_map = {
                    entry.entity_id: entry.tier.value.upper()
                    for entry in target_tierlist.entries
                    if entry.entity_type == "unit"
                }

        for unit in self.units:
            if not region_matches(unit.server_region, server_region):
                continue
            if mode is not None and mode not in unit.content_ratings:
                continue
            if role is not None and unit.role.value.lower() != role.lower():
                continue
            if element is not None and unit.element.lower() != element.lower():
                continue
            if race is not None and unit.race.lower() != race.lower():
                continue
            if (
                damage_type is not None
                and unit.damage_type.value.lower() != damage_type.lower()
            ):
                continue
            if slot is not None and slot.upper() not in {
                s.value for s in unit.equip_slots
            }:
                continue
            if tag is not None and tag.lower() not in {t.lower() for t in unit.tags}:
                continue
            if tags_any_set and not tags_any_set.intersection(
                {candidate.lower() for candidate in unit.tags}
            ):
                continue

            if query_token is not None:
                searchable_chunks = [
                    unit.name,
                    unit.slug,
                    unit.element,
                    unit.race,
                    *unit.tags,
                    *unit.best_use,
                    *unit.weak_in,
                    *unit.passives,
                ]
                if not any(
                    query_token in str(chunk).lower() for chunk in searchable_chunks
                ):
                    continue

            if focus is not None:
                value = unit.values.get(focus.lower())
                if value is None:
                    continue
                if min_value is not None and value < min_value:
                    continue

            if tier is not None:
                normalized_tier = tier.upper()
                if tier_map:
                    if tier_map.get(unit.id) != normalized_tier:
                        continue
                else:
                    if mode is None:
                        continue
                    rating = unit.content_ratings.get(mode)
                    if rating is None or rating.value.upper() != normalized_tier:
                        continue

            result.append(unit)
        return result

    def get_unit(self, unit_id_or_slug: str) -> Optional[UnitProfile]:
        if unit_id_or_slug in self.unit_by_id:
            return self.unit_by_id[unit_id_or_slug]
        for unit in self.units:
            if unit.slug == unit_id_or_slug:
                return unit
        return None

    def list_equips(
        self,
        server_region: Optional[ServerRegion] = None,
        slot_type: Optional[str] = None,
        category: Optional[str] = None,
        max_cooldown: Optional[int] = None,
        min_cooldown: Optional[int] = None,
        tier: Optional[str] = None,
        context: Optional[str] = None,
        tag: Optional[str] = None,
        tags_any: Optional[List[str]] = None,
    ) -> List[EquipProfile]:
        result = []
        tags_any_set: Set[str] = {
            candidate.strip().lower()
            for candidate in (tags_any or [])
            if candidate and candidate.strip()
        }

        for equip in self.equips:
            if not region_matches(equip.server_region, server_region):
                continue
            if (
                slot_type is not None
                and equip.slot_type.value.lower() != slot_type.lower()
            ):
                continue
            if category is not None and equip.category.lower() != category.lower():
                continue
            if max_cooldown is not None and equip.cooldown_seconds > max_cooldown:
                continue
            if min_cooldown is not None and equip.cooldown_seconds < min_cooldown:
                continue
            if tag is not None and tag.lower() not in {
                candidate.lower() for candidate in equip.tags
            }:
                continue
            if tags_any_set and not tags_any_set.intersection(
                {candidate.lower() for candidate in equip.tags}
            ):
                continue

            if tier is not None:
                normalized_tier = tier.upper()
                if context:
                    ctx_tier = equip.ranking_by_context.get(context.lower())
                    if ctx_tier is None or ctx_tier.value.upper() != normalized_tier:
                        continue
                else:
                    if equip.ranking_overall.value.upper() != normalized_tier:
                        continue

            result.append(equip)
        return result

    def get_equip(self, equip_id_or_slug: str) -> Optional[EquipProfile]:
        if equip_id_or_slug in self.equip_by_id:
            return self.equip_by_id[equip_id_or_slug]
        for equip in self.equips:
            if equip.slug == equip_id_or_slug:
                return equip
        return None

    def list_bosses(
        self,
        mode: Optional[ContentMode] = None,
        required_tag: Optional[str] = None,
        required_tags_any: Optional[List[str]] = None,
    ) -> List[BossProfile]:
        tags_any_set: Set[str] = {
            candidate.strip().lower()
            for candidate in (required_tags_any or [])
            if candidate and candidate.strip()
        }

        result: List[BossProfile] = []
        for boss in self.bosses:
            if mode is not None and boss.mode != mode:
                continue
            normalized_required = {tag.lower() for tag in boss.required_tags}
            if (
                required_tag is not None
                and required_tag.lower() not in normalized_required
            ):
                continue
            if tags_any_set and not normalized_required.intersection(tags_any_set):
                continue
            result.append(boss)
        return result

    def get_boss(self, boss_id_or_slug: str) -> Optional[BossProfile]:
        if boss_id_or_slug in self.boss_by_id:
            return self.boss_by_id[boss_id_or_slug]
        for boss in self.bosses:
            if boss.slug == boss_id_or_slug:
                return boss
        return None

    def list_comps(
        self,
        mode: Optional[ContentMode] = None,
        boss_id: Optional[str] = None,
        style: Optional[str] = None,
        beginner_friendly: Optional[bool] = None,
        required_tag: Optional[str] = None,
    ) -> List[TeamComp]:
        result = self.comps
        if mode is not None:
            result = [comp for comp in result if comp.content_mode == mode]
        if boss_id is not None:
            result = [comp for comp in result if comp.target_boss_id == boss_id]
        if style is not None:
            result = [
                comp for comp in result if comp.style.value.lower() == style.lower()
            ]
        if beginner_friendly is not None:
            result = [
                comp
                for comp in result
                if bool(comp.beginner_friendly) is bool(beginner_friendly)
            ]
        if required_tag is not None:
            result = [
                comp
                for comp in result
                if required_tag.lower()
                in {candidate.lower() for candidate in comp.required_tags}
            ]
        return result

    def get_comp(self, comp_id_or_slug: str) -> Optional[TeamComp]:
        if comp_id_or_slug in self.comp_by_id:
            return self.comp_by_id[comp_id_or_slug]
        for comp in self.comps:
            if comp.slug == comp_id_or_slug:
                return comp
        return None

    def list_tierlists(
        self,
        category: Optional[str] = None,
        mode: Optional[ContentMode] = None,
        server_region: Optional[ServerRegion] = None,
    ) -> List[Tierlist]:
        result = self.tierlists
        if category is not None:
            result = [tier for tier in result if tier.category == category]
        if mode is not None:
            result = [tier for tier in result if tier.mode == mode]
        if server_region is not None:
            if server_region == ServerRegion.BOTH:
                return result
            result = [
                tier
                for tier in result
                if tier.server_region in (server_region, ServerRegion.BOTH)
            ]
        return result

    def get_tierlist(self, slug: str) -> Optional[Tierlist]:
        return self.tierlist_by_slug.get(slug)

    def search_global(
        self, query: str, limit: int = 8, server_region: Optional[ServerRegion] = None
    ) -> Dict[str, List[dict]]:
        token = query.lower().strip()
        if not token:
            return {
                "units": [],
                "equips": [],
                "bosses": [],
                "guides": [],
                "comps": [],
            }

        units = [
            {
                "id": unit.id,
                "slug": unit.slug,
                "name": unit.name,
                "type": "unit",
            }
            for unit in self.units
            if token in unit.name.lower()
            and region_matches(unit.server_region, server_region)
        ][:limit]

        equips = [
            {
                "id": equip.id,
                "slug": equip.slug,
                "name": equip.name,
                "type": "equip",
            }
            for equip in self.equips
            if token in equip.name.lower()
            and region_matches(equip.server_region, server_region)
        ][:limit]

        bosses = [
            {
                "id": boss.id,
                "slug": boss.slug,
                "name": boss.stage_name,
                "type": "boss",
            }
            for boss in self.bosses
            if token in boss.name.lower() or token in boss.stage_name.lower()
        ][:limit]

        guides = [
            {
                "id": guide.id,
                "slug": guide.slug,
                "name": guide.title,
                "type": "guide",
            }
            for guide in self.guides
            if token in guide.title.lower() or token in guide.excerpt.lower()
        ][:limit]

        comps = [
            {
                "id": comp.id,
                "slug": comp.slug,
                "name": comp.name,
                "type": "comp",
            }
            for comp in self.comps
            if token in comp.name.lower() or token in comp.summary.lower()
        ][:limit]

        return {
            "units": units,
            "equips": equips,
            "bosses": bosses,
            "guides": guides,
            "comps": comps,
        }

    def get_mode_hub(self, mode: ContentMode) -> ModeHubPayload:
        mode_meta = next((item for item in self.modes if item["mode"] == mode), None)
        if mode_meta is None:
            mode_meta = {
                "slug": mode.value.lower(),
                "name": mode.value,
                "mode": mode,
                "overview": "Mode overview not curated yet.",
            }

        top_units = [
            unit.id
            for unit in sorted(
                [
                    candidate
                    for candidate in self.units
                    if mode in candidate.content_ratings
                ],
                key=lambda item: TIER_ORDER.get(item.content_ratings[mode], 0),
                reverse=True,
            )
        ][:8]

        comp_candidates = self.list_comps(mode=mode)
        important_boss_ids = [boss.id for boss in self.list_bosses(mode=mode)][:6]

        strategy_tips = [
            "Prioritize utility checks before pure damage slots.",
            "Map boss thresholds and align mitigation/cleanse windows.",
            "Use substitutes by role, not only by rarity.",
        ]

        if mode == ContentMode.RAID:
            strategy_tips = [
                "Align burst cooldowns to vulnerability windows.",
                "Use one fallback sustain plan if nuke misses.",
                "Track opener consistency before damage optimization.",
            ]

        if mode == ContentMode.SUMMONERS_ROAD:
            strategy_tips = [
                "Build roster depth for role redundancy.",
                "Cleanse and mitigation generally outvalue greed damage picks.",
                "Treat long-form arts loops as primary win condition.",
            ]

        tierlist_slugs = [
            tier.slug for tier in self.list_tierlists(mode=mode) if tier.mode == mode
        ]
        if not tierlist_slugs:
            tierlist_slugs = [
                tier.slug
                for tier in self.tierlists
                if tier.category.startswith("overall")
            ][:2]

        guide_slugs = [
            guide.slug for guide in self.guides if guide.mode in (mode, None)
        ][:6]

        top_equips = [
            equip.id
            for equip in sorted(
                self.equips,
                key=lambda item: TIER_ORDER.get(item.ranking_overall, 0),
                reverse=True,
            )
        ][:8]

        return ModeHubPayload(
            slug=str(mode_meta["slug"]),
            name=str(mode_meta["name"]),
            mode=mode,
            overview=str(mode_meta["overview"]),
            top_units=top_units,
            top_equips=top_equips,
            common_comp_ids=[comp.id for comp in comp_candidates][:8],
            important_boss_ids=important_boss_ids,
            strategy_tips=strategy_tips,
            tierlist_slugs=tierlist_slugs,
            guide_slugs=guide_slugs,
        )


repo = MemoryRepository()
