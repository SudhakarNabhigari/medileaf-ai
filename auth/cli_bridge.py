"""JSON stdin/stdout CLI bridge exposing auth/authentication.py to the Express preview server."""

from __future__ import annotations

import json
import sys

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


def main() -> None:
    init_db()
    payload = json.loads(sys.stdin.read() or "{}")
    action = payload.get("action")

    if action == "register":
        ok, msg, user = register_user(
            payload.get("username", ""),
            payload.get("email", ""),
            payload.get("password", ""),
        )
        print(json.dumps({"ok": ok, "message": msg, "user": user}))
    elif action == "login":
        ok, msg, user = authenticate_user(
            payload.get("identifier", ""),
            payload.get("password", ""),
        )
        print(json.dumps({"ok": ok, "message": msg, "user": user}))
    elif action == "change_password":
        ok, msg = change_password(
            int(payload["user_id"]),
            payload.get("current_password", ""),
            payload.get("new_password", ""),
        )
        print(json.dumps({"ok": ok, "message": msg}))
    elif action == "get_prefs":
        prefs = get_user_preferences(int(payload["user_id"]))
        print(json.dumps({"ok": True, "preferences": prefs}))
    elif action == "update_prefs":
        update_user_preferences(
            int(payload["user_id"]),
            payload.get("theme", "Light"),
            bool(payload.get("notifications_enabled", True)),
            bool(payload.get("save_history_enabled", True)),
        )
        print(json.dumps({"ok": True}))
    elif action == "get_history":
        rows = get_prediction_history(int(payload["user_id"]), limit=int(payload.get("limit", 50)))
        print(json.dumps({"ok": True, "history": rows}))
    elif action == "save_history":
        save_prediction_record(
            user_id=int(payload["user_id"]),
            filename=payload.get("filename", "upload.jpg"),
            predicted_species=payload.get("predicted_species", "UNCERTAIN"),
            confidence=payload.get("confidence"),
            energy_score=payload.get("energy_score"),
            status=payload.get("status", "Rejected"),
            reason=payload.get("reason", ""),
            image_thumbnail_b64=payload.get("image_thumbnail_b64"),
        )
        print(json.dumps({"ok": True}))
    elif action == "clear_history":
        clear_prediction_history(int(payload["user_id"]))
        print(json.dumps({"ok": True}))
    else:
        print(json.dumps({"ok": False, "message": f"Unknown action: {action}"}))


if __name__ == "__main__":
    main()
