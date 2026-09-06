import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('smoke', Path(__file__).resolve().parents[1] / 'scripts/smoke_test.py')
smoke = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(smoke)


class RedrawMetricsTests(unittest.TestCase):
    def test_exact_framebuffer(self):
        self.assertTrue(smoke.redraw_matches({'pixels': 700000, 'changedPixels': 0, 'maxChannelDelta': 0}))

    def test_isolated_single_level_quantization(self):
        self.assertTrue(smoke.redraw_matches({'pixels': 700000, 'changedPixels': 7, 'maxChannelDelta': 1}))

    def test_larger_color_difference_fails(self):
        self.assertFalse(smoke.redraw_matches({'pixels': 700000, 'changedPixels': 1, 'maxChannelDelta': 2}))

    def test_widespread_small_difference_fails(self):
        self.assertFalse(smoke.redraw_matches({'pixels': 700000, 'changedPixels': 71, 'maxChannelDelta': 1}))

    def test_empty_framebuffer_fails(self):
        self.assertFalse(smoke.redraw_matches({'pixels': 0, 'changedPixels': 0, 'maxChannelDelta': 0}))


if __name__ == '__main__': unittest.main()
