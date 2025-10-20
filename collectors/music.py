"""Track music listening time from Apple Music and Spotify."""
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

from config import HOME_DIR, DATA_DIR


MUSIC_DATA = DATA_DIR / "music.json"


def get_music_app_playing() -> Dict[str, any]:
    """Check if Music app is currently playing and get track info."""
    try:
        # Check if Music is running
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Music" to player state as string'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode != 0:
            return {"is_playing": False, "app": "Music"}

        state = result.stdout.strip()

        if state == "playing":
            # Get current track info
            track_info = subprocess.run(
                ["osascript", "-e", '''
                    tell application "Music"
                        set trackName to name of current track
                        set artistName to artist of current track
                        set albumName to album of current track
                        return trackName & " | " & artistName & " | " & albumName
                    end tell
                '''],
                capture_output=True,
                text=True,
                timeout=2
            )

            if track_info.returncode == 0:
                parts = track_info.stdout.strip().split(" | ")
                return {
                    "is_playing": True,
                    "app": "Music",
                    "track": parts[0] if len(parts) > 0 else "Unknown",
                    "artist": parts[1] if len(parts) > 1 else "Unknown",
                    "album": parts[2] if len(parts) > 2 else "Unknown",
                }

        return {"is_playing": state == "playing", "app": "Music"}

    except Exception as e:
        return {"is_playing": False, "app": "Music", "error": str(e)}


def get_spotify_playing() -> Dict[str, any]:
    """Check if Spotify is currently playing."""
    try:
        # Check if Spotify is running
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Spotify" to player state as string'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode != 0:
            return {"is_playing": False, "app": "Spotify"}

        state = result.stdout.strip()

        if state == "playing":
            # Get current track info
            track_info = subprocess.run(
                ["osascript", "-e", '''
                    tell application "Spotify"
                        set trackName to name of current track
                        set artistName to artist of current track
                        set albumName to album of current track
                        return trackName & " | " & artistName & " | " & albumName
                    end tell
                '''],
                capture_output=True,
                text=True,
                timeout=2
            )

            if track_info.returncode == 0:
                parts = track_info.stdout.strip().split(" | ")
                return {
                    "is_playing": True,
                    "app": "Spotify",
                    "track": parts[0] if len(parts) > 0 else "Unknown",
                    "artist": parts[1] if len(parts) > 1 else "Unknown",
                    "album": parts[2] if len(parts) > 2 else "Unknown",
                }

        return {"is_playing": state == "playing", "app": "Spotify"}

    except Exception as e:
        return {"is_playing": False, "app": "Spotify", "error": str(e)}


def load_historical_data() -> List[Dict]:
    """Load historical music listening data."""
    if MUSIC_DATA.exists():
        try:
            with open(MUSIC_DATA, "r") as f:
                data = json.load(f)
                return data.get("history", [])
        except json.JSONDecodeError:
            return []
    return []


def calculate_listening_stats(history: List[Dict]) -> Dict[str, any]:
    """Calculate listening statistics from history."""
    if not history:
        return {
            "sessions_today": 0,
            "sessions_this_week": 0,
            "total_sessions": 0,
            "favorite_app": None,
        }

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    sessions_today = sum(
        1 for s in history
        if datetime.fromisoformat(s["timestamp"]) >= today_start
    )

    sessions_this_week = sum(
        1 for s in history
        if datetime.fromisoformat(s["timestamp"]) >= week_ago
    )

    # Count by app
    app_counts = {}
    for session in history:
        if datetime.fromisoformat(session["timestamp"]) >= week_ago:
            app = session.get("app", "Unknown")
            app_counts[app] = app_counts.get(app, 0) + 1

    favorite_app = max(app_counts.items(), key=lambda x: x[1])[0] if app_counts else None

    return {
        "sessions_today": sessions_today,
        "sessions_this_week": sessions_this_week,
        "total_sessions": len(history),
        "favorite_app": favorite_app,
        "app_counts": app_counts,
    }


def collect_music_data() -> Dict[str, any]:
    """Collect music listening data."""
    print("🎵 Analyse de l'activité musicale...")

    # Check current playback
    music_status = get_music_app_playing()
    spotify_status = get_spotify_playing()

    # Load historical data
    history = load_historical_data()

    # Add current session to history if playing
    now = datetime.now().isoformat()
    if music_status["is_playing"]:
        history.append({
            "timestamp": now,
            "app": "Music",
            "track": music_status.get("track"),
            "artist": music_status.get("artist"),
        })
    elif spotify_status["is_playing"]:
        history.append({
            "timestamp": now,
            "app": "Spotify",
            "track": spotify_status.get("track"),
            "artist": spotify_status.get("artist"),
        })

    # Keep only last 1000 sessions to avoid bloat
    history = history[-1000:]

    # Calculate stats
    stats = calculate_listening_stats(history)

    data = {
        "timestamp": now,
        "current_music": music_status,
        "current_spotify": spotify_status,
        "stats": stats,
        "history": history,
    }

    # Save to file
    with open(MUSIC_DATA, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = stats["sessions_this_week"]
    print(f"✅ {total} sessions d'écoute cette semaine")
    return data


if __name__ == "__main__":
    collect_music_data()
