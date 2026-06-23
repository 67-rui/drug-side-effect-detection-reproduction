"""Small provenance helpers for generated result artifacts."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path


def file_manifest(path: str | Path) -> dict:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        return {
            'path': str(resolved),
            'exists': False,
        }

    digest = hashlib.sha256()
    with resolved.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)

    stat = resolved.stat()
    return {
        'path': str(resolved),
        'exists': True,
        'size_bytes': stat.st_size,
        'mtime': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        'sha256': digest.hexdigest(),
    }


def artifact_status(*, stale: bool, reason: str | None = None) -> dict:
    out = {'stale': stale}
    if reason:
        out['reason'] = reason
    return out
