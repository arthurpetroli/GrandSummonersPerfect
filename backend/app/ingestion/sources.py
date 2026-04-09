from typing import Any, Dict, List


def parse_google_sheet_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for row in rows:
        normalized.append(
            {
                "id": row.get("id")
                or row.get("slug")
                or row.get("name", "unknown").lower().replace(" ", "-"),
                "name": row.get("name"),
                "role": row.get("role"),
                "element": row.get("element"),
                "tier": row.get("tier"),
                "notes": row.get("notes"),
                "server_region": row.get("region") or "BOTH",
            }
        )
    return normalized


def parse_public_doc_sections(sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    output = []
    for section in sections:
        output.append(
            {
                "id": section.get("slug")
                or section.get("title", "guide").lower().replace(" ", "-"),
                "title": section.get("title"),
                "content": section.get("content"),
                "tags": section.get("tags", []),
            }
        )
    return output


def transform_public_site_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": card.get("id") or card.get("name", "entry").lower().replace(" ", "-"),
            "name": card.get("name"),
            "category": card.get("category"),
            "description": card.get("description"),
        }
        for card in cards
    ]
