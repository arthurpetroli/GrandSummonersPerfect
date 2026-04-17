from __future__ import annotations

from urllib.parse import quote


def normalize_unit_name_for_gsinfo(name: str) -> str:
    normalized = name.strip()
    if "(" in normalized and ")" in normalized:
        return normalized
    # match common naming from community sheets to gsinfo style
    aliases = {
        "hart": "Hart (Earth)",
        "sanstone": "Sanstone",
        "fen": "Fen",
        "vox": "Vox",
        "mako": "Mako",
        "berwick": "Berwick",
        "forte": "Forte",
        "cestina": "Cestina (Earth)",
        "emperor isliid": "Emperor Isliid",
    }
    return aliases.get(normalized.lower(), normalized)


def gsinfo_unit_page_url(name: str) -> str:
    return f"https://www.grandsummoners.info/units/{quote(normalize_unit_name_for_gsinfo(name))}"


def fallback_unit_portrait_url(unit_id: str) -> str:
    # deterministic fallback, works for many GSInfo unit asset IDs
    numeric = "".join(char for char in unit_id if char.isdigit())
    if numeric:
        return f"https://www.grandsummoners.info/db/Units/Detail/unit_detail_{numeric}.png"
    return "https://www.grandsummoners.info/logo.png"
