from app.services.editorial import (
    add_tierlist_draft_change,
    append_sync_job,
    get_admin_overview,
    get_review_queue,
    list_sync_jobs,
    list_tierlist_drafts,
)
from app.services.ingestion_service import get_sync_status


def test_add_tierlist_draft_change_registers_staged_item() -> None:
    draft = add_tierlist_draft_change(
        tierlist_slug="overall-units-global",
        entity_id="unit_hart",
        payload={
            "entity_type": "unit",
            "tier": "SS",
            "reason": "Test change for coverage",
            "source_ids": ["src_sheet_tier"],
            "submitted_by": "pytest",
        },
    )
    assert draft["status"] == "staged"
    assert draft["tierlist_slug"] == "overall-units-global"
    assert draft["entity_id"] == "unit_hart"


def test_admin_overview_includes_draft_metric() -> None:
    overview = get_admin_overview()
    assert "draft_tier_changes" in overview["counts"]


def test_review_queue_includes_structured_items() -> None:
    queue = get_review_queue()
    assert len(queue) > 0
    assert "id" in queue[0]
    assert "type" in queue[0]


def test_list_tierlist_drafts_filters_by_slug() -> None:
    drafts = list_tierlist_drafts(slug="overall-units-global")
    assert all(item.get("tierlist_slug") == "overall-units-global" for item in drafts)


def test_sync_jobs_can_be_registered() -> None:
    job = append_sync_job(
        {
            "source_id": "src_sheet_tier",
            "status": "ok",
            "summary": {"accepted": 3, "rejected": 0},
        }
    )
    jobs = list_sync_jobs(limit=5)
    assert any(item.get("id") == job["id"] for item in jobs)


def test_sync_status_payload_is_structured() -> None:
    status = get_sync_status()
    assert "last_tier_sync_at" in status
    assert "last_image_sync_at" in status
    assert "last_sync_signature" in status
