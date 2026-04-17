import math
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.enums import ContentMode, ServerRegion
from app.models.schemas import BossSolverRequest, HomePayload, TeamBuilderRequest
from app.repositories.memory_repo import repo
from app.services.gsinfo_unit_db import (
    get_gsinfo_unit_by_slug,
    has_gsinfo_store,
    search_gsinfo_units,
    sync_gsinfo_unit_database,
)
from app.services.recommendation import (
    classify_manual_team,
    explain_comp,
    recommend_teams,
    solve_boss,
)
from app.services.tierlist import (
    group_entries_by_tier,
    tierlist_change_log,
    tierlist_methodology,
)

router = APIRouter(prefix="/public", tags=["public"])


def _local_unit_to_payload(unit) -> Dict[str, Any]:
    return unit.model_dump(mode="json")


def _external_metric_score(value: float, base: int = 30, scale: int = 30) -> int:
    return max(20, min(100, int(round(base + (value * scale)))))


def _external_values(metrics: Dict[str, float]) -> Dict[str, int]:
    damage = float(metrics.get("damage", 0.0))
    artgen = float(metrics.get("artgen", 0.0))
    buffs = float(metrics.get("buffs", 0.0))
    defense = float(metrics.get("defense", 0.0))
    heal = float(metrics.get("heal", 0.0))
    breaker = float(metrics.get("break", 0.0))

    return {
        "beginner": _external_metric_score((defense + heal + buffs) / 3.0, base=40, scale=22),
        "endgame": _external_metric_score((damage + artgen + buffs) / 3.0, base=38, scale=26),
        "sustain": _external_metric_score((defense + heal + artgen) / 3.0, base=38, scale=24),
        "nuke": _external_metric_score((damage + buffs) / 2.0, base=34, scale=30),
        "auto": _external_metric_score((defense + heal + damage) / 3.0, base=35, scale=24),
        "arena": _external_metric_score((damage + breaker + buffs) / 3.0, base=34, scale=27),
    }


def _external_role(metrics: Dict[str, float]) -> str:
    damage = float(metrics.get("damage", 0.0))
    artgen = float(metrics.get("artgen", 0.0))
    buffs = float(metrics.get("buffs", 0.0))
    defense = float(metrics.get("defense", 0.0))
    heal = float(metrics.get("heal", 0.0))
    breaker = float(metrics.get("break", 0.0))

    if heal >= max(damage, artgen, buffs, defense, breaker) and heal >= 0.9:
        return "HEALER"
    if defense >= max(damage, artgen, buffs, heal, breaker) and defense >= 0.9:
        return "TANK"
    if breaker >= max(damage, artgen, buffs, defense, heal) and breaker >= 0.9:
        return "BREAKER"
    if (artgen + buffs) >= (damage + 0.4):
        return "SUPPORT"
    return "DPS"


def _external_tags(metrics: Dict[str, float]) -> List[str]:
    tags = ["external_source", "gsinfo_imported"]
    if float(metrics.get("artgen", 0.0)) >= 0.8:
        tags.append("art_gen")
    if float(metrics.get("heal", 0.0)) >= 0.8:
        tags.append("heal")
    if float(metrics.get("defense", 0.0)) >= 0.8:
        tags.append("mitigation")
    if float(metrics.get("break", 0.0)) >= 0.8:
        tags.append("break")
    if float(metrics.get("damage", 0.0)) >= 1.0:
        tags.append("dps")
    if float(metrics.get("buffs", 0.0)) >= 0.8:
        tags.append("buff")
    return sorted(set(tags))


def _external_best_use(values: Dict[str, int]) -> List[str]:
    contexts = sorted(values.items(), key=lambda item: item[1], reverse=True)
    result = [name for name, _ in contexts[:3]]
    return result if result else ["pending_curation"]


def _external_unit_to_payload(unit: Dict[str, Any]) -> Dict[str, Any]:
    metrics = unit.get("metrics") or {}
    values = _external_values(metrics)
    role = _external_role(metrics)
    tags = _external_tags(metrics)
    best_use = _external_best_use(values)
    weak_in = [name for name, _ in sorted(values.items(), key=lambda item: item[1])[:2]]

    return {
        "id": unit.get("id"),
        "slug": unit.get("slug"),
        "name": unit.get("name"),
        "rarity": 5,
        "element": unit.get("element") or "Unknown",
        "race": unit.get("race") or "Unknown",
        "role": role,
        "damage_type": "HYBRID",
        "equip_slots": ["SUPPORT", "HEAL", "ARMOR"],
        "tags": tags,
        "server_region": "BOTH",
        "skill": {
            "name": "Skill",
            "description": unit.get("skill") or "No skill data available",
            "cooldown_seconds": None,
        },
        "arts": {
            "name": "Arts",
            "description": unit.get("arts") or "No arts data available",
            "cooldown_seconds": None,
        },
        "true_arts": {
            "name": "True Arts",
            "description": unit.get("true_arts") or "No true arts data available",
            "cooldown_seconds": None,
        },
        "super_arts": None,
        "passives": unit.get("passives") or ["No passive data available"],
        "strengths": unit.get("strengths") or ["No review data available"],
        "limitations": unit.get("limitations") or ["No review data available"],
        "best_use": best_use,
        "weak_in": weak_in,
        "team_dependencies": [],
        "equip_dependencies": [],
        "values": values,
        "content_ratings": {},
        "synergy_units": [],
        "substitute_unit_ids": [],
        "image_url": unit.get("image_url"),
        "image_thumb_url": unit.get("image_thumb_url"),
        "source_updated_at": unit.get("source_updated_at"),
        "source_refs": [unit.get("source_ref")],
        "external_metrics": metrics,
    }


def _unit_sort_value(item: Dict[str, Any], sort_by: str) -> Any:
    if sort_by in {"beginner", "endgame", "sustain", "nuke", "auto", "arena"}:
        return float(item.get("values", {}).get(sort_by, 0))
    if sort_by == "rarity":
        return int(item.get("rarity", 0))
    if sort_by == "updated":
        return str(item.get("source_updated_at") or "")
    if sort_by in {"element", "role", "name"}:
        return str(item.get(sort_by) or "").lower()
    return str(item.get("name") or "").lower()


@router.get("/home", response_model=HomePayload)
def get_home(
    server_region: Optional[ServerRegion] = Query(default=None),
) -> HomePayload:
    featured = repo.list_tierlists(server_region=server_region)[:3]
    trending = repo.list_comps()[:4]
    updates = repo.meta_updates[:6]

    return HomePayload(
        hero_message="Decisions, not spreadsheets: build better teams with context-aware recommendations.",
        featured_tierlists=featured,
        trending_comps=trending,
        recent_updates=updates,
        quick_links=[
            {"label": "Units", "href": "/units"},
            {"label": "Equips", "href": "/equips"},
            {"label": "Boss Solver", "href": "/bosses"},
            {"label": "Team Builder", "href": "/team-builder"},
            {"label": "Tier Lists", "href": "/tierlists"},
            {"label": "Mode Hubs", "href": "/modes"},
            {"label": "Guides", "href": "/guides"},
            {"label": "AI Presets", "href": "/ai-presets"},
            {"label": "Progression", "href": "/progression"},
        ],
    )


@router.get("/search")
def global_search(
    q: str = Query(min_length=1),
    server_region: Optional[ServerRegion] = Query(default=None),
    limit: int = Query(default=8, ge=1, le=50),
) -> dict:
    if not has_gsinfo_store():
        try:
            sync_gsinfo_unit_database()
        except Exception:
            pass

    local_results = repo.search_global(query=q, limit=limit, server_region=server_region)
    gsinfo_units = search_gsinfo_units(query=q, limit=limit)
    return {
        **local_results,
        "external_units": [
            {
                "id": item.get("id"),
                "slug": item.get("slug"),
                "name": item.get("name"),
                "type": "external_unit",
            }
            for item in gsinfo_units
        ],
    }


@router.get("/modes")
def list_modes() -> dict:
    return {"items": repo.modes, "count": len(repo.modes)}


@router.get("/modes/{mode}")
def get_mode_hub(mode: ContentMode) -> dict:
    return {"item": repo.get_mode_hub(mode)}


@router.get("/units")
def list_units(
    server_region: Optional[ServerRegion] = Query(default=None),
    mode: Optional[ContentMode] = Query(default=None),
    role: Optional[str] = Query(default=None),
    element: Optional[str] = Query(default=None),
    race: Optional[str] = Query(default=None),
    damage_type: Optional[str] = Query(default=None),
    slot: Optional[str] = Query(default=None),
    tier: Optional[str] = Query(default=None),
    tierlist_slug: Optional[str] = Query(default=None),
    focus: Optional[str] = Query(default=None),
    min_value: Optional[int] = Query(default=None, ge=0, le=100),
    tag: Optional[str] = Query(default=None),
    tags_any: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    include_external: bool = Query(default=False),
    sort_by: str = Query(default="name"),
    sort_dir: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=24, ge=1, le=100),
) -> dict:
    tags_any_list: List[str] = []
    if tags_any:
        tags_any_list = [
            token.strip() for token in tags_any.split(",") if token.strip()
        ]

    local_units = repo.list_units(
        server_region=server_region,
        mode=mode,
        role=role,
        element=element,
        race=race,
        damage_type=damage_type,
        slot=slot,
        tier=tier,
        tierlist_slug=tierlist_slug,
        focus=focus,
        min_value=min_value,
        tag=tag,
        tags_any=tags_any_list,
        q=q,
    )

    merged_items: List[Dict[str, Any]] = [_local_unit_to_payload(item) for item in local_units]
    source_type: Dict[str, str] = {item["id"]: "local" for item in merged_items}

    if include_external and q:
        if not has_gsinfo_store():
            try:
                sync_gsinfo_unit_database()
            except Exception:
                pass

        for external in search_gsinfo_units(query=q, limit=120):
            payload = _external_unit_to_payload(external)
            if any(item.get("slug") == payload.get("slug") for item in merged_items):
                continue
            merged_items.append(payload)
            source_type[str(payload.get("id"))] = "external"

    reverse_sort = sort_dir.lower() == "desc"
    merged_items.sort(key=lambda item: _unit_sort_value(item, sort_by), reverse=reverse_sort)

    total_count = len(merged_items)
    total_pages = max(1, int(math.ceil(total_count / page_size))) if total_count else 1
    current_page = min(page, total_pages)
    start = (current_page - 1) * page_size
    end = start + page_size
    page_items = merged_items[start:end]

    return {
        "items": page_items,
        "count": total_count,
        "page": current_page,
        "page_size": page_size,
        "total_pages": total_pages,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
        "source_type": {item.get("id"): source_type.get(str(item.get("id")), "local") for item in page_items},
    }


@router.get("/units/{unit_id_or_slug}")
def get_unit(unit_id_or_slug: str) -> dict:
    if not has_gsinfo_store():
        try:
            sync_gsinfo_unit_database()
        except Exception:
            pass

    unit = repo.get_unit(unit_id_or_slug)
    if unit is None:
        external_unit = get_gsinfo_unit_by_slug(unit_id_or_slug)
        if external_unit is None:
            raise HTTPException(status_code=404, detail="unit_not_found")
        return {
            "item": _external_unit_to_payload(external_unit),
            "substitutes": [],
            "synergies": [],
            "external_source": True,
        }
    substitutes = [repo.get_unit(sub) for sub in unit.substitute_unit_ids]
    return {
        "item": unit,
        "substitutes": [sub for sub in substitutes if sub is not None],
        "synergies": [
            repo.get_unit(uid)
            for uid in unit.synergy_units
            if repo.get_unit(uid) is not None
        ],
    }


@router.get("/equips")
def list_equips(
    server_region: Optional[ServerRegion] = Query(default=None),
    slot_type: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    max_cooldown: Optional[int] = Query(default=None, ge=0),
    min_cooldown: Optional[int] = Query(default=None, ge=0),
    tier: Optional[str] = Query(default=None),
    context: Optional[str] = Query(default=None),
    tag: Optional[str] = Query(default=None),
    tags_any: Optional[str] = Query(default=None),
) -> dict:
    tags_any_list: List[str] = []
    if tags_any:
        tags_any_list = [
            token.strip() for token in tags_any.split(",") if token.strip()
        ]

    items = repo.list_equips(
        server_region=server_region,
        slot_type=slot_type,
        category=category,
        max_cooldown=max_cooldown,
        min_cooldown=min_cooldown,
        tier=tier,
        context=context,
        tag=tag,
        tags_any=tags_any_list,
    )
    return {"items": items, "count": len(items)}


@router.get("/equips/{equip_id_or_slug}")
def get_equip(equip_id_or_slug: str) -> dict:
    equip = repo.get_equip(equip_id_or_slug)
    if equip is None:
        raise HTTPException(status_code=404, detail="equip_not_found")
    substitutes = [repo.get_equip(sub) for sub in equip.substitute_equip_ids]
    return {
        "item": equip,
        "substitutes": [sub for sub in substitutes if sub is not None],
    }


@router.get("/bosses")
def list_bosses(
    mode: Optional[ContentMode] = Query(default=None),
    required_tag: Optional[str] = Query(default=None),
    required_tags_any: Optional[str] = Query(default=None),
) -> dict:
    required_tags_any_list: List[str] = []
    if required_tags_any:
        required_tags_any_list = [
            token.strip() for token in required_tags_any.split(",") if token.strip()
        ]

    items = repo.list_bosses(
        mode=mode,
        required_tag=required_tag,
        required_tags_any=required_tags_any_list,
    )
    return {"items": items, "count": len(items)}


@router.get("/bosses/{boss_id_or_slug}")
def get_boss(boss_id_or_slug: str) -> dict:
    boss = repo.get_boss(boss_id_or_slug)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss_not_found")
    recommended = [repo.get_comp(comp_id) for comp_id in boss.recommended_comp_ids]
    return {
        "item": boss,
        "recommended_comps": [comp for comp in recommended if comp is not None],
    }


@router.post("/bosses/{boss_id_or_slug}/solve")
def solve_boss_route(
    boss_id_or_slug: str,
    payload: Optional[BossSolverRequest] = None,
) -> dict:
    boss = repo.get_boss(boss_id_or_slug)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss_not_found")

    try:
        response = solve_boss(boss.id, payload)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return response.model_dump()


@router.get("/comps")
def list_comps(
    mode: Optional[ContentMode] = Query(default=None),
    boss_id: Optional[str] = Query(default=None),
    style: Optional[str] = Query(default=None),
    beginner_friendly: Optional[bool] = Query(default=None),
    required_tag: Optional[str] = Query(default=None),
) -> dict:
    items = repo.list_comps(
        mode=mode,
        boss_id=boss_id,
        style=style,
        beginner_friendly=beginner_friendly,
        required_tag=required_tag,
    )
    return {"items": items, "count": len(items)}


@router.get("/comps/{comp_id_or_slug}")
def get_comp(
    comp_id_or_slug: str, boss_id: Optional[str] = Query(default=None)
) -> dict:
    comp = repo.get_comp(comp_id_or_slug)
    if comp is None:
        raise HTTPException(status_code=404, detail="comp_not_found")
    explanation = explain_comp(comp.id, boss_id=boss_id)
    return {"item": comp, "explanation": explanation}


@router.get("/tierlists")
def list_tierlists(
    category: Optional[str] = Query(default=None),
    mode: Optional[ContentMode] = Query(default=None),
    server_region: Optional[ServerRegion] = Query(default=None),
) -> dict:
    items = repo.list_tierlists(
        category=category,
        mode=mode,
        server_region=server_region,
    )
    return {"items": items, "count": len(items)}


@router.get("/tierlists/{slug}")
def get_tierlist(slug: str) -> dict:
    tier = repo.get_tierlist(slug)
    if tier is None:
        raise HTTPException(status_code=404, detail="tierlist_not_found")
    return {
        "item": tier,
        "grouped_entries": group_entries_by_tier(slug),
        "change_history": tierlist_change_log(slug),
        "methodology": tierlist_methodology(slug),
    }


@router.get("/guides")
def list_guides(
    mode: Optional[ContentMode] = Query(default=None),
    tag: Optional[str] = Query(default=None),
) -> dict:
    items = repo.guides
    if mode is not None:
        items = [guide for guide in items if guide.mode == mode]
    if tag is not None:
        items = [
            guide
            for guide in items
            if tag.lower() in {candidate.lower() for candidate in guide.tags}
        ]
    return {"items": items, "count": len(items)}


@router.get("/guides/{slug}")
def get_guide(slug: str) -> dict:
    for guide in repo.guides:
        if guide.slug == slug:
            return {"item": guide}
    raise HTTPException(status_code=404, detail="guide_not_found")


@router.get("/ai-presets")
def list_ai_presets(
    unit_id: Optional[str] = Query(default=None),
    purpose: Optional[str] = Query(default=None),
) -> dict:
    items = repo.ai_presets
    if unit_id is not None:
        items = [preset for preset in items if preset.unit_id in (unit_id, None)]
    if purpose is not None:
        items = [
            preset
            for preset in items
            if preset.purpose.lower().replace("_", " ")
            == purpose.lower().replace("_", " ")
        ]
    return {"items": items, "count": len(items)}


@router.get("/progression-paths")
def list_progression_paths(audience: Optional[str] = Query(default=None)) -> dict:
    items = repo.progression_paths
    if audience is not None:
        items = [item for item in items if audience.lower() in item.audience.lower()]
    return {"items": items, "count": len(items)}


@router.post("/team-builder/recommend")
def team_builder_recommend(payload: TeamBuilderRequest) -> dict:
    response = recommend_teams(payload)
    return response.model_dump()


@router.post("/team-builder/classify")
def team_builder_classify(payload: dict) -> dict:
    unit_ids = payload.get("unit_ids", [])
    if not isinstance(unit_ids, list):
        raise HTTPException(status_code=422, detail="unit_ids_must_be_array")
    return classify_manual_team(unit_ids)


@router.get("/meta/updates")
def list_meta_updates(
    server_region: Optional[ServerRegion] = Query(default=None),
) -> dict:
    items = repo.meta_updates
    if server_region is not None:
        if server_region == ServerRegion.GLOBAL:
            items = [item for item in items if item.patch_version.startswith("GL")]
        elif server_region == ServerRegion.JP:
            items = [item for item in items if item.patch_version.startswith("JP")]
    return {"items": items, "count": len(items)}
