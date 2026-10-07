import sys
import unittest
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from summarize_temperature import summarize  # noqa: E402


class TemperatureSummaryTests(unittest.TestCase):
    def test_dominant_value_fraction_is_reported(self) -> None:
        samples = [
            {"region": "accelerator", "temperature_c": value}
            for value in [31.609, 31.609, 31.609, 32.000]
        ]
        result = summarize(samples)
        region = result["regions"]["accelerator"]
        self.assertEqual(region["dominant_value_c"], 31.609)
        self.assertEqual(region["dominant_fraction"], 0.75)


if __name__ == "__main__":
    unittest.main()
