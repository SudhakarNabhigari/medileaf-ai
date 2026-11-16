"""Tests for confidence gating, Energy OOD scoring, and validation-only calibration."""

from __future__ import annotations

import unittest

try:
    import numpy as np
    import torch
    from src.reject import (
        RejectionConfig,
        calibrate_thresholds_on_validation,
        compute_scores_from_logits,
        evaluate_rejection_rule,
    )
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False


@unittest.skipUnless(DEPS_AVAILABLE, "Requires NumPy and PyTorch")
class TestRejectionMechanism(unittest.TestCase):
    def test_high_confidence_accepted_and_ambiguous_rejected(self) -> None:
        idx_to_class = {0: "Species_0", 1: "Species_1", 2: "Species_2"}
        cfg = RejectionConfig(
            gate_method="msp_and_energy",
            msp_threshold=0.75,
            energy_threshold=-2.0,
            energy_temperature=1.0,
        )

        # Sharp high-confidence logits -> accepted
        strong_logits = torch.tensor([[8.0, 0.2, 0.1]])
        dec_accept = evaluate_rejection_rule(strong_logits, idx_to_class, cfg)
        self.assertTrue(dec_accept.accepted)
        self.assertEqual(dec_accept.predicted_label, "Species_0")
        self.assertGreater(dec_accept.confidence, 0.90)

        # Flat ambiguous logits -> UNCERTAIN
        flat_logits = torch.tensor([[0.4, 0.35, 0.30]])
        dec_reject = evaluate_rejection_rule(flat_logits, idx_to_class, cfg)
        self.assertFalse(dec_reject.accepted)
        self.assertEqual(dec_reject.predicted_label, "UNCERTAIN")

    def test_validation_threshold_calibration(self) -> None:
        # 8 clear ID samples + 2 ambiguous misclassified samples
        logits = torch.tensor(
            [
                [6.0, 0.0, 0.0],
                [5.5, 0.1, 0.0],
                [0.0, 6.0, 0.0],
                [0.1, 5.2, 0.0],
                [0.0, 0.0, 6.5],
                [0.2, 0.0, 5.0],
                [5.0, 0.2, 0.1],
                [0.1, 5.1, 0.2],
                [0.6, 0.5, 0.4],
                [0.4, 0.5, 0.45],
            ]
        )
        labels = np.array([0, 0, 1, 1, 2, 2, 0, 1, 2, 0])
        cfg = calibrate_thresholds_on_validation(logits, labels, target_coverage=0.80)
        self.assertEqual(cfg.calibrated_on, "validation_manifest.csv")
        self.assertGreaterEqual(cfg.val_selective_accuracy, 0.95)


if __name__ == "__main__":
    unittest.main()
