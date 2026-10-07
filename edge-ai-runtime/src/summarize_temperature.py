#!/usr/bin/env python3
"""Summarize temperature samples and flag repeated dominant values."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import statistics
from pathlib import Path
from typing import Any


def load_samples(path: Path) -> list[dict[str, Any]]:
    samples = []
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            try:
                samples.append(
                    {
                        "timestamp_s": float(row["timestamp_s"]),
                        "region": row["region"],
                        "temperature_c": float(row["temperature_c"]),
                        "status": row.get("status", ""),
                    }
                )
            except (KeyError, ValueError):
                continue
    return samples


def summarize(samples: list[dict[str, Any]]) -> dict[str, Any]:
    regions: dict[str, list[float]] = collections.defaultdict(list)
    for sample in samples:
        regions[str(sample["region"])].append(float(sample["temperature_c"]))

    result = {}
    for region, values in sorted(regions.items()):
        rounded = [round(value, 3) for value in values]
        dominant_value, dominant_count = collections.Counter(rounded).most_common(1)[0]
        result[region] = {
            "count": len(values),
            "mean_c": round(statistics.mean(values), 6),
            "min_c": min(values),
            "max_c": max(values),
            "range_c": round(max(values) - min(values), 6),
            "dominant_value_c": dominant_value,
            "dominant_fraction": round(dominant_count / len(values), 6),
        }
    return {
        "regions": result,
        "note": "A parsed numeric value is not proof that the sensor reading is valid.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize region-based temperature samples")
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(load_samples(args.csv_file)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
