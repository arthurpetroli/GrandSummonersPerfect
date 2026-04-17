from app.services.gsinfo_unit_db import get_gsinfo_store_status, has_gsinfo_store


def test_gsinfo_store_status_has_expected_shape() -> None:
    status = get_gsinfo_store_status()
    assert "count" in status
    assert "updated_at" in status


def test_has_gsinfo_store_returns_boolean() -> None:
    value = has_gsinfo_store()
    assert isinstance(value, bool)
