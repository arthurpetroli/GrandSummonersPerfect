from app.services.ingestion_service import _extract_sheet_id, _normalize_tier


def test_normalize_tier_accepts_expected_values() -> None:
    assert _normalize_tier("SSS") == "SSS"
    assert _normalize_tier("ss") == "SS"
    assert _normalize_tier(" a ") == "A"
    assert _normalize_tier("B-") == "B"


def test_normalize_tier_rejects_invalid_values() -> None:
    assert _normalize_tier("top") is None
    assert _normalize_tier("") is None


def test_extract_sheet_id_from_url() -> None:
    sheet_id = _extract_sheet_id(
        "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit?gid=116729514"
    )
    assert sheet_id == "1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8"
