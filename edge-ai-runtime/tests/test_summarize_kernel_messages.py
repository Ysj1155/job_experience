import sys
import unittest
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from summarize_kernel_messages import summarize_text  # noqa: E402


class KernelMessageTests(unittest.TestCase):
    def test_matching_lines_are_counted_separately(self) -> None:
        text = "page fault\nGPU fault\nGPU fault followed by page fault\n"
        result = summarize_text(text)
        self.assertEqual(result["counts"]["page_fault_messages"], 2)
        self.assertEqual(result["counts"]["gpu_fault_messages"], 2)


if __name__ == "__main__":
    unittest.main()
