import json
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from summarize_runtime import load_events, sequence_gap, summarize  # noqa: E402


class RuntimeSummaryTests(unittest.TestCase):
    def test_warmup_latency_fps_and_sequence_wrap(self) -> None:
        events = []
        for frame_id, (sequence, latency) in enumerate([(2**32 - 1, 900), (1, 10), (2, 20)]):
            timestamp = frame_id * 1000
            events.append(
                {"event": "input", "timestamp_us": timestamp, "frame_id": frame_id, "stream": "camera0", "sequence": sequence}
            )
            events.append(
                {
                    "event": "inference_end",
                    "timestamp_us": timestamp + 100,
                    "frame_id": frame_id,
                    "stream": "camera0",
                    "latency_us": latency,
                }
            )
        result = summarize(events, warmup=1)
        stream = result["streams"][0]
        self.assertEqual(stream["execute_latency_us"]["mean"], 15)
        self.assertEqual(stream["execute_latency_us"]["p99"], 20)
        self.assertEqual(stream["completion_interval_fps"], 1000)
        self.assertEqual(stream["input_sequence"]["gap_count"], 1)

    def test_malformed_lines_are_counted(self) -> None:
        valid = {"event": "input", "timestamp_us": 1, "frame_id": 1, "stream": "s"}
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "events.jsonl"
            path.write_text(json.dumps(valid) + "\nnot-json\n{}\n", encoding="utf-8")
            events, malformed = load_events(path)
        self.assertEqual(len(events), 1)
        self.assertEqual(malformed, 2)

    def test_invalid_sequence_order_returns_unknown_gap(self) -> None:
        result = sequence_gap([10, 9])
        self.assertIsNone(result["gap_count"])


if __name__ == "__main__":
    unittest.main()
