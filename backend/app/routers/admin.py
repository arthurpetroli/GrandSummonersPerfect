from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.enums import ContentMode
from app.repositories.memory_repo import repo

router = APIRouter(prefix="/admin", tags=["admin"])


def _staged_response(entity: str, entity_id: str, payload: dict) -> dict:
    return {
        "status": "staged",
        "entity": entity,
        "id": entity_id,
        "changes": payload,
        "workflow": ["staged", "review", "publish"],
    }


@router.get("/overview")
def admin_overview() -> dict:
    return {
        "counts": {
            "units": len(repo.units),
            "equips": len(repo.equips),
            "bosses": len(repo.bosses),
            "comps": len(repo.comps),
            "tierlists": len(repo.tierlists),
            "guides": len(repo.guides),
            "ai_presets": len(repo.ai_presets),
            "progression_paths": len(repo.progression_paths),
        },
        "pending_reviews": {
            "community_comps": 2,
            "tierlist_changes": 1,
            "source_imports": 3,
            "guide_updates": 2,
        },
    }


@router.get("/review-queue")
def admin_review_queue() -> dict:
    return {
        "items": [
            {
                "id": "rq_comp_001",
                "type": "community_comp",
                "title": "Ashdrake Speed Variant",
                "status": "pending",
                "submitted_by": "user_community_41",
            },
            {
                "id": "rq_tier_004",
                "type": "tier_update",
                "title": "Arena list adjustment",
                "status": "pending",
                "submitted_by": "editor_luna",
            },
            {
                "id": "rq_guide_011",
                "type": "guide_update",
                "title": "Road cleanse strategy refresh",
                "status": "pending",
                "submitted_by": "editor_aria",
            },
        ]
    }


@router.post("/publish")
def admin_publish(payload: dict) -> dict:
    entity_type = payload.get("entity_type")
    entity_id = payload.get("entity_id")
    source_ids = payload.get("source_ids", [])
    if not entity_type or not entity_id:
        raise HTTPException(
            status_code=422, detail="entity_type_and_entity_id_required"
        )
    return {
        "status": "published",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "source_ids": source_ids,
        "published_at": "2026-04-08T10:00:00Z",
        "editorial_history": {
            "author": payload.get("author", "system"),
            "reviewer": payload.get("reviewer", "system"),
            "change_notes": payload.get("change_notes", []),
        },
    }


@router.get("/sources")
def list_sources(kind: Optional[str] = Query(default=None)) -> dict:
    sources = [
        {
            "id": "src_gsinfo",
            "kind": "website",
            "name": "Grand Summoners Info",
            "url": "https://www.grandsummoners.info/",
            "last_synced_at": "2026-04-01",
        },
        {
            "id": "src_sheet_tier",
            "kind": "google_sheet",
            "name": "Community Tier Sheet",
            "url": "https://docs.google.com/spreadsheets/...",
            "last_synced_at": "2026-04-02",
        },
    ]
    if kind is not None:
        sources = [item for item in sources if item["kind"] == kind]
    return {"items": sources, "count": len(sources)}


@router.get("/source-mappings")
def list_source_mappings(entity_type: Optional[str] = Query(default=None)) -> dict:
    mappings = [
        {
            "id": "map_001",
            "source_id": "src_sheet_tier",
            "entity_type": "tierlist_entry",
            "entity_id": "unit_hart",
            "validation_status": "approved",
            "published": True,
            "updated_at": "2026-04-04",
        },
        {
            "id": "map_002",
            "source_id": "src_gsinfo",
            "entity_type": "unit",
            "entity_id": "unit_vox",
            "validation_status": "pending",
            "published": False,
            "updated_at": "2026-04-05",
        },
    ]
    if entity_type is not None:
        mappings = [item for item in mappings if item["entity_type"] == entity_type]
    return {"items": mappings, "count": len(mappings)}


@router.post("/sources/import")
def import_source(payload: dict) -> dict:
    return {
        "status": "queued",
        "job": "ingestion_import",
        "source_id": payload.get("source_id"),
        "entity_type": payload.get("entity_type"),
        "started_at": "2026-04-08T10:00:00Z",
        "pipeline": ["raw_source", "normalization", "validation", "publish"],
    }


@router.get("/units")
def admin_list_units(mode: Optional[ContentMode] = Query(default=None)) -> dict:
    items = repo.list_units(mode=mode)
    return {"items": items, "count": len(items)}


@router.patch("/units/{unit_id}")
def admin_patch_unit(unit_id: str, payload: dict) -> dict:
    unit = repo.get_unit(unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="unit_not_found")
    return _staged_response("unit", unit_id, payload)


@router.get("/equips")
def admin_list_equips() -> dict:
    return {"items": repo.equips, "count": len(repo.equips)}


@router.patch("/equips/{equip_id}")
def admin_patch_equip(equip_id: str, payload: dict) -> dict:
    equip = repo.get_equip(equip_id)
    if equip is None:
        raise HTTPException(status_code=404, detail="equip_not_found")
    return _staged_response("equip", equip_id, payload)


@router.get("/bosses")
def admin_list_bosses() -> dict:
    return {"items": repo.bosses, "count": len(repo.bosses)}


@router.patch("/bosses/{boss_id}")
def admin_patch_boss(boss_id: str, payload: dict) -> dict:
    boss = repo.get_boss(boss_id)
    if boss is None:
        raise HTTPException(status_code=404, detail="boss_not_found")
    return _staged_response("boss", boss_id, payload)


@router.get("/comps")
def admin_list_comps(mode: Optional[ContentMode] = Query(default=None)) -> dict:
    comps = repo.list_comps(mode=mode)
    return {"items": comps, "count": len(comps)}


@router.patch("/comps/{comp_id}")
def admin_patch_comp(comp_id: str, payload: dict) -> dict:
    comp = repo.get_comp(comp_id)
    if comp is None:
        raise HTTPException(status_code=404, detail="comp_not_found")
    return _staged_response("comp", comp_id, payload)


@router.post("/comps/community/{submission_id}/approve")
def admin_approve_community_comp(submission_id: str, payload: dict) -> dict:
    return {
        "status": "approved",
        "submission_id": submission_id,
        "approved_by": payload.get("reviewer", "admin"),
        "published_as": payload.get("comp_id", "new_comp_id"),
        "approved_at": "2026-04-08T10:00:00Z",
    }


@router.get("/tierlists")
def admin_list_tierlists() -> dict:
    return {"items": repo.tierlists, "count": len(repo.tierlists)}


@router.patch("/tierlists/{slug}")
def admin_patch_tierlist(slug: str, payload: dict) -> dict:
    tierlist = repo.get_tierlist(slug)
    if tierlist is None:
        raise HTTPException(status_code=404, detail="tierlist_not_found")
    return _staged_response("tierlist", slug, payload)


@router.patch("/tierlists/{slug}/entries/{entity_id}")
def admin_patch_tier_entry(slug: str, entity_id: str, payload: dict) -> dict:
    tierlist = repo.get_tierlist(slug)
    if tierlist is None:
        raise HTTPException(status_code=404, detail="tierlist_not_found")
    return {
        "status": "staged",
        "entity": "tierlist_entry",
        "tierlist": slug,
        "entry": entity_id,
        "changes": payload,
        "workflow": ["staged", "review", "publish"],
    }


@router.get("/guides")
def admin_list_guides() -> dict:
    return {"items": repo.guides, "count": len(repo.guides)}


@router.patch("/guides/{guide_slug}")
def admin_patch_guide(guide_slug: str, payload: dict) -> dict:
    guide = next((item for item in repo.guides if item.slug == guide_slug), None)
    if guide is None:
        raise HTTPException(status_code=404, detail="guide_not_found")
    return _staged_response("guide", guide_slug, payload)


@router.post("/substitutions")
def admin_register_substitution(payload: dict) -> dict:
    required = ["entity_type", "from_id", "to_id"]
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise HTTPException(
            status_code=422, detail=f"missing_fields:{','.join(missing)}"
        )
    return {
        "status": "registered",
        "entity_type": payload["entity_type"],
        "from_id": payload["from_id"],
        "to_id": payload["to_id"],
        "context": payload.get("context"),
    }


@router.get("/editorial-history")
def admin_editorial_history(entity_type: Optional[str] = Query(default=None)) -> dict:
    history = [
        {
            "id": "hist_001",
            "entity_type": "unit",
            "entity_id": "unit_hart",
            "action": "update",
            "author": "editor_luna",
            "reviewer": "lead_admin",
            "published_at": "2026-04-06",
            "source_ids": ["src_gsinfo", "src_sheet_tier"],
        },
        {
            "id": "hist_002",
            "entity_type": "tierlist_entry",
            "entity_id": "unit_forte",
            "action": "tier_change",
            "author": "editor_aria",
            "reviewer": "lead_admin",
            "published_at": "2026-04-07",
            "source_ids": ["src_sheet_tier"],
        },
    ]
    if entity_type is not None:
        history = [item for item in history if item["entity_type"] == entity_type]
    return {"items": history, "count": len(history)}
