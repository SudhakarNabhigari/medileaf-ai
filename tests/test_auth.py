"""Unit tests for SQLite PBKDF2 authentication and prediction history persistence (stdlib only)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from auth.authentication import (
    authenticate_user,
    change_password,
    clear_prediction_history,
    get_prediction_history,
    get_user_preferences,
    init_db,
    register_user,
    save_prediction_record,
    update_user_preferences,
)


class TestAuthenticationAndHistory(unittest.TestCase):
    def test_register_authenticate_change_password_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test_medileaf.db"
            init_db(db)

            ok, _, user = register_user("botanist01", "botanist@example.edu", "StrongPass!23", db_path=db)
            self.assertTrue(ok)
            self.assertIsNotNone(user)

            # Duplicate registration rejected
            ok_dup, _, _ = register_user("botanist01", "botanist@example.edu", "StrongPass!23", db_path=db)
            self.assertFalse(ok_dup)

            # Wrong password rejected
            ok_bad, _, _ = authenticate_user("botanist01", "WrongPass!", db_path=db)
            self.assertFalse(ok_bad)

            # Login by email succeeds
            ok_good, _, auth_user = authenticate_user("botanist@example.edu", "StrongPass!23", db_path=db)
            self.assertTrue(ok_good)
            self.assertEqual(auth_user["username"], "botanist01")

            # Change password
            ok_chg, _ = change_password(auth_user["id"], "StrongPass!23", "NewSecurePass!99", db_path=db)
            self.assertTrue(ok_chg)
            ok_old, _, _ = authenticate_user("botanist01", "StrongPass!23", db_path=db)
            self.assertFalse(ok_old)
            ok_new, _, _ = authenticate_user("botanist01", "NewSecurePass!99", db_path=db)
            self.assertTrue(ok_new)

            # Preferences
            prefs = get_user_preferences(auth_user["id"], db_path=db)
            self.assertTrue(prefs["save_history_enabled"])
            update_user_preferences(auth_user["id"], "Dark", False, True, db_path=db)
            self.assertEqual(get_user_preferences(auth_user["id"], db_path=db)["theme"], "Dark")

            # History
            save_prediction_record(
                user_id=auth_user["id"],
                filename="leaf_01.jpg",
                predicted_species="UNCERTAIN",
                confidence=0.41,
                energy_score=-1.2,
                status="Rejected",
                reason="Below threshold",
                db_path=db,
            )
            hist = get_prediction_history(auth_user["id"], db_path=db)
            self.assertEqual(len(hist), 1)
            self.assertEqual(hist[0]["predicted_species"], "UNCERTAIN")

            clear_prediction_history(auth_user["id"], db_path=db)
            self.assertEqual(len(get_prediction_history(auth_user["id"], db_path=db)), 0)


if __name__ == "__main__":
    unittest.main()
