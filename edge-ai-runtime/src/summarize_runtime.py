#!/usr/bin/env python3
"""Summarize generic inference events without a vendor runtime dependency."""

from __future__ import annotations

import argparse
import collections
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable


REQUIRED_FIELDS = {"event", "timestamp_us", "frame_id", "stream"}


def nearest_rank(values: Iterable[float]) -> dict[str, float | int] | None:
    ordered = sorted(values)
    if not ordered:
        return None
    return {
        "count": len(ordered),
        "mean": statistics.mean(ordered),
        "median": statistics.median(ordered),
        "p95": ordered[math.ceil(0.95 * len(ordered)) - 1],
        "p99": ordered[math.ceil(0.99 * len(ordered)) - 1],
        "min": ordered[0],
        "max": ordered[-1],
    }


def load_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    malformed = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not isinstance(event, dict) or not REQUIRED_FIELDS.issubset(event):
            malformed += 1
            continue
        events.append(event)
    events.sort(key=lambda event: event["timestamp_us"])
    return events, malformed


def sequence_gap(sequences: list[int], modulus: int = 2**32) -> dict[str, int | float | None]:
    if len(sequences) < 2:
        return {"observed": len(sequences), "gap_count": None, "gap_rate": None}
    deltas = [(current - previous) % modulus for previous, current in zip(sequences, sequences[1:])]
    if not all(0 < delta < modulus // 2 for delta in deltas):
        return {"observed": len(sequences), "gap_count": None, "gap_rate": None}
    gap_count = sum(delta - 1 for delta in deltas)
    return {
        "observed": len(sequences),
        "gap_count": gap_count,
        "gap_rate": gap_count / sum(deltas),
    }


def summarize(events: list[dict[str, Any]], warmup: int = 10) -> dict[str, Any]:
    if warmup < 0:
        raise ValueError("warmup must be non-negative")

    counts = dict(collections.Counter(event["event"] for event in events))
    grouped: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for event in events:
        if event["event"] == "inference_end" and isinstance(event.get("latency_us"), (int, float)):
            grouped[str(event["stream"])].append(event)

    streams = []
    for stream, completed in sorted(grouped.items()):
        steady = completed[warmup:]
        latencies = [float(event["latency_us"]) for event in steady]
        elapsed_s = 0.0
        if len(steady) > 1:
            elapsed_s = (steady[-1]["timestamp_us"] - steady[0]["timestamp_us"]) / 1_000_000
        input_sequences = [
            int(event["sequence"])
            for event in events
            if event["event"] == "input" and str(event["stream"]) == stream and isinstance(event.get("sequence"), int)
        ]
        streams.append(
            {
                "stream": stream,
                "completed": len(completed),
                "warmup_excluded": min(warmup, len(completed)),
                "execute_latency_us": nearest_rank(latencies),
                "completion_interval_fps": (len(steady) - 1) / elapsed_s if elapsed_s > 0 else None,
                "input_sequence": sequence_gap(input_sequences),
            }
        )

    input_ids = {(str(event["stream"]), event["frame_id"]) for event in events if event["event"] == "input"}
    completed_ids = {
        (str(event["stream"]), event["frame_id"]) for event in events if event["event"] == "inference_end"
    }
    return {
        "counts": counts,
        "streams": streams,
        "correspondence": {
            "input_unique": len(input_ids),
            "completed_unique": len(completed_ids),
            "input_without_completion_at_stop": len(input_ids - completed_ids),
        },
        "notes": [
            "FPS uses intervals between steady-state inference completions.",
            "Sequence gaps do not prove physical camera frame loss.",
            "In-flight work at shutdown may appear incomplete.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize generic inference events")
    parser.add_argument("events", type=Path)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    events, malformed = load_events(args.events)
    result = summarize(events, args.warmup)
    result["malformed_lines"] = malformed
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
