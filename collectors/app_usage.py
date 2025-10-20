"""Collect application usage statistics."""
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

from config import APP_USAGE_DATA


def get_running_apps() -> List[str]:
    """Get list of currently running applications."""
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get name of (processes where background only is false)'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            apps = result.stdout.strip().split(", ")
            return [app for app in apps if app and app != ""]
        return []
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"⚠️  Erreur lors de la récupération des apps: {e}")
        return []


def get_installed_apps() -> List[Dict[str, str]]:
    """Get list of installed applications."""
    apps = []
    apps_dir = Path("/Applications")

    try:
        for app_path in apps_dir.glob("*.app"):
            try:
                stat = app_path.stat()
                # Use st_birthtime (creation time) for actual install date
                created = datetime.fromtimestamp(stat.st_birthtime).isoformat()
                apps.append({
                    "name": app_path.stem,
                    "path": str(app_path),
                    "size_mb": round(get_app_size(app_path) / (1024**2), 2),
                    "created": created,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass

    # Also check user Applications
    user_apps_dir = Path.home() / "Applications"
    if user_apps_dir.exists():
        try:
            for app_path in user_apps_dir.glob("*.app"):
                try:
                    stat = app_path.stat()
                    created = datetime.fromtimestamp(stat.st_birthtime).isoformat()
                    apps.append({
                        "name": app_path.stem,
                        "path": str(app_path),
                        "size_mb": round(get_app_size(app_path) / (1024**2), 2),
                        "created": created,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except (OSError, PermissionError):
                    pass
        except (OSError, PermissionError):
            pass

    return apps


def get_app_size(app_path: Path) -> int:
    """Get total size of an application bundle."""
    total = 0
    try:
        for entry in app_path.rglob("*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total


def get_recent_apps(days: int = 7) -> List[Dict[str, str]]:
    """Get recently installed applications (based on creation date)."""
    all_apps = get_installed_apps()
    cutoff = datetime.now() - timedelta(days=days)

    recent = [
        app for app in all_apps
        if datetime.fromisoformat(app["created"]) > cutoff
    ]

    recent.sort(key=lambda x: x["created"], reverse=True)
    return recent


def collect_app_usage_data() -> Dict[str, any]:
    """Collect application usage data."""
    print("💻 Analyse des applications...")

    running = get_running_apps()
    installed = get_installed_apps()
    recent = get_recent_apps(7)

    data = {
        "timestamp": datetime.now().isoformat(),
        "running_apps": running,
        "running_count": len(running),
        "installed_count": len(installed),
        "recent_apps": recent[:5],
        "total_apps_size_gb": round(sum(app["size_mb"] for app in installed) / 1024, 2),
        # Note: Real usage time tracking would require screen time API or accessibility permissions
        # This is a simplified version
        "top_apps": []  # Placeholder for actual usage tracking
    }

    # Save to file
    with open(APP_USAGE_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ {data['running_count']} applications en cours d'exécution")
    return data


if __name__ == "__main__":
    collect_app_usage_data()
