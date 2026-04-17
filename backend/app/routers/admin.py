from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.enums import ContentMode
from app.repositories.memory_repo import repo
from app.services.editorial import (
    add_tierlist_draft_change,
    append_sync_job,
    get_admin_overview,
    get_review_queue,
    list_editorial_history,
    list_source_mappings,
    list_sources,
    list_sync_jobs,
    list_tierlist_drafts,
    publish_tierlist_draft,
    register_source_mapping,
)
from app.services.gsinfo_unit_db import (
    get_gsinfo_store_status,
    sync_gsinfo_unit_database,
)
from app.services.ingestion_service import (
    apply_google_sheet_import,
    get_sync_status,
    preview_google_sheet_import,
    sync_if_stale,
    sync_unit_images_from_gsinfo,
)

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
    return get_admin_overview()


@router.get("/review-queue")
def admin_review_queue() -> dict:
    items = get_review_queue()
    return {"items": items}


@router.post("/publish")
def admin_publish(payload: dict) -> dict:
    entity_type = payload.get("entity_type")
    entity_id = payload.get("entity_id")
    source_ids = payload.get("source_ids", [])
    if not entity_type or not entity_id:
        raise HTTPException(
            status_code=422, detail="entity_type_and_entity_id_required"
        )

    if entity_type == "tierlist_draft":
        try:
            draft = publish_tierlist_draft(
                draft_id=entity_id,
                reviewer=payload.get("reviewer", "admin"),
                change_notes=payload.get("change_notes", []),
            )
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        return {
            "status": "published",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "source_ids": source_ids,
            "published_draft": draft,
        }

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
def admin_sources(kind: Optional[str] = Query(default=None)) -> dict:
    items = list_sources(kind=kind)
    return {"items": items, "count": len(items)}


@router.get("/source-mappings")
def admin_source_mappings(entity_type: Optional[str] = Query(default=None)) -> dict:
    mappings = list_source_mappings(entity_type=entity_type)
    return {"items": mappings, "count": len(mappings)}


@router.post("/sources/import")
def import_source(payload: dict) -> dict:
    source_id = str(payload.get("source_id") or "")
    entity_type = str(payload.get("entity_type") or "")
    if not source_id or not entity_type:
        raise HTTPException(status_code=422, detail="source_id_and_entity_type_required")

    if source_id == "src_sheet_tier" and entity_type in {"tierlist", "tierlist_entry"}:
        dry_run = bool(payload.get("dry_run", True))
        if dry_run:
            result = preview_google_sheet_import(
                spreadsheet_url=payload.get(
                    "spreadsheet_url",
                    "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit",
                ),
                gid=payload.get("gid"),
                dry_run=True,
            )
        else:
            result = apply_google_sheet_import(
                spreadsheet_url=payload.get(
                    "spreadsheet_url",
                    "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit",
                ),
                gid=payload.get("gid"),
                tierlist_slug=str(
                    payload.get("tierlist_slug") or "community-recent-added-tier"
                ),
            )

        preview_block = result.get("preview", result)
        for item in preview_block.get("records", []):
            register_source_mapping(
                {
                    "source_id": source_id,
                    "entity_type": "tierlist_entry",
                    "entity_id": item.get("entity_id"),
                    "source_entity_key": item.get("source_entity_key"),
                    "validation_status": item.get("validation_status", "pending"),
                    "published": not dry_run and item.get("validation_status") == "valid",
                }
            )

        append_sync_job(
            {
                "source_id": source_id,
                "status": result.get("status", "failed"),
                "summary": {
                    "accepted": preview_block.get("accepted", 0),
                    "rejected": preview_block.get("rejected", 0),
                    "dry_run": dry_run,
                },
            }
        )

        return {
            "status": "queued" if dry_run else "completed",
            "job": "ingestion_import",
            "source_id": source_id,
            "entity_type": entity_type,
            "started_at": "2026-04-08T10:00:00Z",
            "pipeline": ["raw_source", "normalization", "validation", "publish"],
            "result": result,
        }

    return {
        "status": "queued",
        "job": "ingestion_import",
        "source_id": source_id,
        "entity_type": entity_type,
        "started_at": "2026-04-08T10:00:00Z",
        "pipeline": ["raw_source", "normalization", "validation", "publish"],
    }


@router.post("/sync/run")
def run_full_sync(payload: Optional[dict] = None) -> dict:
    payload = payload or {}
    force = bool(payload.get("force", False))
    result = sync_if_stale(force=force)
    append_sync_job(
        {
            "source_id": "src_sheet_tier",
            "status": result.get("status", "failed"),
            "summary": result,
        }
    )
    return {"status": "ok", "result": result}


@router.get("/sync/status")
def sync_status() -> dict:
    return {
        "status": "ok",
        "sync": get_sync_status(),
        "recent_jobs": list_sync_jobs(limit=10),
    }


@router.post("/sync/images")
def sync_images() -> dict:
    result = sync_unit_images_from_gsinfo()
    append_sync_job(
        {
            "source_id": "src_gsinfo",
            "status": result.get("status", "failed"),
            "summary": result,
        }
    )
    return {"status": "ok", "result": result}


@router.post("/sync/gsinfo-units")
def sync_gsinfo_units() -> dict:
    result = sync_gsinfo_unit_database()
    append_sync_job(
        {
            "source_id": "src_gsinfo",
            "status": result.get("status", "failed"),
            "summary": result,
        }
    )
    return {"status": "ok", "result": result}


@router.get("/sync/gsinfo-units/status")
def sync_gsinfo_units_status() -> dict:
    return {"status": "ok", "store": get_gsinfo_store_status()}


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


@router.get("/tierlists/drafts")
def admin_list_tierlist_drafts(slug: Optional[str] = Query(default=None)) -> dict:
    drafts = list_tierlist_drafts(slug=slug)
    return {"items": drafts, "count": len(drafts)}


@router.patch("/tierlists/{slug}")
def admin_patch_tierlist(slug: str, payload: dict) -> dict:
    tierlist = repo.get_tierlist(slug)
    if tierlist is None:
        raise HTTPException(status_code=404, detail="tierlist_not_found")
    return _staged_response("tierlist", slug, payload)


@router.patch("/tierlists/{slug}/entries/{entity_id}")
def admin_patch_tier_entry(slug: str, entity_id: str, payload: dict) -> dict:
    try:
        draft = add_tierlist_draft_change(slug, entity_id, payload)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "status": "staged",
        "entity": "tierlist_entry",
        "tierlist": slug,
        "entry": entity_id,
        "changes": payload,
        "draft": draft,
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
    history = list_editorial_history(entity_type=entity_type)
    return {"items": history, "count": len(history)}
