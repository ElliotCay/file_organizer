"""Detect unorganized screenshots."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

from config import HOME_DIR, DATA_DIR


SCREENSHOTS_DATA = DATA_DIR / "screenshots.json"

# Common screenshot locations
SCREENSHOT_LOCATIONS = [
    HOME_DIR / "Desktop",
    HOME_DIR / "Downloads",
    HOME_DIR / "Documents",
]


def is_screenshot(file_path: Path) -> bool:
    """Determine if a file is likely a screenshot."""
    name = file_path.name.lower()

    # macOS screenshot patterns
    patterns = [
        "screenshot",
        "screen shot",
        "capture d'écran",
        "capture d\\'écran",
    ]

    # Check if filename matches screenshot patterns
    for pattern in patterns:
        if pattern in name:
            return True

    # Check for default macOS screenshot naming pattern
    # e.g., "Screenshot 2025-10-19 at 22.30.45.png"
    if name.startswith(("screenshot ", "screen shot ")):
        return True

    return False


def find_screenshots() -> List[Dict[str, any]]:
    """Find all screenshots in common locations."""
    screenshots = []

    for location in SCREENSHOT_LOCATIONS:
        if not location.exists():
            continue

        try:
            # Look for image files
            for ext in [".png", ".jpg", ".jpeg", ".tiff", ".gif"]:
                for file_path in location.glob(f"*{ext}"):
                    if is_screenshot(file_path):
                        try:
                            stat = file_path.stat()
                            age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days

                            screenshots.append({
                                "name": file_path.name,
                                "path": str(file_path),
                                "location": location.name,
                                "size_kb": round(stat.st_size / 1024, 2),
                                "created": datetime.fromtimestamp(stat.st_birthtime).isoformat(),
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "age_days": age_days
                            })
                        except (OSError, PermissionError):
                            pass
        except (OSError, PermissionError):
            pass

    # Sort by creation date (newest first)
    screenshots.sort(key=lambda x: x["created"], reverse=True)
    return screenshots


def get_screenshots_stats(screenshots: List[Dict]) -> Dict[str, any]:
    """Calculate statistics about screenshots."""
    if not screenshots:
        return {
            "total_count": 0,
            "total_size_mb": 0,
            "on_desktop": 0,
            "on_downloads": 0,
            "older_than_7_days": 0,
            "older_than_30_days": 0,
        }

    total_size_kb = sum(s["size_kb"] for s in screenshots)
    on_desktop = sum(1 for s in screenshots if s["location"] == "Desktop")
    on_downloads = sum(1 for s in screenshots if s["location"] == "Downloads")
    older_than_7 = sum(1 for s in screenshots if s["age_days"] > 7)
    older_than_30 = sum(1 for s in screenshots if s["age_days"] > 30)

    return {
        "total_count": len(screenshots),
        "total_size_mb": round(total_size_kb / 1024, 2),
        "on_desktop": on_desktop,
        "on_downloads": on_downloads,
        "older_than_7_days": older_than_7,
        "older_than_30_days": older_than_30,
    }


def collect_screenshots_data() -> Dict[str, any]:
    """Collect screenshots data."""
    print("📸 Détection des captures d'écran...")

    screenshots = find_screenshots()
    stats = get_screenshots_stats(screenshots)

    data = {
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "screenshots": screenshots[:20],  # Keep only most recent 20 for display
    }

    # Save to file
    with open(SCREENSHOTS_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ {stats['total_count']} captures d'écran non triées trouvées")
    return data


if __name__ == "__main__":
    collect_screenshots_data()
