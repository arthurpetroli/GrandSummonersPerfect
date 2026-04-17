from app.services.tierlist import group_entries_by_tier, tierlist_change_log
from app.repositories.memory_repo import repo


def test_group_entries_by_tier() -> None:
    grouped = group_entries_by_tier("overall-units-global")
    assert "SSS" in grouped or "SS" in grouped


def test_grouped_entries_include_entity_resolution() -> None:
    grouped = group_entries_by_tier("overall-units-global")
    first_tier_entries = grouped.get("SSS") or grouped.get("SS") or []
    assert len(first_tier_entries) > 0
    first_entry = first_tier_entries[0]

    assert first_entry["entity_name"]
    assert first_entry["tier"] in {"SSS", "SS", "S", "A", "B", "C"}
    assert isinstance(first_entry["substitute_entities"], list)
    if first_entry["substitute_entities"]:
        substitute = first_entry["substitute_entities"][0]
        assert "name" in substitute
        assert "href" in substitute


def test_tierlist_has_change_log() -> None:
    changes = tierlist_change_log("overall-units-global")
    assert len(changes) >= 1
    assert "version" in changes[0]


def test_required_unit_tierlists_are_available() -> None:
    expected_slugs = {
        "beginner-unit-tier-list",
        "endgame-unit-tier-list",
        "sustain-unit-tier-list",
        "nuke-unit-tier-list",
        "arena-unit-tier-list",
        "farming-unit-tier-list",
        "bossing-unit-tier-list",
        "support-unit-tier-list",
    }
    available = {tier.slug for tier in repo.tierlists}
    assert expected_slugs.issubset(available)
    assert (
        "equip-tier-list" in available
        or "overall-equip-tier-list" in available
    )


def test_mode_tierlists_have_entries_even_when_sparse() -> None:
    mode_slugs = [
        "dungeon-of-trials-tier-list",
        "collab-content-tier-list",
    ]
    for slug in mode_slugs:
        tierlist = repo.get_tierlist(slug)
        assert tierlist is not None
        assert len(tierlist.entries) > 0
