from typing import Dict, List, Optional, Set

from app.models.enums import CompStyle
from app.models.schemas import (
    BossSolverAnswer,
    BossSolverCompBucket,
    BossSolverRequest,
    BossSolverResponse,
    RecommendationReason,
    TeamBuilderRequest,
    TeamBuilderResponse,
    TeamComp,
    TeamRecommendation,
)
from app.repositories.memory_repo import repo


def _coverage_tags_for_comp(comp: TeamComp) -> Set[str]:
    tags = set(comp.required_tags)
    for slot in comp.unit_slots:
        unit = repo.get_unit(slot.unit_id)
        if unit is not None:
            tags.update(unit.tags)
    return tags


def _roster_unit_ids(request: TeamBuilderRequest) -> Set[str]:
    return set(request.roster.unit_ids)


def _roster_equip_ids(request: TeamBuilderRequest) -> Set[str]:
    return set(request.roster.equip_ids)


def _match_ratio(comp: TeamComp, roster_ids: Set[str]) -> float:
    needed = [slot.unit_id for slot in comp.unit_slots]
    matched = sum(1 for unit_id in needed if unit_id in roster_ids)
    return matched / max(len(needed), 1)


def _build_substitute_map(comp: TeamComp, roster_ids: Set[str]) -> Dict[str, List[str]]:
    substitutes: Dict[str, List[str]] = {}
    for slot in comp.unit_slots:
        if slot.unit_id in roster_ids:
            continue
        available_subs = [
            candidate for candidate in slot.substitutes if candidate in roster_ids
        ]
        if available_subs:
            substitutes[slot.unit_id] = available_subs
    return substitutes


def _missing_requirements(comp: TeamComp, boss_required_tags: List[str]) -> List[str]:
    coverage = _coverage_tags_for_comp(comp)
    return [tag for tag in boss_required_tags if tag not in coverage]


def _collect_conflicts(comp: TeamComp) -> List[str]:
    coverage = _coverage_tags_for_comp(comp)
    conflicts: List[str] = []

    if "nuke_core" in coverage and "sustain_core" in coverage:
        conflicts.append(
            "Hybrid shell can lose nuke consistency if sustain timings are greedy."
        )
    if "taunt_support" in coverage and "auto_friendly" not in coverage:
        conflicts.append("Taunt timing requires manual control in some auto scenarios.")
    if "cleanse" not in coverage:
        conflicts.append("No built-in cleanse coverage for status-heavy encounters.")

    return conflicts


def _collect_synergies(comp: TeamComp) -> List[str]:
    notes: List[str] = []
    coverage = _coverage_tags_for_comp(comp)

    if "art_gen" in coverage and "mitigation" in coverage:
        notes.append("Arts loop + mitigation creates stable threshold handling.")
    if "nuke_core" in coverage and "debuff" in coverage:
        notes.append("Debuff and burst windows align for high nuke conversion.")
    if "cleanse" in coverage and "status_resist" in coverage:
        notes.append("Status resilience reduces wipe risk in long fights.")

    if not notes:
        notes.append("Role split is balanced, but utility overlap is limited.")

    return notes


def _equip_suggestions_map(
    comp: TeamComp, roster_equip_ids: Set[str]
) -> Dict[str, List[str]]:
    mapped: Dict[str, List[str]] = {}
    for suggestion in comp.equip_suggestions:
        if roster_equip_ids:
            owned = [
                equip_id
                for equip_id in suggestion.equip_ids
                if equip_id in roster_equip_ids
            ]
            fallback = [
                equip_id for equip_id in suggestion.equip_ids if equip_id not in owned
            ]
            mapped[suggestion.unit_id] = owned + fallback
        else:
            mapped[suggestion.unit_id] = suggestion.equip_ids
    return mapped


def _strategy_summary(comp: TeamComp, missing: List[str]) -> str:
    if comp.style == CompStyle.NUKE:
        base = "Focus opener consistency and align burst inside vulnerability windows."
    elif comp.style == CompStyle.SUSTAIN:
        base = "Stabilize arts + mitigation loops, then close with consistent DPS."
    elif comp.style == CompStyle.AUTO_FARM:
        base = "Prioritize safety and repeatability over fastest clear speed."
    else:
        base = "Play around role fidelity and utility timing windows."

    if missing:
        return f"{base} Missing utility: {', '.join(missing)}."
    return base


def recommend_teams(request: TeamBuilderRequest) -> TeamBuilderResponse:
    boss_required_tags: List[str] = []
    if request.boss_id:
        boss = repo.get_boss(request.boss_id)
        if boss:
            boss_required_tags = boss.required_tags

    candidates = repo.list_comps(
        mode=request.mode,
        boss_id=request.boss_id,
        style=request.desired_style.value if request.desired_style else None,
    )
    if not candidates:
        candidates = repo.list_comps(mode=request.mode, boss_id=request.boss_id)
    if not candidates:
        candidates = repo.list_comps(mode=request.mode)

    roster_ids = _roster_unit_ids(request)
    roster_equip_ids = _roster_equip_ids(request)
    recommendations: List[TeamRecommendation] = []

    for comp in candidates:
        ratio = _match_ratio(comp, roster_ids)
        substitutes = _build_substitute_map(comp, roster_ids)
        missing = _missing_requirements(comp, boss_required_tags)

        style_bonus = 0.0
        if request.desired_style and request.desired_style == comp.style:
            style_bonus = 0.12

        beginner_bonus = 0.06 if comp.beginner_friendly else 0.0
        requirement_penalty = 0.1 * len(missing)
        substitute_bonus = min(0.1, 0.04 * len(substitutes))

        score = (
            (ratio * 0.64)
            + style_bonus
            + beginner_bonus
            + substitute_bonus
            - requirement_penalty
        )
        score = max(0.0, min(1.0, score))

        fit = "high"
        if score < 0.75:
            fit = "medium"
        if score < 0.5:
            fit = "low"

        reasons = [
            RecommendationReason(
                label="Roster Fit",
                detail=f"You own {int(ratio * 100)}% of core units for this composition.",
            ),
            RecommendationReason(
                label="Comp Identity",
                detail=f"This team is optimized for {comp.style.value.lower().replace('_', ' ')} play.",
            ),
        ]

        if request.desired_style and request.desired_style == comp.style:
            reasons.append(
                RecommendationReason(
                    label="Style Match",
                    detail="Matches your requested playstyle target.",
                )
            )

        if missing:
            reasons.append(
                RecommendationReason(
                    label="Mechanic Gap",
                    detail=f"Missing boss requirements: {', '.join(missing)}.",
                )
            )
        else:
            reasons.append(
                RecommendationReason(
                    label="Mechanic Coverage",
                    detail="Covers all mandatory boss mechanics for this context.",
                )
            )

        recommendations.append(
            TeamRecommendation(
                comp_id=comp.id,
                score=round(score * 100, 2),
                fit=fit,
                reasons=reasons,
                missing_requirements=missing,
                substitutes=substitutes,
                strategy_summary=_strategy_summary(comp, missing),
                synergy_notes=_collect_synergies(comp),
                conflict_notes=_collect_conflicts(comp),
                equip_suggestions=_equip_suggestions_map(comp, roster_equip_ids),
            )
        )

    recommendations.sort(key=lambda item: item.score, reverse=True)
    return TeamBuilderResponse(recommendations=recommendations)


def explain_comp(comp_id: str, boss_id: Optional[str] = None) -> Dict[str, object]:
    comp = repo.get_comp(comp_id)
    if comp is None:
        return {"error": "comp_not_found"}

    boss_required = []
    if boss_id:
        boss = repo.get_boss(boss_id)
        if boss:
            boss_required = boss.required_tags

    coverage = _coverage_tags_for_comp(comp)
    missing = [tag for tag in boss_required if tag not in coverage]

    return {
        "comp_id": comp.id,
        "why_it_works": comp.why_it_works,
        "conditions": [
            "Correct equip cooldown alignment",
            "Role fidelity per slot",
            "Maintained arts loop in multi-phase fights",
        ],
        "weak_points": comp.weaknesses,
        "missing_boss_requirements": missing,
        "substitute_logic": {
            slot.unit_id: slot.substitutes
            for slot in comp.unit_slots
            if slot.substitutes
        },
        "strategy_summary": _strategy_summary(comp, missing),
        "synergy_notes": _collect_synergies(comp),
        "conflict_notes": _collect_conflicts(comp),
    }


def classify_manual_team(unit_ids: List[str]) -> Dict[str, object]:
    units = [repo.get_unit(unit_id) for unit_id in unit_ids]
    valid_units = [unit for unit in units if unit is not None]

    tag_bag: Set[str] = set()
    roles: Set[str] = set()
    for unit in valid_units:
        tag_bag.update(unit.tags)
        roles.add(unit.role.value.lower())

    has_art = "art_gen" in tag_bag
    has_mit = "mitigation" in tag_bag or "barrier" in tag_bag
    has_nuke = "nuke_core" in tag_bag or "burst_setup" in tag_bag
    has_cleanse = "cleanse" in tag_bag
    has_break = "break" in tag_bag or "breaker" in roles
    has_taunt = "taunt" in tag_bag or "taunt_support" in tag_bag

    archetype = "balanced"
    if has_nuke and not has_mit:
        archetype = "nuke"
    elif has_mit and has_art:
        archetype = "sustain"
    elif has_art and "auto_friendly" in tag_bag:
        archetype = "auto_farm"
    elif has_break:
        archetype = "breaker"

    gaps = []
    if not has_art:
        gaps.append("Missing reliable arts generation")
    if not has_mit:
        gaps.append("Missing mitigation/barrier anchor")
    if not has_cleanse:
        gaps.append("No cleanse coverage for status-heavy bosses")

    strengths = []
    if has_nuke:
        strengths.append("Strong burst potential")
    if has_art:
        strengths.append("Stable arts economy")
    if has_mit:
        strengths.append("Good defensive stability")
    if has_taunt:
        strengths.append("Can route boss pressure with taunt utility")

    conflicts = []
    if archetype == "nuke" and has_mit:
        conflicts.append("Nuke shell may lose tempo if defensive cycles are overused")
    if has_taunt and not has_mit:
        conflicts.append(
            "Taunt without mitigation can be risky in burst threshold fights"
        )

    return {
        "archetype": archetype,
        "strengths": strengths,
        "gaps": gaps,
        "conflicts": conflicts,
        "tag_coverage": sorted(list(tag_bag)),
    }


def _yes_no_answer(required_tags: List[str], tag: str) -> str:
    return "Sim" if tag in required_tags else "Nao"


def _recommended_buckets(comp_ids: List[str]) -> List[BossSolverCompBucket]:
    safe: List[str] = []
    auto_farm: List[str] = []
    nuke: List[str] = []
    budget: List[str] = []

    for comp_id in comp_ids:
        comp = repo.get_comp(comp_id)
        if comp is None:
            continue
        if comp.style == CompStyle.SUSTAIN:
            safe.append(comp.id)
        if comp.style == CompStyle.AUTO_FARM:
            auto_farm.append(comp.id)
        if comp.style == CompStyle.NUKE:
            nuke.append(comp.id)
        if comp.beginner_friendly:
            budget.append(comp.id)

    return [
        BossSolverCompBucket(label="clear_seguro", comp_ids=safe),
        BossSolverCompBucket(label="auto_farm", comp_ids=auto_farm),
        BossSolverCompBucket(label="nuke", comp_ids=nuke),
        BossSolverCompBucket(label="budget", comp_ids=budget),
    ]


def solve_boss(
    boss_id: str,
    payload: Optional[BossSolverRequest] = None,
) -> BossSolverResponse:
    boss = repo.get_boss(boss_id)
    if boss is None:
        raise ValueError("boss_not_found")

    required = boss.required_tags
    answers = [
        BossSolverAnswer(
            question="Preciso de accuracy?",
            answer=_yes_no_answer(required, "accuracy"),
            reason="Boss required tags and mechanics define hit consistency requirements.",
        ),
        BossSolverAnswer(
            question="Preciso de disease?",
            answer=_yes_no_answer(required, "disease"),
            reason="Only needed when disease appears as explicit mechanic check.",
        ),
        BossSolverAnswer(
            question="Preciso de mitigacao?",
            answer=_yes_no_answer(required, "mitigation"),
            reason="Threshold burst and unavoidable damage usually demand mitigation.",
        ),
        BossSolverAnswer(
            question="Preciso de cleanse?",
            answer=_yes_no_answer(required, "cleanse"),
            reason="Status pressure in mechanics and special conditions determines cleanse need.",
        ),
        BossSolverAnswer(
            question="Preciso de taunt?",
            answer=_yes_no_answer(required, "taunt"),
            reason="Taunt is niche and only required in pressure-routing encounters.",
        ),
        BossSolverAnswer(
            question="Vale breakar ou ignorar break?",
            answer="Ignorar break" if "break" not in required else "Break recomendado",
            reason=boss.break_recommendation,
        ),
        BossSolverAnswer(
            question="E melhor sustain ou nuke?",
            answer="Nuke" if "nuke_core" in required else "Sustain",
            reason="Boss vulnerability window and mechanic density guide strategy style.",
        ),
    ]

    recommended_comps = [
        comp
        for comp in [repo.get_comp(comp_id) for comp_id in boss.recommended_comp_ids]
        if comp
    ]

    buckets = _recommended_buckets([comp.id for comp in recommended_comps])

    with_my_box: List[TeamRecommendation] = []
    if payload and payload.roster:
        request = TeamBuilderRequest(
            mode=boss.mode,
            boss_id=boss.id,
            desired_style=payload.desired_style,
            roster=payload.roster,
        )
        with_my_box = recommend_teams(request).recommendations[:4]

    equip_recommendations: List[str] = []
    if required:
        for equip in repo.equips:
            if set(required).intersection({tag.lower() for tag in equip.tags}):
                equip_recommendations.append(equip.id)
    equip_recommendations = equip_recommendations[:8]

    crest_recommendations = [
        "Atk + Crit DMG for nuke finishers",
        "Skill CT down for support loop consistency",
        "Def/HP + Heal amount for safe sustain clears",
    ]

    execution_order = [
        "Open with arts battery and utility equips.",
        "Apply required debuffs/buffs before boss threshold phases.",
        "Hold mitigation/cleanse for scripted burst or status windows.",
        "Spend finisher arts during safe or vulnerability windows.",
    ]

    return BossSolverResponse(
        boss_id=boss.id,
        required_utilities=required,
        answers=answers,
        recommended=buckets,
        with_my_box=with_my_box,
        crest_recommendations=crest_recommendations,
        equip_recommendations=equip_recommendations,
        execution_order=execution_order,
    )
