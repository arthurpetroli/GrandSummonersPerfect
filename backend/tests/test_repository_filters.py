from app.models.enums import ContentMode, ServerRegion
from app.repositories.memory_repo import repo


def test_units_filter_by_mode_and_tag() -> None:
    items = repo.list_units(mode=ContentMode.CREST_PALACE, tag="art_gen")
    assert len(items) > 0


def test_units_filter_by_region() -> None:
    jp_items = repo.list_units(server_region=ServerRegion.JP)
    assert any(item.server_region.value in {"JP", "BOTH"} for item in jp_items)


def test_equips_filter_by_context_tier() -> None:
    items = repo.list_equips(context="sustain", tier="SSS")
    assert len(items) > 0


def test_units_filter_by_query_token() -> None:
    items = repo.list_units(q="hart")
    assert any(item.name.lower().startswith("hart") for item in items)


def test_units_query_matches_passives_or_tags() -> None:
    items = repo.list_units(q="mitigation")
    assert len(items) > 0
