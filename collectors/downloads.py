"""Analyze downloads folder."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

from config import DOWNLOADS_DIR, DOWNLOADS_DATA, FILE_CATEGORIES


def get_download_stats() -> Dict[str, any]:
    """Get statistics about downloaded files."""
    if not DOWNLOADS_DIR.exists():
        return {}

    now = datetime.now()
    files_info = []
    file_types = Counter()

    try:
        for item in DOWNLOADS_DIR.iterdir():
            if item.is_file() and not item.name.startswith("."):
                try:
                    stat = item.stat()
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    age_days = (now - modified_time).days

                    extension = item.suffix.lower() or "sans extension"
                    file_types[extension] += 1

                    # Determine category
                    category = "Autre"
                    for cat, extensions in FILE_CATEGORIES.items():
                        if extension in extensions:
                            category = cat
                            break

                    files_info.append({
                        "name": item.name,
                        "size_mb": round(stat.st_size / (1024**2), 2),
                        "extension": extension,
                        "category": category,
                        "modified": modified_time.isoformat(),
                        "age_days": age_days,
                        "unused": age_days > 30
                    })
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        return {}

    # Sort by modification time (most recent first)
    files_info.sort(key=lambda x: x["modified"], reverse=True)

    # Calculate statistics
    total_files = len(files_info)
    total_size_mb = sum(f["size_mb"] for f in files_info)
    unused_files = [f for f in files_info if f["unused"]]

    # Files from this week
    week_ago = now - timedelta(days=7)
    this_week = [f for f in files_info if datetime.fromisoformat(f["modified"]) > week_ago]

    return {
        "total_files": total_files,
        "total_size_mb": round(total_size_mb, 2),
        "total_size_gb": round(total_size_mb / 1024, 2),
        "files_this_week": len(this_week),
        "unused_count": len(unused_files),
        "file_types": dict(file_types.most_common(10)),
        "recent_files": files_info[:20],
        "unused_files": unused_files[:10],
    }


def collect_downloads_data() -> Dict[str, any]:
    """Collect downloads folder data."""
    print("📥 Analyse des téléchargements...")

    data = {
        "timestamp": datetime.now().isoformat(),
        "downloads": get_download_stats()
    }

    # Save to file
    with open(DOWNLOADS_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ {data['downloads'].get('total_files', 0)} fichiers analysés dans Téléchargements")
    return data


if __name__ == "__main__":
    collect_downloads_data()
