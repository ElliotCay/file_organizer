"""Collect and analyze disk storage information."""
import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import subprocess

from config import FILE_CATEGORIES, HOME_DIR, STORAGE_DATA


def get_disk_usage() -> Dict[str, any]:
    """Get overall disk usage statistics."""
    usage = shutil.disk_usage("/")

    return {
        "total_gb": round(usage.total / (1024**3), 2),
        "used_gb": round(usage.used / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
        "percent_used": round((usage.used / usage.total) * 100, 1),
        "timestamp": datetime.now().isoformat()
    }


def get_file_size(path: Path) -> int:
    """Get size of a file or directory in bytes."""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        total = 0
        try:
            for entry in path.rglob("*"):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total
    return 0


def categorize_files(directory: Path, max_depth: int = 3) -> Dict[str, int]:
    """Categorize files by type and calculate sizes."""
    categories = {cat: 0 for cat in FILE_CATEGORIES.keys()}
    categories["Autre"] = 0

    try:
        for item in directory.rglob("*"):
            if item.is_file():
                try:
                    size = item.stat().st_size
                    extension = item.suffix.lower()

                    categorized = False
                    for category, extensions in FILE_CATEGORIES.items():
                        if extension in extensions:
                            categories[category] += size
                            categorized = True
                            break

                    if not categorized:
                        categories["Autre"] += size

                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass

    # Convert to GB
    return {k: round(v / (1024**3), 2) for k, v in categories.items() if v > 0}


def find_large_files(directory: Path, limit: int = 10) -> List[Dict[str, any]]:
    """Find the largest files and directories."""
    items = []

    try:
        # Get top-level directories and files
        for item in directory.iterdir():
            try:
                if item.name.startswith("."):
                    continue

                size = get_file_size(item)
                if size > 100 * 1024 * 1024:  # Only items > 100MB
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "size_gb": round(size / (1024**3), 2),
                        "size_mb": round(size / (1024**2), 2),
                        "type": "dossier" if item.is_dir() else "fichier",
                        "extension": item.suffix if item.is_file() else None
                    })
            except (OSError, PermissionError):
                pass
    except (OSError, PermissionError):
        pass

    # Sort by size and return top items
    items.sort(key=lambda x: x["size_gb"], reverse=True)
    return items[:limit]


def collect_storage_data() -> Dict[str, any]:
    """Collect all storage-related data."""
    print("📊 Analyse du stockage...")

    data = {
        "timestamp": datetime.now().isoformat(),
        "disk_usage": get_disk_usage(),
        "categories": categorize_files(HOME_DIR),
        "large_items": find_large_files(HOME_DIR, limit=10),
    }

    # Save to file
    with open(STORAGE_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Données de stockage collectées: {data['disk_usage']['free_gb']} GB libres")
    return data


if __name__ == "__main__":
    collect_storage_data()
