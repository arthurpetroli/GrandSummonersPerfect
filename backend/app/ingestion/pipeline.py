from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class RawRecord:
    source_id: str
    source_entity_key: str
    payload: Dict[str, Any]
    fetched_at: datetime


@dataclass
class NormalizedRecord:
    source_id: str
    entity_type: str
    source_entity_key: str
    normalized_payload: Dict[str, Any]
    normalized_at: datetime


@dataclass
class ValidationResult:
    record: NormalizedRecord
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class RawSourceLayer:
    def ingest(
        self, source_id: str, raw_payloads: List[Dict[str, Any]]
    ) -> List[RawRecord]:
        now = datetime.utcnow()
        records = []
        for item in raw_payloads:
            records.append(
                RawRecord(
                    source_id=source_id,
                    source_entity_key=str(
                        item.get("id") or item.get("slug") or "unknown"
                    ),
                    payload=item,
                    fetched_at=now,
                )
            )
        return records


class NormalizationLayer:
    def normalize(
        self, records: List[RawRecord], entity_type: str
    ) -> List[NormalizedRecord]:
        now = datetime.utcnow()
        normalized = []
        for record in records:
            payload = dict(record.payload)
            payload["_source_id"] = record.source_id
            normalized.append(
                NormalizedRecord(
                    source_id=record.source_id,
                    entity_type=entity_type,
                    source_entity_key=record.source_entity_key,
                    normalized_payload=payload,
                    normalized_at=now,
                )
            )
        return normalized


class ValidationLayer:
    REQUIRED_BY_ENTITY = {
        "unit": ["name", "element", "role"],
        "equip": ["name", "slot_type", "category"],
        "boss": ["name", "mode", "stage_name"],
    }

    def validate(self, records: List[NormalizedRecord]) -> List[ValidationResult]:
        results = []
        for record in records:
            required = self.REQUIRED_BY_ENTITY.get(record.entity_type, [])
            errors: List[str] = []
            warnings: List[str] = []

            for field in required:
                if not record.normalized_payload.get(field):
                    errors.append(f"missing_field:{field}")

            if record.normalized_payload.get("server_region") is None:
                warnings.append("missing_server_region_defaulting_both")

            results.append(
                ValidationResult(
                    record=record,
                    is_valid=len(errors) == 0,
                    errors=errors,
                    warnings=warnings,
                )
            )

        return results


class PublishLayer:
    def publish(
        self, validations: List[ValidationResult], dry_run: bool = True
    ) -> Dict[str, Any]:
        accepted = [item for item in validations if item.is_valid]
        rejected = [item for item in validations if not item.is_valid]

        return {
            "dry_run": dry_run,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "accepted_keys": [item.record.source_entity_key for item in accepted],
            "rejected": [
                {
                    "key": item.record.source_entity_key,
                    "errors": item.errors,
                }
                for item in rejected
            ],
            "published_at": datetime.utcnow().isoformat(),
        }


class IngestionPipeline:
    def __init__(self) -> None:
        self.raw = RawSourceLayer()
        self.normalize_layer = NormalizationLayer()
        self.validate_layer = ValidationLayer()
        self.publish_layer = PublishLayer()

    def run(
        self,
        source_id: str,
        entity_type: str,
        raw_payloads: List[Dict[str, Any]],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        raw_records = self.raw.ingest(source_id=source_id, raw_payloads=raw_payloads)
        normalized_records = self.normalize_layer.normalize(
            records=raw_records, entity_type=entity_type
        )
        validations = self.validate_layer.validate(normalized_records)
        result = self.publish_layer.publish(validations=validations, dry_run=dry_run)

        return {
            "source_id": source_id,
            "entity_type": entity_type,
            "raw_count": len(raw_records),
            "normalized_count": len(normalized_records),
            "validation": {
                "valid": len([item for item in validations if item.is_valid]),
                "invalid": len([item for item in validations if not item.is_valid]),
            },
            "publish": result,
        }
