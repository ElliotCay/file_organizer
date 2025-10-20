"""Collect Notes app data for productivity tracking."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

from config import HOME_DIR, DATA_DIR


NOTES_DATA = DATA_DIR / "notes.json"

# Notes database location (may vary by macOS version)
NOTES_DB_PATHS = [
    HOME_DIR / "Library" / "Group Containers" / "group.com.apple.notes" / "NoteStore.sqlite",
    HOME_DIR / "Library" / "Containers" / "com.apple.Notes" / "Data" / "Library" / "Notes" / "NotesV7.storedata",
]


def find_notes_database() -> Path:
    """Find the Notes database file."""
    for db_path in NOTES_DB_PATHS:
        if db_path.exists():
            return db_path
    return None


def get_notes_stats() -> Dict[str, any]:
    """Get statistics from Notes app."""
    db_path = find_notes_database()

    if not db_path:
        print("⚠️  Base de données Notes non trouvée")
        return {
            "total_notes": 0,
            "notes_this_week": 0,
            "notes_modified_this_week": 0,
            "error": "Notes database not found"
        }

    try:
        # Make a copy to avoid locking issues
        import shutil
        import tempfile

        with tempfile.NamedTemporaryFile(suffix='.sqlite', delete=False) as tmp_file:
            temp_db = Path(tmp_file.name)

        shutil.copy2(db_path, temp_db)

        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        now = datetime.now()
        week_ago = now - timedelta(days=7)
        week_ago_timestamp = int(week_ago.timestamp())

        # Try to get note counts (schema may vary)
        try:
            # Total notes
            cursor.execute("""
                SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT
                WHERE ZTITLE IS NOT NULL AND ZMARKEDFORDELETION = 0
            """)
            total_notes = cursor.fetchone()[0]

            # Notes created this week (Core Data uses reference date from 2001-01-01)
            # Convert Unix timestamp to Core Data timestamp
            core_data_epoch = datetime(2001, 1, 1)
            unix_epoch = datetime(1970, 1, 1)
            offset = (unix_epoch - core_data_epoch).total_seconds()
            week_ago_core_data = week_ago_timestamp - offset

            cursor.execute("""
                SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT
                WHERE ZTITLE IS NOT NULL
                AND ZMARKEDFORDELETION = 0
                AND ZCREATIONDATE > ?
            """, (week_ago_core_data,))
            notes_this_week = cursor.fetchone()[0]

            # Notes modified this week
            cursor.execute("""
                SELECT COUNT(*) FROM ZICCLOUDSYNCINGOBJECT
                WHERE ZTITLE IS NOT NULL
                AND ZMARKEDFORDELETION = 0
                AND ZMODIFICATIONDATE > ?
            """, (week_ago_core_data,))
            notes_modified_this_week = cursor.fetchone()[0]

            # Get longest notes
            cursor.execute("""
                SELECT ZTITLE, LENGTH(ZDATA) as content_length
                FROM ZICCLOUDSYNCINGOBJECT
                WHERE ZTITLE IS NOT NULL AND ZMARKEDFORDELETION = 0
                ORDER BY content_length DESC
                LIMIT 5
            """)
            longest_notes = [
                {"title": row[0], "length": row[1]}
                for row in cursor.fetchall()
            ]

            conn.close()
            temp_db.unlink()  # Clean up temp file

            return {
                "total_notes": total_notes,
                "notes_this_week": notes_this_week,
                "notes_modified_this_week": notes_modified_this_week,
                "longest_notes": longest_notes,
            }

        except sqlite3.OperationalError as e:
            print(f"⚠️  Erreur de schéma Notes: {e}")
            conn.close()
            temp_db.unlink()
            return {
                "total_notes": 0,
                "notes_this_week": 0,
                "notes_modified_this_week": 0,
                "error": f"Schema error: {str(e)}"
            }

    except Exception as e:
        print(f"⚠️  Erreur lors de l'accès à Notes: {e}")
        return {
            "total_notes": 0,
            "notes_this_week": 0,
            "notes_modified_this_week": 0,
            "error": str(e)
        }


def collect_notes_data() -> Dict[str, any]:
    """Collect Notes app data."""
    print("📝 Analyse des notes...")

    data = {
        "timestamp": datetime.now().isoformat(),
        "notes": get_notes_stats()
    }

    # Save to file
    with open(NOTES_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = data["notes"].get("total_notes", 0)
    print(f"✅ {total} notes trouvées")
    return data


if __name__ == "__main__":
    collect_notes_data()
