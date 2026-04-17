from app.services.assets import gsinfo_unit_page_url, normalize_unit_name_for_gsinfo
from app.services.gsinfo_unit_db import _normalize_slug


def test_normalize_unit_name_for_gsinfo_handles_aliases() -> None:
    assert normalize_unit_name_for_gsinfo("hart") == "Hart (Earth)"
    assert normalize_unit_name_for_gsinfo("Fen") == "Fen"


def test_gsinfo_unit_page_url_encodes_path() -> None:
    url = gsinfo_unit_page_url("Hart (Earth)")
    assert url.startswith("https://www.grandsummoners.info/units/")
    assert "Hart%20%28Earth%29" in url


def test_normalize_slug_from_external_name() -> None:
    assert _normalize_slug("Abaddon") == "abaddon"
    assert _normalize_slug("Hart (Earth)") == "hart-earth"
