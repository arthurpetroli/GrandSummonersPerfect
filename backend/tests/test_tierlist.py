from app.services.tierlist import group_entries_by_tier, tierlist_change_log


def test_group_entries_by_tier() -> None:
    grouped = group_entries_by_tier("overall-units-global")
    assert "SSS" in grouped or "SS" in grouped


def test_tierlist_has_change_log() -> None:
    changes = tierlist_change_log("overall-units-global")
    assert len(changes) >= 1
    assert "version" in changes[0]
