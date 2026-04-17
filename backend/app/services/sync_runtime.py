from __future__ import annotations

import threading

from app.services.gsinfo_unit_db import sync_gsinfo_unit_database
from app.services.ingestion_service import sync_if_stale

_has_run = False
_lock = threading.Lock()


def run_startup_sync_once() -> None:
    global _has_run
    with _lock:
        if _has_run:
            return
        _has_run = True

    try:
        sync_if_stale(force=False)
        sync_gsinfo_unit_database()
    except Exception:
        # startup must not fail if external sources are unavailable
        return
