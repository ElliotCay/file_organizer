"""Configuration constants for the usage dashboard."""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DASHBOARD_DIR = BASE_DIR / "dashboard"
TEMPLATE_DIR = DASHBOARD_DIR / "templates"
STATIC_DIR = DASHBOARD_DIR / "static"
OUTPUT_DIR = BASE_DIR / "output"

# User paths
HOME_DIR = Path.home()
DOWNLOADS_DIR = HOME_DIR / "Downloads"
MESSAGES_DB = HOME_DIR / "Library" / "Messages" / "chat.db"
NOTES_DIR = HOME_DIR / "Library" / "Group Containers" / "group.com.apple.notes"

# Data files
STORAGE_DATA = DATA_DIR / "storage.json"
DOWNLOADS_DATA = DATA_DIR / "downloads.json"
APP_USAGE_DATA = DATA_DIR / "app_usage.json"
NOTES_DATA = DATA_DIR / "notes.json"
SCREENSHOTS_DATA = DATA_DIR / "screenshots.json"
MUSIC_DATA = DATA_DIR / "music.json"
WEEKLY_ARCHIVES = DATA_DIR / "archives"

# Create directories if they don't exist
for directory in [DATA_DIR, DASHBOARD_DIR, TEMPLATE_DIR, STATIC_DIR, OUTPUT_DIR, WEEKLY_ARCHIVES]:
    directory.mkdir(parents=True, exist_ok=True)

# Dashboard settings
DASHBOARD_TITLE = "Ta semaine"
REFRESH_INTERVAL_HOURS = 24
TOP_APPS_LIMIT = 10
TOP_CONTACTS_LIMIT = 5
TOP_SPACE_EATERS_LIMIT = 5

# Storage thresholds
LOW_SPACE_THRESHOLD_PERCENT = 10
CRITICAL_SPACE_THRESHOLD_PERCENT = 5

# File categories for storage analysis
FILE_CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".pages", ".xlsx", ".xls", ".pptx", ".ppt"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".heic", ".raw", ".cr2", ".nef"],
    "Vidéos": [".mp4", ".mov", ".avi", ".mkv", ".m4v"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".m4a"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".dmg"],
    "Code": [".py", ".js", ".java", ".cpp", ".h", ".swift", ".go", ".rs"],
    "Applications": [".app"],
}
