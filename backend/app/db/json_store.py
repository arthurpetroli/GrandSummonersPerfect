import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict


class JsonStore:
    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)
        self._lock = Lock()
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write({})

    def _read(self) -> Dict[str, Any]:
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, payload: Dict[str, Any]) -> None:
        with self.file_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True, sort_keys=True)

    def load(self) -> Dict[str, Any]:
        with self._lock:
            return self._read()

    def save(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._write(payload)

    def update(self, updater) -> Dict[str, Any]:
        with self._lock:
            payload = self._read()
            updated = updater(payload)
            self._write(updated)
            return updated
