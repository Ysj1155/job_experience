#!/usr/bin/env python3
"""Send newline-delimited heartbeat messages to a test receiver."""

from __future__ import annotations

import argparse
import json
import socket
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send heartbeat messages for a local validation demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=10001)
    parser.add_argument("--period-ms", type=int, default=500)
    parser.add_argument("--count", type=int, default=10)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.period_ms <= 0 or args.count <= 0:
        raise SystemExit("period-ms and count must be positive")

    with socket.create_connection((args.host, args.port), timeout=5.0) as connection:
        for sequence in range(args.count):
            message = {"type": "heartbeat", "sequence": sequence}
            connection.sendall((json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8"))
            print(message, flush=True)
            time.sleep(args.period_ms / 1000.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
