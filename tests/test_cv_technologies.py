"""Unit tests verifying Computer Vision Architecture & Technologies catalog (stdlib only)."""

from __future__ import annotations

import unittest

from src.cv_technologies import get_cv_technologies


class TestCVTechnologiesCatalog(unittest.TestCase):
    def test_all_twelve_technologies_present_with_honest_statuses(self) -> None:
        items = get_cv_technologies()
        keys = {item.key for item in items}
        expected = {
            "cnn",
            "resnet50",
            "transfer_learning",
            "preprocessing",
            "augmentation",
            "softmax",
            "rejection",
            "ood",
            "evaluation",
            "pytorch",
            "opencv_pillow",
            "sklearn",
        }
        self.assertEqual(keys, expected)

        valid_statuses = {"IMPLEMENTED", "VERIFIED", "NOT IMPLEMENTED"}
        for item in items:
            self.assertIn(item.status, valid_statuses)
            self.assertTrue(len(item.what_is_this) > 20)
            self.assertTrue(len(item.why_used) > 20)
            self.assertTrue(len(item.where_used_in_medileaf) > 10)
            self.assertTrue(len(item.module_path) > 3)


if __name__ == "__main__":
    unittest.main()
