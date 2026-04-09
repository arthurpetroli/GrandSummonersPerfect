from typing import Dict, List

from app.repositories.memory_repo import repo


DEFAULT_METHODLOGY = {
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
        grouped.setdefault(entry.tier.value, []).append(
            {
                "entity_id": entry.entity_id,
                "context_score": entry.context_score,
                "reason": entry.reason,
                "strong_in": entry.strong_in,
                "weak_in": entry.weak_in,
                "dependencies": entry.dependencies,
                "substitutes": entry.substitutes,
                "beginner_value": entry.beginner_value,
                "veteran_value": entry.veteran_value,
                "ease_of_use": entry.ease_of_use,
                "consistency": entry.consistency,
                "niche_or_generalist": entry.niche_or_generalist,
                "requires_specific_team": entry.requires_specific_team,
                "requires_specific_equips": entry.requires_specific_equips,
            }
        )

    return grouped


def tierlist_methodology(tierlist_slug: str) -> Dict[str, object]:
    tierlist = repo.get_tierlist(tierlist_slug)
    if tierlist is None:
        return {"criteria": []}

    criteria = DEFAULT_METHODLOGY.get(
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
