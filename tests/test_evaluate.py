"""Tests for evaluation metrics, confusion matrix, OOD AUROC/AUPR, and histogram generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    import torch
    from PIL import Image

    from src.evaluate import plot_confidence_ood_histogram, plot_confusion_matrix, plot_ood_curves
    from src.model import build_resnet50_classifier, save_checkpoint
    from src.reject import RejectionConfig

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


@unittest.skipUnless(DEPS_AVAILABLE, "Requires NumPy, Pandas, PyTorch, Pillow, Matplotlib, and Scikit-learn")
class TestEvaluationPipeline(unittest.TestCase):
    def test_plot_helpers_generate_png_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            cm = np.array([[8, 1], [1, 9]])
            cm_path = tmp_dir / "confusion_matrix.png"
            plot_confusion_matrix(cm, ["Species_A", "Species_B"], cm_path)
            self.assertTrue(cm_path.exists() and cm_path.stat().st_size > 100)

            id_scores = np.array([0.92, 0.89, 0.95, 0.84, 0.91])
            ood_scores = np.array([0.31, 0.42, 0.25, 0.49, 0.37])
            ood_curve_path = tmp_dir / "ood_curves.png"
            auroc, aupr = plot_ood_curves(id_scores, ood_scores, "MSP", ood_curve_path)
            self.assertTrue(ood_curve_path.exists() and ood_curve_path.stat().st_size > 100)
            self.assertGreater(auroc, 0.95)
            self.assertGreater(aupr, 0.95)

            hist_path = tmp_dir / "confidence_hist.png"
            plot_confidence_ood_histogram(
                id_scores,
                ood_scores,
                np.array([-5.0, -4.5, -5.2, -4.1, -4.8]),
                np.array([-1.0, -1.3, -0.8, -1.5, -1.2]),
                0.70,
                hist_path,
            )
            self.assertTrue(hist_path.exists() and hist_path.stat().st_size > 100)


if __name__ == "__main__":
    unittest.main()
