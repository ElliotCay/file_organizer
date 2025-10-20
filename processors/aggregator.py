"""Aggregate data from all collectors."""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

from config import (
    STORAGE_DATA, DOWNLOADS_DATA, APP_USAGE_DATA,
    NOTES_DATA, SCREENSHOTS_DATA, MUSIC_DATA,
    WEEKLY_ARCHIVES
)


def load_json_data(file_path: Path) -> Dict:
    """Load JSON data from file, return empty dict if file doesn't exist."""
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️  Erreur de lecture: {file_path}")
            return {}
    return {}


def load_historical_weeks(weeks: int = 8) -> List[Dict]:
    """Load historical weekly archives."""
    archives = []

    if not WEEKLY_ARCHIVES.exists():
        return archives

    # Get all archive files
    archive_files = sorted(WEEKLY_ARCHIVES.glob("week_*.json"), reverse=True)

    for archive_file in archive_files[:weeks]:
        try:
            with open(archive_file, "r") as f:
                data = json.load(f)
                archives.append(data)
        except (json.JSONDecodeError, OSError):
            pass

    return archives


def calculate_trends(current: Dict, historical: List[Dict]) -> Dict[str, any]:
    """Calculate trends comparing current week to historical data."""
    if not historical:
        return {}

    trends = {}

    # Storage trend
    current_used = current.get("storage", {}).get("disk_usage", {}).get("percent_used", 0)
    if historical:
        prev_used = historical[0].get("storage", {}).get("disk_usage", {}).get("percent_used", 0)
        trends["storage_trend"] = "↗️" if current_used > prev_used else "↘️" if current_used < prev_used else "→"

    # Downloads trend
    current_downloads = current.get("downloads", {}).get("downloads", {}).get("total_files", 0)
    if historical:
        prev_downloads = historical[0].get("downloads", {}).get("downloads", {}).get("total_files", 0)
        trends["downloads_trend"] = "↗️" if current_downloads > prev_downloads else "↘️" if current_downloads < prev_downloads else "→"

    # Screenshots trend
    current_screenshots = current.get("screenshots", {}).get("stats", {}).get("total_count", 0)
    if historical:
        prev_screenshots = historical[0].get("screenshots", {}).get("stats", {}).get("total_count", 0)
        trends["screenshots_trend"] = "↗️" if current_screenshots > prev_screenshots else "↘️" if current_screenshots < prev_screenshots else "→"

    # Music sessions trend
    current_music = current.get("music", {}).get("stats", {}).get("sessions_this_week", 0)
    if historical:
        prev_music = historical[0].get("music", {}).get("stats", {}).get("sessions_this_week", 0)
        trends["music_trend"] = "↗️" if current_music > prev_music else "↘️" if current_music < prev_music else "→"

    return trends


def calculate_health_score(data: Dict) -> int:
    """Calculate an overall system health score (0-100)."""
    score = 100

    # Disk space check (up to -30 points)
    disk_usage = data.get("storage", {}).get("disk_usage", {})
    percent_used = disk_usage.get("percent_used", 0)
    if percent_used > 95:
        score -= 30
    elif percent_used > 90:
        score -= 20
    elif percent_used > 80:
        score -= 10

    # Downloads folder check (up to -15 points)
    downloads = data.get("downloads", {}).get("downloads", {})
    unused_count = downloads.get("unused_count", 0)
    if unused_count > 100:
        score -= 15
    elif unused_count > 50:
        score -= 10
    elif unused_count > 20:
        score -= 5

    # Running apps check (up to -10 points)
    running_count = data.get("apps", {}).get("running_count", 0)
    if running_count > 30:
        score -= 10
    elif running_count > 20:
        score -= 5

    # Screenshots check (up to -15 points)
    screenshots_count = data.get("screenshots", {}).get("stats", {}).get("total_count", 0)
    if screenshots_count > 100:
        score -= 15
    elif screenshots_count > 50:
        score -= 10
    elif screenshots_count > 20:
        score -= 5

    return max(0, min(100, score))


def generate_insights(data: Dict) -> List[Dict[str, str]]:
    """Generate automated insights and recommendations."""
    insights = []

    # Storage insights
    disk_usage = data.get("storage", {}).get("disk_usage", {})
    free_gb = disk_usage.get("free_gb", 0)
    percent_used = disk_usage.get("percent_used", 0)

    if percent_used > 90:
        insights.append({
            "icon": "⚠️",
            "type": "warning",
            "title": f"Espace disque critique: {free_gb} GB libres",
            "message": f"Ton disque est plein à {percent_used}%. Il est temps de faire du ménage!",
            "action": "Voir les gros fichiers"
        })
    elif percent_used > 80:
        insights.append({
            "icon": "💾",
            "type": "info",
            "title": f"Espace disque: {free_gb} GB libres",
            "message": f"Tu utilises {percent_used}% de ton disque. Pense à libérer de l'espace bientôt.",
            "action": "Analyser le stockage"
        })

    # Downloads insights
    downloads = data.get("downloads", {}).get("downloads", {})
    unused_count = downloads.get("unused_count", 0)
    total_files = downloads.get("total_files", 0)

    if unused_count > 20:
        insights.append({
            "icon": "📥",
            "type": "action",
            "title": f"{unused_count} fichiers non utilisés depuis 30 jours",
            "message": f"Tu as {total_files} fichiers dans Téléchargements dont {unused_count} inutilisés.",
            "action": "Nettoyer maintenant"
        })

    # Screenshots insights
    screenshots = data.get("screenshots", {}).get("stats", {})
    screenshots_count = screenshots.get("total_count", 0)
    on_desktop = screenshots.get("on_desktop", 0)

    if screenshots_count > 20:
        insights.append({
            "icon": "📸",
            "type": "action",
            "title": f"{screenshots_count} captures d'écran non triées",
            "message": f"{on_desktop} sont sur ton Bureau. Organise-les dans des dossiers!",
            "action": None
        })

    # Recent apps
    recent_apps = data.get("apps", {}).get("recent_apps", [])
    if recent_apps:
        app_names = ", ".join([app["name"] for app in recent_apps[:3]])
        insights.append({
            "icon": "✨",
            "type": "info",
            "title": f"Nouvelles apps cette semaine",
            "message": f"Tu as installé: {app_names}",
            "action": None
        })

    # Music insights
    music_stats = data.get("music", {}).get("stats", {})
    sessions_week = music_stats.get("sessions_this_week", 0)
    favorite_app = music_stats.get("favorite_app")

    if sessions_week > 0 and favorite_app:
        insights.append({
            "icon": "🎵",
            "type": "info",
            "title": f"Activité musicale: {sessions_week} sessions",
            "message": f"Tu préfères {favorite_app} cette semaine.",
            "action": None
        })

    # Notes insights
    notes_data = data.get("notes", {}).get("notes", {})
    notes_this_week = notes_data.get("notes_this_week", 0)
    notes_modified = notes_data.get("notes_modified_this_week", 0)

    if notes_this_week > 0 or notes_modified > 5:
        insights.append({
            "icon": "📝",
            "type": "info",
            "title": "Productivité Notes",
            "message": f"{notes_this_week} notes créées, {notes_modified} modifiées cette semaine.",
            "action": None
        })

    # Large files
    large_items = data.get("storage", {}).get("large_items", [])
    if large_items:
        largest = large_items[0]
        insights.append({
            "icon": "📦",
            "type": "info",
            "title": f"Fichier le plus volumineux",
            "message": f"{largest['name']}: {largest['size_gb']} GB",
            "action": "Voir tous les gros fichiers"
        })

    return insights


def aggregate_all_data() -> Dict:
    """Aggregate data from all collectors."""
    print("🔄 Agrégation des données...")

    # Load current data
    storage = load_json_data(STORAGE_DATA)
    downloads = load_json_data(DOWNLOADS_DATA)
    apps = load_json_data(APP_USAGE_DATA)
    notes = load_json_data(NOTES_DATA)
    screenshots = load_json_data(SCREENSHOTS_DATA)
    music = load_json_data(MUSIC_DATA)

    # Load historical data
    historical = load_historical_weeks(8)

    # Combine all data
    aggregated = {
        "timestamp": datetime.now().isoformat(),
        "week_start": (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"),
        "storage": storage,
        "downloads": downloads,
        "apps": apps,
        "notes": notes,
        "screenshots": screenshots,
        "music": music,
        "historical": historical,
    }

    # Calculate metrics
    aggregated["health_score"] = calculate_health_score(aggregated)
    aggregated["trends"] = calculate_trends(aggregated, historical)
    aggregated["insights"] = generate_insights(aggregated)

    print(f"✅ Données agrégées - Score santé: {aggregated['health_score']}/100")
    return aggregated


def save_weekly_archive(data: Dict):
    """Save a weekly archive of the data."""
    week_start = data.get("week_start", datetime.now().strftime("%Y-%m-%d"))
    archive_file = WEEKLY_ARCHIVES / f"week_{week_start}.json"

    # Don't save historical in the archive to avoid bloat
    archive_data = {k: v for k, v in data.items() if k != "historical"}

    with open(archive_file, "w") as f:
        json.dump(archive_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Archive sauvegardée: {archive_file.name}")


if __name__ == "__main__":
    data = aggregate_all_data()
    save_weekly_archive(data)
