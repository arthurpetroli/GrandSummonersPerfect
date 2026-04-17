from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from app.db.json_store import JsonStore
from app.models.enums import TierGrade
from app.repositories.memory_repo import repo


EDITORIAL_STORE = JsonStore(
    str(Path(__file__).resolve().parents[2] / "data" / "editorial_store.json")
)


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _initial_payload() -> Dict[str, Any]:
    return {
        "draft_tierlist_changes": [],
        "tierlist_history": [],
        "sources": [
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
                "url": "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit",
                "last_synced_at": "2026-04-02",
            },
        ],
        "source_mappings": [],
        "sync_jobs": [],
    }


def _ensure_initialized() -> Dict[str, Any]:
    payload = EDITORIAL_STORE.load()
    if payload:
        return payload
    default_payload = _initial_payload()
    EDITORIAL_STORE.save(default_payload)
    return default_payload


def list_sources(kind: str | None = None) -> List[Dict[str, Any]]:
    payload = _ensure_initialized()
    sources = list(payload.get("sources", []))
    if kind is not None:
        return [item for item in sources if item.get("kind") == kind]
    return sources


def list_source_mappings(entity_type: str | None = None) -> List[Dict[str, Any]]:
    payload = _ensure_initialized()
    mappings = list(payload.get("source_mappings", []))
    if entity_type is not None:
        return [item for item in mappings if item.get("entity_type") == entity_type]
    return mappings


def list_tierlist_drafts(slug: str | None = None) -> List[Dict[str, Any]]:
    payload = _ensure_initialized()
    drafts = list(payload.get("draft_tierlist_changes", []))
    if slug is not None:
        return [item for item in drafts if item.get("tierlist_slug") == slug]
    return drafts


def add_tierlist_draft_change(
    tierlist_slug: str,
    entity_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    tierlist = repo.get_tierlist(tierlist_slug)
    if tierlist is None:
        raise ValueError("tierlist_not_found")

    matching_entry = next(
        (
            entry
            for entry in tierlist.entries
            if entry.entity_id == entity_id
            and entry.entity_type == payload.get("entity_type", entry.entity_type)
        ),
        None,
    )
    if matching_entry is None:
        raise ValueError("tierlist_entry_not_found")

    draft = {
        "id": f"draft_{uuid4().hex}",
        "tierlist_slug": tierlist_slug,
        "entity_id": entity_id,
        "entity_type": payload.get("entity_type", matching_entry.entity_type),
        "previous_tier": matching_entry.tier.value,
        "proposed_tier": payload.get("tier", matching_entry.tier.value),
        "proposed_reason": payload.get("reason", matching_entry.reason),
        "source_ids": payload.get("source_ids", []),
        "status": "staged",
        "submitted_by": payload.get("submitted_by", "admin"),
        "created_at": _utc_now(),
    }

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        if not current:
            current = _initial_payload()
        current.setdefault("draft_tierlist_changes", []).append(draft)
        return current

    EDITORIAL_STORE.update(updater)
    return draft


def publish_tierlist_draft(
    draft_id: str,
    reviewer: str = "admin",
    change_notes: List[str] | None = None,
) -> Dict[str, Any]:
    change_notes = change_notes or []

    published: Dict[str, Any] | None = None

    def apply_to_repo(draft_payload: Dict[str, Any]) -> None:
        tierlist_slug = str(draft_payload.get("tierlist_slug") or "")
        entity_id = str(draft_payload.get("entity_id") or "")
        entity_type = str(draft_payload.get("entity_type") or "")
        proposed_tier = str(draft_payload.get("proposed_tier") or "")
        proposed_reason = str(draft_payload.get("proposed_reason") or "")

        if not tierlist_slug or not entity_id or not entity_type:
            return

        tierlist = repo.get_tierlist(tierlist_slug)
        if tierlist is None:
            return

        normalized_tier = (
            proposed_tier if proposed_tier in {tier.value for tier in TierGrade} else None
        )
        for entry in tierlist.entries:
            if entry.entity_id != entity_id or entry.entity_type != entity_type:
                continue
            if normalized_tier is not None:
                entry.tier = TierGrade(normalized_tier)
            if proposed_reason:
                entry.reason = proposed_reason
            break

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        nonlocal published
        if not current:
            current = _initial_payload()

        drafts = current.setdefault("draft_tierlist_changes", [])
        draft = next((item for item in drafts if item.get("id") == draft_id), None)
        if draft is None:
            raise ValueError("draft_not_found")
        if draft.get("status") == "published":
            published = draft
            return current

        draft["status"] = "published"
        draft["published_at"] = _utc_now()
        draft["reviewed_by"] = reviewer
        draft["change_notes"] = change_notes

        apply_to_repo(draft)

        history_item = {
            "id": f"hist_{uuid4().hex}",
            "entity_type": "tierlist_entry",
            "entity_id": draft.get("entity_id"),
            "tierlist_slug": draft.get("tierlist_slug"),
            "action": "tier_change",
            "old_tier": draft.get("previous_tier"),
            "new_tier": draft.get("proposed_tier"),
            "author": draft.get("submitted_by", "admin"),
            "reviewer": reviewer,
            "published_at": draft["published_at"],
            "source_ids": draft.get("source_ids", []),
            "notes": change_notes,
        }
        current.setdefault("tierlist_history", []).append(history_item)
        published = draft
        return current

    EDITORIAL_STORE.update(updater)
    if published is None:
        raise ValueError("draft_not_found")
    return published


def list_editorial_history(entity_type: str | None = None) -> List[Dict[str, Any]]:
    payload = _ensure_initialized()
    history = list(payload.get("tierlist_history", []))
    if entity_type is not None:
        history = [item for item in history if item.get("entity_type") == entity_type]

    seed_items = [
        {
            "id": "hist_seed_001",
            "entity_type": "unit",
            "entity_id": "unit_hart",
            "action": "update",
            "author": "editor_luna",
            "reviewer": "lead_admin",
            "published_at": "2026-04-06",
            "source_ids": ["src_gsinfo", "src_sheet_tier"],
        },
        {
            "id": "hist_seed_002",
            "entity_type": "tierlist_entry",
            "entity_id": "unit_forte",
            "action": "tier_change",
            "author": "editor_aria",
            "reviewer": "lead_admin",
            "published_at": "2026-04-07",
            "source_ids": ["src_sheet_tier"],
        },
    ]

    merged = seed_items + history
    if entity_type is not None:
        merged = [item for item in merged if item.get("entity_type") == entity_type]
    return merged


def get_admin_overview() -> Dict[str, Any]:
    payload = _ensure_initialized()
    drafts = list_tierlist_drafts()
    pending_tier_changes = len([item for item in drafts if item.get("status") != "published"])
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
            "draft_tier_changes": len(drafts),
        },
        "pending_reviews": {
            "community_comps": 2,
            "tierlist_changes": pending_tier_changes,
            "source_imports": 3,
            "guide_updates": 2,
            "sync_jobs": len(payload.get("sync_jobs", [])),
        },
    }


def get_review_queue() -> List[Dict[str, Any]]:
    drafts = [
        {
            "id": item.get("id"),
            "type": "tier_update",
            "title": f"{item.get('tierlist_slug')} :: {item.get('entity_id')}",
            "status": item.get("status", "pending"),
            "submitted_by": item.get("submitted_by", "admin"),
        }
        for item in list_tierlist_drafts()
        if item.get("status") != "published"
    ]
    seed_queue = [
        {
            "id": "rq_comp_001",
            "type": "community_comp",
            "title": "Ashdrake Speed Variant",
            "status": "pending",
            "submitted_by": "user_community_41",
        },
        {
            "id": "rq_guide_011",
            "type": "guide_update",
            "title": "Road cleanse strategy refresh",
            "status": "pending",
            "submitted_by": "editor_aria",
        },
    ]
    return drafts + seed_queue


def register_source_mapping(mapping_payload: Dict[str, Any]) -> Dict[str, Any]:
    entry = {
        "id": f"map_{uuid4().hex}",
        "source_id": mapping_payload.get("source_id"),
        "entity_type": mapping_payload.get("entity_type"),
        "entity_id": mapping_payload.get("entity_id"),
        "source_entity_key": mapping_payload.get("source_entity_key"),
        "validation_status": mapping_payload.get("validation_status", "pending"),
        "published": bool(mapping_payload.get("published", False)),
        "updated_at": _utc_now(),
    }

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        if not current:
            current = _initial_payload()
        current.setdefault("source_mappings", []).append(entry)
        return current

    EDITORIAL_STORE.update(updater)
    return entry


def append_sync_job(job_payload: Dict[str, Any]) -> Dict[str, Any]:
    entry = {
        "id": f"sync_{uuid4().hex}",
        "source_id": job_payload.get("source_id", "src_sheet_tier"),
        "status": job_payload.get("status", "completed"),
        "summary": job_payload.get("summary", {}),
        "created_at": _utc_now(),
    }

    def updater(current: Dict[str, Any]) -> Dict[str, Any]:
        if not current:
            current = _initial_payload()
        current.setdefault("sync_jobs", []).append(entry)
        return current

    EDITORIAL_STORE.update(updater)
    return entry


def list_sync_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    payload = _ensure_initialized()
    jobs = list(payload.get("sync_jobs", []))
    jobs.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return jobs[:limit]
