#!/usr/bin/env python3
"""Run deterministic examples without board-specific drivers."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from validation_state_machine import ValidationStateMachine  # noqa: E402


def main() -> int:
    model = ValidationStateMachine(timeout_s=2.0, require_manual_recovery=True)

    model.heartbeat(time_s=0.0, sequence=1)
    model.heartbeat(time_s=0.5, sequence=2)
    model.check_timeout(time_s=2.51)
    model.manual_reset(time_s=2.6)
    model.heartbeat(time_s=3.0, sequence=3)
    model.manual_reset(time_s=3.1)
    model.driver_intervention(time_s=4.0, sequence=10)
    model.driver_intervention(time_s=4.1, sequence=10)

    for event in model.events:
        print(json.dumps(event.to_dict(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
