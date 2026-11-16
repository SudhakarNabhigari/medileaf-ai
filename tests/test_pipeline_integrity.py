"""Stdlib integration, AST integrity, CLI bridge, and config verification tests."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import unittest
from pathlib import Path

from src.config import (
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD,
    MAX_UPLOAD_SIZE_BYTES,
    RESIZE_SHORTER_SIDE,
    ROOT_DIR,
    SAFETY_DISCLAIMER,
    VERIFIED_DATASET_METADATA,
)


class TestPipelineIntegrityAndCLI(unittest.TestCase):
    def test_config_constants_and_verified_metadata(self) -> None:
        self.assertEqual(IMAGE_SIZE, 224)
        self.assertEqual(RESIZE_SHORTER_SIDE, 256)
        self.assertEqual(IMAGENET_MEAN, (0.485, 0.456, 0.406))
        self.assertEqual(IMAGENET_STD, (0.229, 0.224, 0.225))
        self.assertEqual(MAX_UPLOAD_SIZE_BYTES, 10 * 1024 * 1024)
        self.assertEqual(VERIFIED_DATASET_METADATA["doi"], "10.17632/748f8jkphb.3")
        self.assertEqual(VERIFIED_DATASET_METADATA["version"], "3")
        self.assertIn("not medical advice", SAFETY_DISCLAIMER.lower())

    def test_no_llm_vision_replacement_in_python_pipeline(self) -> None:
        forbidden_tokens = ("google.generativeai", "google.genai", "openai", "anthropic")
        py_files = (
            list((ROOT_DIR / "src").glob("*.py"))
            + list((ROOT_DIR / "scripts").glob("*.py"))
            + list((ROOT_DIR / "pages").glob("*.py"))
            + [ROOT_DIR / "app.py"]
        )
        self.assertGreater(len(py_files), 10)
        for py_file in py_files:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(py_file))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        for bad in forbidden_tokens:
                            self.assertNotIn(bad, alias.name.lower(), f"Forbidden import in {py_file}")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for bad in forbidden_tokens:
                        self.assertNotIn(bad, node.module.lower(), f"Forbidden import in {py_file}")

    def test_eval_and_inference_share_same_transform_function(self) -> None:
        eval_src = (ROOT_DIR / "src" / "evaluate.py").read_text(encoding="utf-8")
        inf_src = (ROOT_DIR / "src" / "inference.py").read_text(encoding="utf-8")
        self.assertIn("get_eval_transforms", eval_src)
        self.assertIn("get_eval_transforms", inf_src)

    def test_colab_notebook_is_valid_nbformat_v4(self) -> None:
        nb_path = ROOT_DIR / "notebooks" / "medicinal_leaf_identifier_colab.ipynb"
        self.assertTrue(nb_path.exists())
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        self.assertEqual(nb.get("nbformat"), 4)
        self.assertGreaterEqual(len(nb.get("cells", [])), 8)
        full_src = "\n".join("".join(c.get("source", [])) for c in nb["cells"])
        for expected in ("inspect_dataset.py", "prepare_dataset.py", "src.train", "src.evaluate", "MediLeafPredictor"):
            self.assertIn(expected, full_src)

    def test_cv_technologies_cli_outputs_12_cards_json(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "src.cv_technologies"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=True,
        )
        items = json.loads(proc.stdout)
        self.assertEqual(len(items), 12)
        self.assertTrue(all(item["status"] in {"IMPLEMENTED", "VERIFIED", "NOT IMPLEMENTED"} for item in items))

    def test_auth_cli_bridge_handles_unknown_action_safely(self) -> None:
        proc = subprocess.run(
            [sys.executable, "-m", "auth.cli_bridge"],
            input=json.dumps({"action": "unknown_test_action"}),
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("Unknown action", payload["message"])


if __name__ == "__main__":
    unittest.main()
