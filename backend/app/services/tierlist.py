from typing import Dict, List, Optional

from app.repositories.memory_repo import repo


DEFAULT_METHODOLOGY = {
    "overall_units": [
        "General utility and cross-mode viability",
        "Mechanic coverage (cleanse, mitigation, accuracy, art generation)",
        "Consistency, ease of use, and roster accessibility",
    ],
    "mode_specific_units": [
        "Mode-specific mechanic checks",
        "Role compression and slot efficiency",
        "Reliability under scripted boss phases",
    ],
    "overall_equips": [
        "Cooldown efficiency and slot value",
        "Relevance in sustain and nuke contexts",
        "Substitutability and account progression impact",
    ],
}


def _resolve_entity(entity_type: str, entity_id: str) -> Dict[str, Optional[str]]:
    if entity_type == "unit":
        entity = repo.get_unit(entity_id)
        if entity is not None:
            return {
                "entity_name": entity.name,
                "entity_slug": entity.slug,
                "entity_href": f"/units/{entity.slug}",
            }
    if entity_type == "equip":
        entity = repo.get_equip(entity_id)
        if entity is not None:
            return {
                "entity_name": entity.name,
                "entity_slug": entity.slug,
                "entity_href": f"/equips/{entity.slug}",
            }
    if entity_type == "boss":
        entity = repo.get_boss(entity_id)
        if entity is not None:
            return {
                "entity_name": entity.stage_name,
                "entity_slug": entity.slug,
                "entity_href": f"/bosses/{entity.slug}",
            }
    if entity_type == "comp":
        entity = repo.get_comp(entity_id)
        if entity is not None:
            return {
                "entity_name": entity.name,
                "entity_slug": entity.slug,
                "entity_href": f"/comps/{entity.slug}",
            }

    return {
        "entity_name": entity_id,
        "entity_slug": None,
        "entity_href": None,
    }


def _resolve_substitutes(entity_type: str, substitute_ids: List[str]) -> List[Dict[str, str]]:
    resolved_substitutes: List[Dict[str, str]] = []
    for substitute_id in substitute_ids:
        resolved = _resolve_entity(entity_type, substitute_id)
        resolved_substitutes.append(
            {
                "id": substitute_id,
                "name": str(resolved["entity_name"]),
                "href": resolved["entity_href"] or "",
            }
        )
    return resolved_substitutes


def tierlist_change_log(tierlist_slug: str) -> List[Dict[str, str]]:
    tierlist = repo.get_tierlist(tierlist_slug)
    if tierlist is None:
        return []

    return [
        {
            "version": "2026.04",
            "change": f"Refined {tierlist.title} with boss mechanic-weighted context scores.",
            "reason": "Improved weighting for utility coverage (accuracy/cleanse/mitigation).",
        },
        {
            "version": "2026.03",
            "change": "Adjusted nuke-only entries downward in long-form content lists.",
            "reason": "Meta shifted toward consistency after recent stage updates.",
        },
    ]


def group_entries_by_tier(tierlist_slug: str) -> Dict[str, List[Dict[str, object]]]:
    tierlist = repo.get_tierlist(tierlist_slug)
    if tierlist is None:
        return {}

    grouped: Dict[str, List[Dict[str, object]]] = {}
    for entry in tierlist.entries:
        resolved = _resolve_entity(entry.entity_type, entry.entity_id)
        grouped.setdefault(entry.tier.value, []).append(
            {
                "entity_type": entry.entity_type,
                "entity_id": entry.entity_id,
                "tier": entry.tier.value,
                "entity_name": resolved["entity_name"],
                "entity_slug": resolved["entity_slug"],
                "entity_href": resolved["entity_href"],
                "context_score": entry.context_score,
                "reason": entry.reason,
                "strong_in": entry.strong_in,
                "weak_in": entry.weak_in,
                "dependencies": entry.dependencies,
                "substitutes": entry.substitutes,
                "substitute_entities": _resolve_substitutes(
                    entry.entity_type, entry.substitutes
                ),
                "beginner_value": entry.beginner_value,
                "veteran_value": entry.veteran_value,
                "ease_of_use": entry.ease_of_use,
                "consistency": entry.consistency,
                "niche_or_generalist": entry.niche_or_generalist,
                "requires_specific_team": entry.requires_specific_team,
                "requires_specific_equips": entry.requires_specific_equips,
            }
        )

    for tier, entries in grouped.items():
        grouped[tier] = sorted(
            entries,
            key=lambda item: (
                -float(item.get("context_score", 0)),
                str(item.get("entity_name", "")),
            ),
        )

    return grouped


def tierlist_methodology(tierlist_slug: str) -> Dict[str, object]:
    tierlist = repo.get_tierlist(tierlist_slug)
    if tierlist is None:
        return {"criteria": []}

    criteria = DEFAULT_METHODOLOGY.get(
        tierlist.category,
        [
            "Context-aware impact",
            "Reliability and consistency",
            "Accessibility and substitute ecosystem",
        ],
    )

    return {
        "category": tierlist.category,
        "criteria": criteria,
        "notes": [
            "Tier entries are contextual, not absolute rankings.",
            "Substitute quality and equip dependency are reflected in explanations.",
            "Beginner and veteran values are intentionally separated.",
        ],
    }
