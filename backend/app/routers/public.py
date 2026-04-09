from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.enums import ContentMode, ServerRegion
from app.models.schemas import BossSolverRequest, HomePayload, TeamBuilderRequest
from app.repositories.memory_repo import repo
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
    return repo.search_global(query=q, limit=limit, server_region=server_region)


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
) -> dict:
    tags_any_list: List[str] = []
    if tags_any:
        tags_any_list = [
            token.strip() for token in tags_any.split(",") if token.strip()
        ]

    items = repo.list_units(
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
    )
    return {"items": items, "count": len(items)}


@router.get("/units/{unit_id_or_slug}")
def get_unit(unit_id_or_slug: str) -> dict:
    unit = repo.get_unit(unit_id_or_slug)
    if unit is None:
        raise HTTPException(status_code=404, detail="unit_not_found")
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
