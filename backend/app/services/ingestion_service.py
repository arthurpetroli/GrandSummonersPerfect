from __future__ import annotations

import json
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from app.models.enums import (
    ContentMode,
    DamageType,
    EquipSlotType,
    ServerRegion,
    TierGrade,
    UnitRole,
)
from app.models.schemas import Tierlist, TierlistEntry, UnitProfile, UnitSkill
from app.repositories.memory_repo import repo


COMMUNITY_SHEET_URL = "https://docs.google.com/spreadsheets/d/1J6b7ptaZPZYFkd1p28X_RiP8QpCRiaQnS0bfMpVtah8/edit"
COMMUNITY_TIER_GID = "116729514"
GSINFO_BUNDLE_URL = "https://www.grandsummoners.info/static/js/main.aa9a7fb7.js"
GSINFO_BASE_URL = "https://www.grandsummoners.info"

SYNC_STATE_PATH = Path(__file__).resolve().parents[2] / "data" / "sync_state.json"
SYNC_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


TIER_SCALE = {
    "SSS": 97.0,
    "SS": 91.0,
    "S": 84.0,
    "A": 76.0,
    "B": 67.0,
    "C": 56.0,
}


UNIT_NAME_ALIASES = {
    "hart": "Hart (Earth)",
    "cestina": "Cestina (Earth)",
    "fen": "Fen (Earth)",
}


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _load_sync_state() -> Dict[str, Any]:
    if not SYNC_STATE_PATH.exists():
        return {}
    try:
        return json.loads(SYNC_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_sync_state(payload: Dict[str, Any]) -> None:
    SYNC_STATE_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True),
        encoding="utf-8",
    )


def _extract_sheet_id(spreadsheet_url: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
    if not match:
        raise ValueError("invalid_google_sheet_url")
    return match.group(1)


def _extract_gid(spreadsheet_url: str, fallback: str) -> str:
    query = parse_qs(urlparse(spreadsheet_url).query)
    value = query.get("gid", [fallback])[0]
    return str(value)


def _gviz_json_url(sheet_id: str, gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json&gid={gid}"


def _gviz_default_json_url(sheet_id: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"


def _read_remote_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _load_gviz_table(url: str) -> Dict[str, Any]:
    raw = _read_remote_text(url)
    match = re.search(r"google\.visualization\.Query\.setResponse\((.*)\);?\s*$", raw, re.S)
    if match is None:
        raise ValueError("invalid_gviz_response")
    parsed = json.loads(match.group(1))
    if parsed.get("status") != "ok":
        raise ValueError("gviz_status_not_ok")
    return parsed.get("table", {})


def _table_rows_to_matrix(table: Dict[str, Any]) -> List[List[str]]:
    rows: List[List[str]] = []
    for row in table.get("rows", []):
        values: List[str] = []
        for cell in row.get("c", []):
            if cell is None:
                values.append("")
            else:
                value = cell.get("v")
                if value in (None, ""):
                    value = cell.get("f", "")
                values.append("" if value is None else str(value))
        rows.append(values)
    return rows


def _normalize_tier(raw: str | None) -> str | None:
    if raw is None:
        return None
    token = raw.strip().upper().replace(" ", "")
    token = token.replace("-", "")
    if token in {"SSS", "SS", "S", "A", "B", "C"}:
        return token
    return None


def _normalize_key(name: str) -> str:
    token = name.lower().strip()
    token = token.replace("(earth)", "")
    token = token.replace("(light)", "")
    token = token.replace("(dark)", "")
    token = token.replace("(fire)", "")
    token = token.replace("(water)", "")
    token = token.replace("\"", "")
    token = re.sub(r"\s+", " ", token)
    return token.strip()


def _build_repository_unit_index() -> Dict[str, UnitProfile]:
    index: Dict[str, UnitProfile] = {}
    for unit in repo.units:
        index[_normalize_key(unit.name)] = unit
        index[_normalize_key(unit.slug)] = unit
    return index


def _resolve_repo_unit(name: str, index: Dict[str, UnitProfile]) -> Optional[UnitProfile]:
    key = _normalize_key(name)
    unit = index.get(key)
    if unit is not None:
        return unit

    alias = UNIT_NAME_ALIASES.get(key)
    if alias is None:
        return None
    return index.get(_normalize_key(alias))


def _resolve_entity_type(entity_id: str) -> str:
    if entity_id.startswith("unit_"):
        return "unit"
    if entity_id.startswith("equip_"):
        return "equip"
    return "unit"


def _extract_recent_added(rows: List[List[str]]) -> List[Tuple[str, str]]:
    target_row: Optional[int] = None
    for row_index, row in enumerate(rows):
        for cell in row:
            if cell.strip().lower() == "recently added units":
                target_row = row_index
                break
        if target_row is not None:
            break

    if target_row is None or target_row + 2 >= len(rows):
        return []

    names_row = rows[target_row + 1]
    tier_row = rows[target_row + 2]
    result: List[Tuple[str, str]] = []
    max_len = max(len(names_row), len(tier_row))
    for column in range(max_len):
        name = names_row[column].strip() if column < len(names_row) else ""
        tier = tier_row[column].strip() if column < len(tier_row) else ""
        normalized_tier = _normalize_tier(tier)
        if name and normalized_tier:
            result.append((name, normalized_tier))
    return result


def _extract_sheet_last_updated(rows: List[List[str]]) -> Optional[str]:
    for row in rows:
        for idx, cell in enumerate(row):
            if cell.strip().lower() == "last updated:":
                if idx + 1 < len(row):
                    value = row[idx + 1].strip()
                    if value:
                        return value
    return None


def _extract_primary_sheet_units(sheet_id: str) -> Dict[str, str]:
    default_url = _gviz_default_json_url(sheet_id)
    try:
        table = _load_gviz_table(default_url)
    except (ValueError, URLError, TimeoutError, json.JSONDecodeError):
        return {}

    rows = _table_rows_to_matrix(table)
    if not rows:
        return {}

    units: Dict[str, str] = {}
    repo_index = _build_repository_unit_index()

    for row in rows:
        if not row:
            continue
        name = row[0].strip() if len(row) > 0 else ""
        element = row[2].strip() if len(row) > 2 else ""
        released = row[3].strip().upper() if len(row) > 3 else ""

        if not name or name.lower().startswith("warning"):
            continue
        if released and released not in {"Y", "YES"}:
            continue

        unit = _resolve_repo_unit(name, repo_index)
        if unit is None:
            continue
        units[unit.id] = element or unit.element

    return units


def _resolve_entity_id(entity_name: str) -> str | None:
    token = _normalize_key(entity_name)

    for unit in repo.units:
        if _normalize_key(unit.name) == token or _normalize_key(unit.slug) == token:
            return unit.id

    aliases = {
        "hart": "unit_hart",
        "cestina": "unit_cestina",
        "fen": "unit_fen",
    }
    if token in aliases:
        return aliases[token]

    for equip in repo.equips:
        if _normalize_key(equip.name) == token or _normalize_key(equip.slug) == token:
            return equip.id

    direct_unit = f"unit_{re.sub(r'[^a-z0-9]+', '_', token).strip('_')}"
    direct_equip = f"equip_{re.sub(r'[^a-z0-9]+', '_', token).strip('_')}"
    if repo.get_unit(direct_unit) is not None:
        return direct_unit
    if repo.get_equip(direct_equip) is not None:
        return direct_equip

    return None


def _external_unit_id_from_name(entity_name: str) -> str:
    token = _normalize_key(entity_name)
    slug = re.sub(r"[^a-z0-9]+", "_", token).strip("_")
    if not slug:
        slug = uuid4().hex[:12]
    return f"unit_ext_{slug}"


def _convert_tier_to_grade(tier: str) -> TierGrade:
    return TierGrade(tier)


def _default_rating_map(tier: str) -> Dict[ContentMode, TierGrade]:
    grade = _convert_tier_to_grade(tier)
    return {
        ContentMode.STORY: grade,
        ContentMode.ARENA: grade,
        ContentMode.CREST_PALACE: grade,
        ContentMode.SUMMONERS_ROAD: grade,
        ContentMode.MAGICAL_MINES: grade,
    }


def _default_values_from_tier(tier: str) -> Dict[str, int]:
    base = int(TIER_SCALE.get(tier, 70))
    return {
        "beginner": base,
        "endgame": base,
        "sustain": base,
        "nuke": max(40, base - 8),
        "auto": max(45, base - 4),
        "arena": max(45, base - 6),
    }


GSINFO_NAME_ALIASES = {
    "hart": "Hart (Earth)",
    "cestina": "Cestina (Earth)",
    "fen": "Fen (Earth)",
}


def _find_gsinfo_name(unit_name: str) -> str:
    normalized = _normalize_key(unit_name)
    return GSINFO_NAME_ALIASES.get(normalized, unit_name)


def _extract_unit_image_map_from_bundle() -> Dict[str, Dict[str, str]]:
    js = _read_remote_text(GSINFO_BUNDLE_URL)
    pattern = re.compile(
        r'id:(\d+),name:"([^\"]+)",tier:\{[^\}]*\},(?:twrequire:"[^\"]+",)?'
        r'attribute:"([^\"]+)",type:"([^\"]+)",image:\{([^\}]*)\}',
        re.S,
    )

    image_map: Dict[str, Dict[str, str]] = {}
    for match in pattern.finditer(js):
        unit_name = match.group(2)
        image_blob = match.group(5)

        detail_match = re.search(r'detailawk:"([^\"]+)"', image_blob)
        thumb_match = re.search(r'thumbawk:"([^\"]+)"', image_blob)
        if detail_match is None:
            detail_match = re.search(r'detail5:"([^\"]+)"', image_blob)
        if thumb_match is None:
            thumb_match = re.search(r'thumb5:"([^\"]+)"', image_blob)

        detail_path = detail_match.group(1) if detail_match else None
        thumb_path = thumb_match.group(1) if thumb_match else None
        if detail_path is None and thumb_path is None:
            continue

        image_map[_normalize_key(unit_name)] = {
            "detail": f"{GSINFO_BASE_URL}{detail_path}" if detail_path else "",
            "thumb": f"{GSINFO_BASE_URL}{thumb_path}" if thumb_path else "",
            "source_name": unit_name,
        }

    return image_map


def _attach_unit_images(image_map: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    updated = 0
    missing = 0
    source_ref = "https://www.grandsummoners.info/units"
    now = _utc_now()

    for unit in list(repo.units):
        normalized = _normalize_key(_find_gsinfo_name(unit.name))
        image = image_map.get(normalized)
        if image is None:
            missing += 1
            if not unit.image_url and not unit.image_thumb_url:
                unit.image_url = f"{GSINFO_BASE_URL}/logo.png"
                unit.image_thumb_url = f"{GSINFO_BASE_URL}/logo.png"
                unit.source_updated_at = now
                refs = set(unit.source_refs)
                refs.add(source_ref)
                unit.source_refs = sorted(refs)
                repo.add_or_update_unit(unit)
            continue

        if image.get("detail"):
            unit.image_url = image.get("detail")
        if image.get("thumb"):
            unit.image_thumb_url = image.get("thumb")
        unit.source_updated_at = now
        refs = set(unit.source_refs)
        refs.add(source_ref)
        unit.source_refs = sorted(refs)
        repo.add_or_update_unit(unit)
        updated += 1

    return {
        "status": "ok",
        "units_with_images": updated,
        "units_missing_images": missing,
        "source": source_ref,
        "updated_at": now,
    }


def sync_unit_images_from_gsinfo() -> Dict[str, Any]:
    try:
        image_map = _extract_unit_image_map_from_bundle()
    except Exception as error:
        return {
            "status": "failed",
            "reason": "gsinfo_bundle_fetch_failed",
            "detail": str(error),
        }

    result = _attach_unit_images(image_map)
    state = _load_sync_state()
    state["last_image_sync_at"] = _utc_now()
    state["image_sync"] = result
    _save_sync_state(state)
    return result


def preview_google_sheet_import(
    spreadsheet_url: str,
    gid: str | None = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    sheet_id = _extract_sheet_id(spreadsheet_url)
    gid_value = gid or _extract_gid(spreadsheet_url, COMMUNITY_TIER_GID)
    gviz_url = _gviz_json_url(sheet_id, gid_value)

    try:
        table = _load_gviz_table(gviz_url)
    except (ValueError, URLError, TimeoutError, json.JSONDecodeError) as error:
        return {
            "dry_run": dry_run,
            "status": "failed",
            "reason": "sheet_fetch_failed",
            "records": [],
            "accepted": 0,
            "rejected": 0,
            "gviz_url": gviz_url,
            "detail": str(error),
        }

    rows = _table_rows_to_matrix(table)
    recently_added = _extract_recent_added(rows)
    last_updated = _extract_sheet_last_updated(rows)

    records: List[Dict[str, Any]] = []
    accepted = 0
    rejected = 0

    for index, (entity_name, tier) in enumerate(recently_added, start=1):
        entity_id = _resolve_entity_id(entity_name)
        status = "valid"
        validation_errors: List[str] = []

        if entity_id is None:
            entity_id = _external_unit_id_from_name(entity_name)
            validation_errors.append("entity_not_mapped_auto_placeholder")
        if _normalize_tier(tier) is None:
            status = "invalid"
            validation_errors.append("tier_invalid")

        if status == "valid":
            accepted += 1
        else:
            rejected += 1

        records.append(
            {
                "row": index,
                "source_entity_key": f"recent-{index}",
                "entity_name": entity_name,
                "entity_id": entity_id,
                "tier": tier,
                "reason": "Imported from Recently added units row",
                "validation_status": status,
                "validation_errors": validation_errors,
            }
        )

    records_hash = hashlib.sha256(
        json.dumps(records, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()

    return {
        "dry_run": dry_run,
        "status": "ok",
        "records": records,
        "accepted": accepted,
        "rejected": rejected,
        "gviz_url": gviz_url,
        "sheet_last_updated": last_updated,
        "records_hash": records_hash,
    }


def _build_placeholder_unit(name: str, tier: str) -> UnitProfile:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    unit_id = f"unit_ext_{slug}"
    now = _utc_now()

    return UnitProfile(
        id=unit_id,
        slug=slug,
        name=name,
        rarity=5,
        element="Unknown",
        race="Unknown",
        role=UnitRole.SUPPORT,
        damage_type=DamageType.HYBRID,
        equip_slots=[EquipSlotType.SUPPORT, EquipSlotType.HEAL, EquipSlotType.ARMOR],
        tags=["external_source", "needs_curation"],
        server_region=ServerRegion.BOTH,
        skill=UnitSkill(
            name="Curated Skill",
            description="Placeholder generated from external sync. Pending curation.",
            cooldown_seconds=10,
        ),
        arts=UnitSkill(
            name="Curated Arts",
            description="Placeholder generated from external sync. Pending curation.",
            cooldown_seconds=None,
        ),
        true_arts=UnitSkill(
            name="Curated True Arts",
            description="Placeholder generated from external sync. Pending curation.",
            cooldown_seconds=None,
        ),
        super_arts=None,
        passives=["Pending curation from sources"],
        strengths=["External source detected new/updated unit"],
        limitations=["Data placeholder until editor review"],
        best_use=["Pending curation"],
        weak_in=["Pending curation"],
        team_dependencies=[],
        equip_dependencies=[],
        values=_default_values_from_tier(tier),
        content_ratings=_default_rating_map(tier),
        synergy_units=[],
        substitute_unit_ids=[],
        image_url=f"{GSINFO_BASE_URL}/logo.png",
        image_thumb_url=f"{GSINFO_BASE_URL}/logo.png",
        source_updated_at=now,
        source_refs=[COMMUNITY_SHEET_URL],
    )


def _upsert_tierlist_entries_from_records(
    tierlist_slug: str,
    records: List[Dict[str, Any]],
    version: str,
) -> Dict[str, Any]:
    existing = repo.get_tierlist(tierlist_slug)
    if existing is None:
        tierlist = Tierlist(
            id=f"tier_{uuid4().hex}",
            slug=tierlist_slug,
            title="Community Recently Added Tier",
            mode=None,
            category="overall_units",
            version=version,
            server_region=ServerRegion.BOTH,
            entries=[],
        )
    else:
        tierlist = existing

    index_by_entity = {
        (entry.entity_type, entry.entity_id): entry for entry in tierlist.entries
    }

    updated = 0
    inserted = 0
    skipped = 0

    for item in records:
        if item.get("validation_status") != "valid":
            skipped += 1
            continue
        entity_id = str(item.get("entity_id"))
        tier_value = str(item.get("tier"))
        if tier_value not in {tier.value for tier in TierGrade}:
            skipped += 1
            continue

        unit = repo.get_unit(entity_id)
        if unit is None:
            placeholder = _build_placeholder_unit(str(item.get("entity_name")), tier_value)
            repo.add_or_update_unit(placeholder)
            entity_id = placeholder.id
            unit = placeholder

        if unit is not None:
            if not unit.image_url and not unit.image_thumb_url:
                unit.image_url = f"{GSINFO_BASE_URL}/logo.png"
                unit.image_thumb_url = f"{GSINFO_BASE_URL}/logo.png"
            unit.source_updated_at = _utc_now()
            refs = set(unit.source_refs)
            refs.add(COMMUNITY_SHEET_URL)
            unit.source_refs = sorted(refs)
            repo.add_or_update_unit(unit)

        entry_type = _resolve_entity_type(entity_id)
        key = (entry_type, entity_id)
        reason = str(item.get("reason") or "Imported from community tierlist sync")
        score = float(TIER_SCALE.get(tier_value, 70.0))

        if key in index_by_entity:
            entry = index_by_entity[key]
            entry.tier = TierGrade(tier_value)
            entry.context_score = score
            entry.reason = reason
            updated += 1
            continue

        entry = TierlistEntry(
            entity_type=entry_type,
            entity_id=entity_id,
            tier=TierGrade(tier_value),
            context_score=score,
            reason=reason,
            strong_in=["Community tier signal"],
            weak_in=["Pending contextual review"],
            dependencies=[],
            substitutes=[],
            beginner_value=max(40, int(score - 4)),
            veteran_value=max(40, int(score + 2)),
            ease_of_use=max(40, int(score - 2)),
            consistency=max(40, int(score - 1)),
            niche_or_generalist="generalist",
            requires_specific_team=False,
            requires_specific_equips=False,
        )
        tierlist.entries.append(entry)
        inserted += 1

    tierlist.version = version
    repo.upsert_tierlist(tierlist)
    return {"updated": updated, "inserted": inserted, "skipped": skipped}


def apply_google_sheet_import(
    spreadsheet_url: str,
    gid: str | None = None,
    tierlist_slug: str = "community-recent-added-tier",
) -> Dict[str, Any]:
    sheet_id = _extract_sheet_id(spreadsheet_url)
    preview = preview_google_sheet_import(spreadsheet_url=spreadsheet_url, gid=gid, dry_run=False)
    if preview.get("status") != "ok":
        return preview

    primary_sheet_map = _extract_primary_sheet_units(sheet_id)
    updated_core_units = 0
    for unit_id, element in primary_sheet_map.items():
        unit = repo.get_unit(unit_id)
        if unit is None:
            continue
        if element and unit.element != element:
            unit.element = element
        now = _utc_now()
        unit.source_updated_at = now
        refs = set(unit.source_refs)
        refs.add(COMMUNITY_SHEET_URL)
        unit.source_refs = sorted(refs)
        repo.add_or_update_unit(unit)
        updated_core_units += 1

    records = preview.get("records", [])
    version_stamp = datetime.now(tz=timezone.utc).strftime("%Y.%m.%d")
    upsert_result = _upsert_tierlist_entries_from_records(
        tierlist_slug=tierlist_slug,
        records=records,
        version=version_stamp,
    )

    image_result = sync_unit_images_from_gsinfo()

    state = _load_sync_state()
    state["last_tier_sync_at"] = _utc_now()
    state["tier_sync"] = {
        "tierlist_slug": tierlist_slug,
        "accepted": preview.get("accepted", 0),
        "rejected": preview.get("rejected", 0),
        "upsert": upsert_result,
        "sheet_last_updated": preview.get("sheet_last_updated"),
        "records_hash": preview.get("records_hash"),
    }
    state["last_sync_signature"] = str(preview.get("records_hash") or "")
    _save_sync_state(state)

    return {
        "status": "ok",
        "preview": preview,
        "core_units_updated": updated_core_units,
        "upsert": upsert_result,
        "image_sync": image_result,
        "external_units_seeded": upsert_result.get("inserted", 0),
        "tierlist_slug": tierlist_slug,
    }


def sync_if_stale(force: bool = False) -> Dict[str, Any]:
    state = _load_sync_state()
    preview = preview_google_sheet_import(
        spreadsheet_url=COMMUNITY_SHEET_URL,
        gid=COMMUNITY_TIER_GID,
        dry_run=True,
    )
    if preview.get("status") != "ok":
        return {
            "status": "failed",
            "reason": "sheet_preview_failed",
            "preview": preview,
        }

    signature = str(preview.get("records_hash") or "")
    last_signature = state.get("last_sync_signature")
    if not force and signature == last_signature:
        image_status = sync_unit_images_from_gsinfo()
        return {
            "status": "skipped",
            "reason": "no_sheet_change_detected",
            "sheet_last_updated": preview.get("sheet_last_updated"),
            "image_sync": image_status,
        }

    return apply_google_sheet_import(
        spreadsheet_url=COMMUNITY_SHEET_URL,
        gid=COMMUNITY_TIER_GID,
        tierlist_slug="community-recent-added-tier",
    )


def get_sync_status() -> Dict[str, Any]:
    state = _load_sync_state()
    return {
        "last_tier_sync_at": state.get("last_tier_sync_at"),
        "last_image_sync_at": state.get("last_image_sync_at"),
        "tier_sync": state.get("tier_sync"),
        "image_sync": state.get("image_sync"),
        "last_sync_signature": state.get("last_sync_signature"),
    }
