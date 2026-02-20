"""
Pytest runtime configuration for stable temp-directory handling.

Some environments deny access to default OS temp roots or previously-created
pytest temp folders. Force a unique, workspace-local basetemp per run so
`tmp_path` fixtures always resolve to writable locations.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path


def pytest_configure(config):
    """Assign a unique writable basetemp unless caller already provided one."""
    if getattr(config.option, "basetemp", None):
        return

    project_root = Path(__file__).resolve().parent
    run_root = project_root / ".pytest-runs" / uuid.uuid4().hex
    run_root.mkdir(parents=True, exist_ok=True)

    # Pytest will create/use this for tmp_path/tmp_path_factory internals.
    basetemp = run_root / "basetemp"
    config.option.basetemp = str(basetemp)

    # Keep stdlib tempfile users on the same writable root.
    tmp_root = str(run_root)
    for key in ("TMPDIR", "TEMP", "TMP"):
        os.environ.setdefault(key, tmp_root)
