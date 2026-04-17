from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

GSINFO_BUNDLE_URL = "https://www.grandsummoners.info/static/js/main.aa9a7fb7.js"
GSINFO_BASE_URL = "https://www.grandsummoners.info"

STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "gsinfo_units_store.json"
STORE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _read_bundle() -> str:
    request = Request(GSINFO_BUNDLE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def _extract_js_object(source: str, start_index: int) -> Optional[str]:
    depth = 0
    in_string = False
    escaped = False
    for index in range(start_index, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
            continue
        if char == "}":
            depth -= 1
            if depth == 0:
                return source[start_index : index + 1]
    return None


def _find_matches(pattern: str, text: str) -> List[str]:
    return [match.group(1).strip() for match in re.finditer(pattern, text, re.S)]


def _find_first(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text, re.S)
    if match is None:
        return None
    return match.group(1).strip()


def _extract_image_path(image_blob: str, keys: List[str]) -> Optional[str]:
    for key in keys:
        value = _find_first(fr'{key}:"([^\"]+)"', image_blob)
        if value:
            return value
    return None


def _safe_number(value: Optional[str], fallback: float = 0.0) -> float:
    if value is None:
        return fallback
    try:
        return float(value)
    except ValueError:
        return fallback


def _normalize_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _build_unit_record(object_blob: str) -> Optional[Dict[str, Any]]:
    unit_id = _find_first(r"id:(\d+)", object_blob)
    name = _find_first(r'name:"([^\"]+)"', object_blob)
    element = _find_first(r'attribute:"([^\"]+)"', object_blob)
    race = _find_first(r'type:"([^\"]+)"', object_blob)
    image_blob = _find_first(r"image:\{([^\}]*)\}", object_blob)
    if unit_id is None or name is None or element is None or race is None:
        return None

    if image_blob is None:
        return None

    detail_path = _extract_image_path(
        image_blob,
        ["detailawk", "detail5", "detail4", "detail3", "detail2"],
    )
    thumb_path = _extract_image_path(
        image_blob,
        ["thumbawk", "thumb5", "thumb4", "thumb3", "thumb2"],
    )

    skill = _find_first(r'skillset:\{[^\}]*skill:"([^\"]+)"', object_blob)
    arts = _find_first(r'skillset:\{[^\}]*arts:"([^\"]+)"', object_blob)
    true_arts = _find_first(r'skillset:\{[^\}]*truearts:"([^\"]+)"', object_blob)
    passive_block = _find_first(r"passive:\{([^\}]*)\}", object_blob)
    passives: List[str] = []
    if passive_block:
        passives = _find_matches(r'ability\d+:"([^\"]+)"', passive_block)

    review_block = _find_first(r"review:\{([^\}]*)\}", object_blob)
    strengths: List[str] = []
    limitations: List[str] = []
    if review_block:
        overall = _find_first(r'overall:"([^\"]+)"', object_blob)
        if overall:
            strengths.append(overall)
        skill_review = _find_first(r'skill:"([^\"]+)"', review_block)
        ta_review = _find_first(r'truearts:"([^\"]+)"', review_block)
        if skill_review:
            strengths.append(skill_review)
        if ta_review:
            strengths.append(ta_review)
        arts_review = _find_first(r'arts:"([^\"]+)"', review_block)
        if arts_review:
            limitations.append(arts_review)

    tier_blob = _find_first(r"tier:\{([^\}]*)\}", object_blob) or ""
    metrics = {
        "defense": _safe_number(_find_first(r"defense:([0-9\.-]+)", tier_blob)),
        "artgen": _safe_number(_find_first(r"artgen:([0-9\.-]+)", tier_blob)),
        "damage": _safe_number(_find_first(r"damage:([0-9\.-]+)", tier_blob)),
        "buffs": _safe_number(_find_first(r"buffs:([0-9\.-]+)", tier_blob)),
        "heal": _safe_number(_find_first(r"heal:([0-9\.-]+)", tier_blob)),
        "break": _safe_number(_find_first(r"break:([0-9\.-]+)", tier_blob)),
    }

    return {
        "id": f"unit_gsinfo_{unit_id}",
        "gsinfo_numeric_id": unit_id,
        "slug": _normalize_slug(name),
        "name": name,
        "element": element,
        "race": race,
        "image_url": f"{GSINFO_BASE_URL}{detail_path}" if detail_path else None,
        "image_thumb_url": f"{GSINFO_BASE_URL}{thumb_path}" if thumb_path else None,
        "skill": skill,
        "arts": arts,
        "true_arts": true_arts,
        "passives": passives,
        "strengths": strengths,
        "limitations": limitations,
        "metrics": metrics,
        "source_ref": f"{GSINFO_BASE_URL}/units/{name}",
        "source_updated_at": _utc_now(),
    }


def _extract_unit_objects(bundle: str) -> List[Dict[str, Any]]:
    starts = [match.start() for match in re.finditer(r"\{id:\d+,name:\"", bundle)]
    units: List[Dict[str, Any]] = []
    for start in starts:
        object_blob = _extract_js_object(bundle, start)
        if object_blob is None:
            continue
        if "attribute:\"" not in object_blob or "skillset:{" not in object_blob:
            continue
        record = _build_unit_record(object_blob)
        if record is None:
            continue
        units.append(record)
    return units


def sync_gsinfo_unit_database() -> Dict[str, Any]:
    bundle = _read_bundle()
    units = _extract_unit_objects(bundle)
    payload = {
        "updated_at": _utc_now(),
        "count": len(units),
        "items": units,
    }
    STORE_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "status": "ok",
        "count": len(units),
        "updated_at": payload["updated_at"],
    }


def has_gsinfo_store() -> bool:
    payload = _load_store()
    return int(payload.get("count", 0)) > 0


def _load_store() -> Dict[str, Any]:
    if not STORE_PATH.exists():
        return {"updated_at": None, "count": 0, "items": []}
    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"updated_at": None, "count": 0, "items": []}


def get_gsinfo_unit_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    payload = _load_store()
    for item in payload.get("items", []):
        if item.get("slug") == slug:
            return item
    return None


def search_gsinfo_units(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    token = query.strip().lower()
    if not token:
        return []
    payload = _load_store()
    results = []
    for item in payload.get("items", []):
        if token in str(item.get("name", "")).lower() or token in str(
            item.get("slug", "")
        ).lower():
            results.append(item)
        if len(results) >= limit:
            break
    return results


def get_gsinfo_store_status() -> Dict[str, Any]:
    payload = _load_store()
    return {
        "count": payload.get("count", 0),
        "updated_at": payload.get("updated_at"),
    }
