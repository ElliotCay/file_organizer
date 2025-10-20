"""Generate HTML dashboard with Liquid Glass design from macOS 26."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

from config import OUTPUT_DIR


def prepare_chart_data(data: Dict) -> Dict[str, str]:
    """Prepare all chart data as JSON strings."""
    # Storage categories
    storage_categories = data.get("storage", {}).get("categories", {})

    # Large items
    large_items = data.get("storage", {}).get("large_items", [])[:5]

    # Downloads file types
    downloads = data.get("downloads", {}).get("downloads", {})
    file_types = downloads.get("file_types", {})

    # Historical data for trends
    historical = data.get("historical", [])

    # Prepare week labels and storage trend data
    weeks_labels = []
    storage_trend_data = []
    downloads_trend_data = []
    screenshots_trend_data = []
    music_trend_data = []

    for i, week_data in enumerate(reversed(historical[:8])):
        week_start = week_data.get("week_start", "")
        weeks_labels.append(week_start)
        storage_trend_data.append(week_data.get("storage", {}).get("disk_usage", {}).get("percent_used", 0))
        downloads_trend_data.append(week_data.get("downloads", {}).get("downloads", {}).get("total_files", 0))
        screenshots_trend_data.append(week_data.get("screenshots", {}).get("stats", {}).get("total_count", 0))
        music_trend_data.append(week_data.get("music", {}).get("stats", {}).get("sessions_this_week", 0))

    # Add current week
    weeks_labels.append(data.get("week_start", "Cette semaine"))
    storage_trend_data.append(data.get("storage", {}).get("disk_usage", {}).get("percent_used", 0))
    downloads_trend_data.append(downloads.get("total_files", 0))
    screenshots_trend_data.append(data.get("screenshots", {}).get("stats", {}).get("total_count", 0))
    music_trend_data.append(data.get("music", {}).get("stats", {}).get("sessions_this_week", 0))

    return {
        "storage_categories": json.dumps(storage_categories),
        "large_items": json.dumps(large_items),
        "file_types": json.dumps(file_types),
        "weeks_labels": json.dumps(weeks_labels),
        "storage_trend": json.dumps(storage_trend_data),
        "downloads_trend": json.dumps(downloads_trend_data),
        "screenshots_trend": json.dumps(screenshots_trend_data),
        "music_trend": json.dumps(music_trend_data),
    }


def generate_html(data: Dict) -> str:
    """Generate the complete HTML dashboard with Liquid Glass design."""
    week_start = data.get("week_start", "")
    health_score = data.get("health_score", 0)
    insights = data.get("insights", [])
    trends = data.get("trends", {})

    # Extract data
    disk_usage = data.get("storage", {}).get("disk_usage", {})
    categories = data.get("storage", {}).get("categories", {})
    large_items = data.get("storage", {}).get("large_items", [])
    downloads = data.get("downloads", {}).get("downloads", {})
    apps = data.get("apps", {})
    notes = data.get("notes", {}).get("notes", {})
    screenshots = data.get("screenshots", {}).get("stats", {})
    music = data.get("music", {}).get("stats", {})

    # Chart data
    charts = prepare_chart_data(data)

    # Health color
    if health_score >= 80:
        health_color = "#34C759"
    elif health_score >= 60:
        health_color = "#FF9500"
    else:
        health_color = "#FF3B30"

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Semaine du {week_start}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            /* Liquid Glass Colors - Light Mode */
            --glass-bg: rgba(255, 255, 255, 0.72);
            --glass-bg-secondary: rgba(245, 245, 247, 0.85);
            --glass-border: rgba(0, 0, 0, 0.08);
            --text-primary: #1d1d1f;
            --text-secondary: #86868b;
            --bg-primary: #f5f5f7;
            --accent-green: #34C759;
            --accent-orange: #FF9500;
            --accent-red: #FF3B30;
            --accent-blue: #007AFF;
            --accent-purple: #5856D6;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
            --shadow-inset: inset 0 1px 0 rgba(255,255,255,0.8);
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                /* Liquid Glass Colors - Dark Mode */
                --glass-bg: rgba(28, 28, 30, 0.72);
                --glass-bg-secondary: rgba(44, 44, 46, 0.85);
                --glass-border: rgba(255, 255, 255, 0.12);
                --text-primary: #f5f5f7;
                --text-secondary: #98989d;
                --bg-primary: #000000;
                --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
                --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
                --shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
                --shadow-inset: inset 0 1px 0 rgba(255,255,255,0.1);
            }}
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 0;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }}

        /* Ambient reflection background */
        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(
                circle at 50% 0%,
                rgba(0, 122, 255, 0.03) 0%,
                transparent 40%
            );
            pointer-events: none;
            z-index: -1;
            animation: ambientPulse 8s ease-in-out infinite;
        }}

        @media (prefers-color-scheme: dark) {{
            body::before {{
                background: radial-gradient(
                    circle at 50% 0%,
                    rgba(0, 122, 255, 0.05) 0%,
                    transparent 40%
                );
            }}
        }}

        @keyframes ambientPulse {{
            0%, 100% {{
                opacity: 0.5;
                transform: scale(1);
            }}
            50% {{
                opacity: 0.8;
                transform: scale(1.05);
            }}
        }}

        /* Liquid Glass Effect */
        .glass {{
            background: var(--glass-bg);
            backdrop-filter: blur(40px) saturate(180%);
            -webkit-backdrop-filter: blur(40px) saturate(180%);
            border: 1px solid var(--glass-border);
            box-shadow: var(--shadow-md), var(--shadow-inset);
            position: relative;
            overflow: hidden;
            transform-style: preserve-3d;
        }}

        /* Reflection Layer - subtle glossy effect */
        .glass::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 50%;
            background: linear-gradient(
                180deg,
                rgba(255, 255, 255, 0.15) 0%,
                rgba(255, 255, 255, 0.05) 50%,
                transparent 100%
            );
            pointer-events: none;
            opacity: 0.6;
            transition: opacity 0.3s ease;
        }}

        @media (prefers-color-scheme: dark) {{
            .glass::before {{
                background: linear-gradient(
                    180deg,
                    rgba(255, 255, 255, 0.08) 0%,
                    rgba(255, 255, 255, 0.02) 50%,
                    transparent 100%
                );
            }}
        }}

        /* Dynamic light reflection that follows mouse */
        .glass::after {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(
                circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
                rgba(255, 255, 255, 0.15) 0%,
                rgba(255, 255, 255, 0.05) 25%,
                transparent 50%
            );
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.4s ease;
        }}

        @media (prefers-color-scheme: dark) {{
            .glass::after {{
                background: radial-gradient(
                    circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
                    rgba(255, 255, 255, 0.12) 0%,
                    rgba(255, 255, 255, 0.04) 25%,
                    transparent 50%
                );
            }}
        }}

        .glass:hover::after {{
            opacity: 1;
        }}

        .glass-secondary {{
            background: var(--glass-bg-secondary);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
        }}

        /* Transparent Menu Bar */
        .menu-bar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 48px;
            background: var(--glass-bg);
            backdrop-filter: blur(60px) saturate(180%);
            -webkit-backdrop-filter: blur(60px) saturate(180%);
            border-bottom: 1px solid var(--glass-border);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 20px;
            box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1) inset,
                        0 4px 12px rgba(0, 0, 0, 0.05);
        }}

        .menu-bar::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 100%;
            background: linear-gradient(
                180deg,
                rgba(255, 255, 255, 0.08) 0%,
                transparent 100%
            );
            pointer-events: none;
        }}

        @media (prefers-color-scheme: dark) {{
            .menu-bar::after {{
                background: linear-gradient(
                    180deg,
                    rgba(255, 255, 255, 0.05) 0%,
                    transparent 100%
                );
            }}
        }}

        .menu-bar h1 {{
            font-size: 1.1em;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .auto-refresh-indicator {{
            margin-left: auto;
            font-size: 0.85em;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .refresh-dot {{
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 68px 20px 40px;
            perspective: 2000px;
            perspective-origin: center top;
        }}

        /* Header Section */
        .header {{
            margin-bottom: 24px;
            text-align: center;
            animation: fadeInDown 0.6s ease-out;
        }}

        .header h2 {{
            font-size: 3em;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--text-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            position: relative;
            text-shadow: 0 4px 12px rgba(0, 122, 255, 0.1);
        }}

        .header h2::after {{
            content: attr(data-text);
            position: absolute;
            left: 0;
            top: 0;
            background: linear-gradient(135deg, rgba(0, 122, 255, 0.2) 0%, transparent 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            opacity: 0.3;
            filter: blur(20px);
        }}

        .header .week-date {{
            color: var(--text-secondary);
            font-size: 1.1em;
            font-weight: 600;
        }}

        /* Health Score */
        .health-score-container {{
            text-align: center;
            margin: 32px 0;
            animation: fadeInUp 0.6s ease-out 0.1s both;
        }}

        .health-score {{
            display: inline-block;
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: conic-gradient({health_color} {health_score * 3.6}deg, var(--glass-bg-secondary) 0deg);
            position: relative;
            box-shadow: var(--shadow-lg),
                        0 0 40px {health_color}40;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1),
                        box-shadow 0.4s ease;
        }}

        .health-score::before {{
            content: '';
            position: absolute;
            top: -5%;
            left: -5%;
            width: 110%;
            height: 110%;
            border-radius: 50%;
            background: radial-gradient(
                circle at 30% 30%,
                rgba(255, 255, 255, 0.4) 0%,
                transparent 50%
            );
            pointer-events: none;
            opacity: 0.3;
        }}

        .health-score:hover {{
            transform: scale(1.05) translateY(-4px);
            box-shadow: var(--shadow-lg),
                        0 0 60px {health_color}60,
                        0 20px 40px rgba(0, 0, 0, 0.2);
        }}

        .health-score-inner {{
            position: absolute;
            width: 116px;
            height: 116px;
            background: var(--glass-bg);
            backdrop-filter: blur(40px);
            -webkit-backdrop-filter: blur(40px);
            border-radius: 50%;
            top: 12px;
            left: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            font-weight: 800;
            color: {health_color};
            box-shadow: var(--shadow-inset);
        }}

        .health-label {{
            margin-top: 16px;
            color: var(--text-secondary);
            font-size: 0.95em;
            font-weight: 600;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            padding: 20px;
            border-radius: 16px;
            animation: fadeInUp 0.6s ease-out calc(0.1s * var(--i)) both;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}

        .stat-card:hover {{
            transform: translateY(-4px) scale(1.02);
            box-shadow: var(--shadow-lg), var(--shadow-inset),
                        0 0 40px rgba(0, 122, 255, 0.1);
        }}

        .stat-card .icon {{
            font-size: 2.2em;
            margin-bottom: 12px;
            display: block;
        }}

        .stat-card .label {{
            color: var(--text-secondary);
            font-size: 0.85em;
            margin-bottom: 6px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .stat-card .value {{
            font-size: 2.2em;
            font-weight: 800;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .trend-indicator {{
            font-size: 0.6em;
            opacity: 0.7;
        }}

        /* Sections */
        .section {{
            padding: 32px;
            border-radius: 24px;
            margin-bottom: 24px;
            animation: fadeInUp 0.6s ease-out calc(0.2s + 0.05s * var(--i)) both;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1),
                        box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            will-change: transform;
        }}

        .section:hover {{
            transform: translateZ(20px) scale(1.005);
            box-shadow: var(--shadow-lg), var(--shadow-inset),
                        0 20px 60px rgba(0, 0, 0, 0.15);
        }}

        .section h2 {{
            font-size: 1.6em;
            margin-bottom: 24px;
            font-weight: 700;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section-icon {{
            font-size: 1.2em;
        }}

        /* Charts */
        .chart-container {{
            position: relative;
            height: 320px;
            margin: 24px 0;
        }}

        .chart-container-small {{
            position: relative;
            height: 250px;
            margin: 24px 0;
        }}

        /* Insights Grid */
        .insights-grid {{
            display: grid;
            gap: 16px;
            margin-bottom: 24px;
        }}

        .insight-card {{
            background: var(--glass-bg-secondary);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 20px;
            display: flex;
            align-items: flex-start;
            gap: 16px;
            border-left: 4px solid transparent;
            animation: fadeInLeft 0.6s ease-out calc(0.1s * var(--i)) both;
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1),
                        box-shadow 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
            overflow: hidden;
        }}

        /* Edge highlight effect */
        .insight-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 16px;
            padding: 1px;
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.3) 0%,
                transparent 50%,
                rgba(255, 255, 255, 0.1) 100%
            );
            -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
            -webkit-mask-composite: xor;
            mask-composite: exclude;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        @media (prefers-color-scheme: dark) {{
            .insight-card::before {{
                background: linear-gradient(
                    135deg,
                    rgba(255, 255, 255, 0.2) 0%,
                    transparent 50%,
                    rgba(255, 255, 255, 0.05) 100%
                );
            }}
        }}

        .insight-card:hover::before {{
            opacity: 1;
        }}

        .insight-card:hover {{
            transform: translateY(-3px) translateZ(10px);
            box-shadow: var(--shadow-lg),
                        0 0 30px rgba(0, 122, 255, 0.08);
        }}

        .insight-card.warning {{
            border-left-color: var(--accent-red);
        }}

        .insight-card.info {{
            border-left-color: var(--accent-blue);
        }}

        .insight-card.action {{
            border-left-color: var(--accent-orange);
        }}

        .insight-card .icon {{
            font-size: 2em;
            flex-shrink: 0;
        }}

        .insight-card .content {{
            flex: 1;
        }}

        .insight-card .title {{
            font-weight: 700;
            margin-bottom: 6px;
            font-size: 1.05em;
        }}

        .insight-card .message {{
            color: var(--text-secondary);
            font-size: 0.95em;
            line-height: 1.5;
        }}

        /* Large Items List */
        .large-items-list {{
            list-style: none;
        }}

        .large-items-list li {{
            background: var(--glass-bg-secondary);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1),
                        box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 1px solid transparent;
        }}

        .large-items-list li::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255, 255, 255, 0.1) 50%,
                transparent 100%
            );
            transition: left 0.5s ease;
        }}

        .large-items-list li:hover {{
            transform: translateX(6px) translateZ(5px);
            box-shadow: var(--shadow-md),
                        0 0 20px rgba(0, 122, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.1);
        }}

        .large-items-list li:hover::before {{
            left: 100%;
        }}

        .large-items-list .item-name {{
            font-weight: 600;
        }}

        .large-items-list .item-size {{
            color: var(--accent-orange);
            font-weight: 700;
            font-size: 1.1em;
        }}

        /* Grid Layouts */
        .two-col-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 24px;
            margin-bottom: 24px;
        }}

        /* Notifications */
        .notification {{
            position: fixed;
            top: 68px;
            right: 20px;
            max-width: 400px;
            padding: 20px 24px;
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            z-index: 999;
            animation: slideInRight 0.4s ease-out;
            border-left: 4px solid var(--accent-red);
        }}

        @keyframes slideInRight {{
            from {{
                transform: translateX(400px);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}

        .notification-title {{
            font-weight: 700;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .notification-message {{
            color: var(--text-secondary);
            font-size: 0.95em;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            color: var(--text-secondary);
            padding: 32px 20px;
            font-size: 0.9em;
            font-weight: 500;
        }}

        /* Animations */
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header h2 {{
                font-size: 2em;
            }}

            .stats-grid {{
                grid-template-columns: 1fr 1fr;
            }}

            .two-col-grid {{
                grid-template-columns: 1fr;
            }}

            .section {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Transparent Menu Bar -->
    <div class="menu-bar glass">
        <h1>📊 Usage Dashboard</h1>
        <div class="auto-refresh-indicator">
            <span class="refresh-dot"></span>
            <span>Auto-refresh: 5min</span>
        </div>
    </div>

    <div class="container">
        <!-- Header -->
        <div class="header">
            <h2>Ta semaine</h2>
            <div class="week-date">Semaine du {week_start}</div>
        </div>

        <!-- Health Score -->
        <div class="health-score-container">
            <div class="health-score">
                <div class="health-score-inner">{health_score}</div>
            </div>
            <div class="health-label">Score de santé système</div>
        </div>

        <!-- Quick Stats -->
        <div class="stats-grid">
            <div class="stat-card glass" style="--i: 1">
                <span class="icon">💾</span>
                <div class="label">Espace libre</div>
                <div class="value">{disk_usage.get('free_gb', 0)} GB <span class="trend-indicator">{trends.get('storage_trend', '')}</span></div>
            </div>
            <div class="stat-card glass" style="--i: 2">
                <span class="icon">📥</span>
                <div class="label">Téléchargements</div>
                <div class="value">{downloads.get('total_files', 0)} <span class="trend-indicator">{trends.get('downloads_trend', '')}</span></div>
            </div>
            <div class="stat-card glass" style="--i: 3">
                <span class="icon">💻</span>
                <div class="label">Apps actives</div>
                <div class="value">{apps.get('running_count', 0)}</div>
            </div>
            <div class="stat-card glass" style="--i: 4">
                <span class="icon">📸</span>
                <div class="label">Screenshots</div>
                <div class="value">{screenshots.get('total_count', 0)} <span class="trend-indicator">{trends.get('screenshots_trend', '')}</span></div>
            </div>
            <div class="stat-card glass" style="--i: 5">
                <span class="icon">📝</span>
                <div class="label">Notes</div>
                <div class="value">{notes.get('total_notes', 0)}</div>
            </div>
            <div class="stat-card glass" style="--i: 6">
                <span class="icon">🎵</span>
                <div class="label">Sessions musique</div>
                <div class="value">{music.get('sessions_this_week', 0)} <span class="trend-indicator">{trends.get('music_trend', '')}</span></div>
            </div>
        </div>

        <!-- Insights -->
        <div class="section glass" style="--i: 1">
            <h2><span class="section-icon">💡</span> Insights & Recommandations</h2>
            <div class="insights-grid">
"""

    # Add insights
    for i, insight in enumerate(insights):
        html += f"""
                <div class="insight-card {insight.get('type', 'info')}" style="--i: {i + 1}">
                    <span class="icon">{insight.get('icon', '💡')}</span>
                    <div class="content">
                        <div class="title">{insight.get('title', '')}</div>
                        <div class="message">{insight.get('message', '')}</div>
                    </div>
                </div>
"""

    html += """
            </div>
        </div>

        <!-- Two Column Grid -->
        <div class="two-col-grid">
            <!-- Storage -->
            <div class="section glass" style="--i: 2">
                <h2><span class="section-icon">💾</span> Stockage</h2>
                <div class="chart-container-small">
                    <canvas id="storageChart"></canvas>
                </div>
            </div>

            <!-- Downloads -->
            <div class="section glass" style="--i: 3">
                <h2><span class="section-icon">📥</span> Types de fichiers</h2>
                <div class="chart-container-small">
                    <canvas id="downloadsChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Large Files -->
        <div class="section glass" style="--i: 4">
            <h2><span class="section-icon">📦</span> Top 5 Space Eaters</h2>
            <ul class="large-items-list" id="largeItemsList"></ul>
        </div>

        <!-- Historical Trends -->
        <div class="section glass" style="--i: 5">
            <h2><span class="section-icon">📈</span> Évolution historique (8 semaines)</h2>
            <div class="chart-container">
                <canvas id="trendsChart"></canvas>
            </div>
        </div>

        <div class="footer">
            Dashboard généré le """ + datetime.now().strftime("%d/%m/%Y à %H:%M") + """ • Auto-refresh activé
        </div>
    </div>

    <script>
        // Chart.js default config
        Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif";
        Chart.defaults.font.weight = 600;
        Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary');

        // Apple-style Mouse Reflection System
        const glassElements = document.querySelectorAll('.glass, .stat-card, .section, .insight-card');

        glassElements.forEach(element => {{
            element.addEventListener('mousemove', (e) => {{
                const rect = element.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;

                // Update CSS variables for dynamic reflection
                element.style.setProperty('--mouse-x', `${{x}}%`);
                element.style.setProperty('--mouse-y', `${{y}}%`);

                // Subtle 3D tilt effect (Apple-style parallax)
                const tiltX = ((e.clientY - rect.top) / rect.height - 0.5) * 3;
                const tiltY = ((e.clientX - rect.left) / rect.width - 0.5) * -3;

                element.style.transform = `perspective(1000px) rotateX(${{tiltX}}deg) rotateY(${{tiltY}}deg) scale(1.005)`;
            }});

            element.addEventListener('mouseleave', () => {{
                element.style.transform = '';
                element.style.setProperty('--mouse-x', '50%');
                element.style.setProperty('--mouse-y', '50%');
            }});
        }});

        // Global spotlight effect that follows cursor
        const createSpotlight = () => {{
            const spotlight = document.createElement('div');
            spotlight.style.cssText = `
                position: fixed;
                width: 600px;
                height: 600px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(0, 122, 255, 0.03) 0%, transparent 70%);
                pointer-events: none;
                z-index: 9999;
                mix-blend-mode: screen;
                transition: opacity 0.3s ease;
                opacity: 0;
            `;
            document.body.appendChild(spotlight);

            document.addEventListener('mousemove', (e) => {{
                spotlight.style.left = `${{e.clientX - 300}}px`;
                spotlight.style.top = `${{e.clientY - 300}}px`;
                spotlight.style.opacity = '1';
            }});

            document.addEventListener('mouseleave', () => {{
                spotlight.style.opacity = '0';
            }});
        }};

        createSpotlight();

        // Parallax scroll effect for sections
        const parallaxElements = document.querySelectorAll('.section, .stat-card');
        let ticking = false;

        const updateParallax = () => {{
            const scrollY = window.scrollY;

            parallaxElements.forEach((element, index) => {{
                const rect = element.getBoundingClientRect();
                const elementTop = rect.top + scrollY;
                const elementHeight = rect.height;
                const windowHeight = window.innerHeight;

                // Calculate if element is in viewport
                if (rect.top < windowHeight && rect.bottom > 0) {{
                    // Calculate parallax offset (subtle)
                    const scrollProgress = (scrollY - elementTop + windowHeight) / (windowHeight + elementHeight);
                    const parallaxOffset = (scrollProgress - 0.5) * 20; // Max 20px movement

                    // Apply subtle parallax transform
                    const currentTransform = element.style.transform;
                    if (!currentTransform.includes('rotateX') && !currentTransform.includes('rotateY')) {{
                        element.style.transform = `translateY(${{parallaxOffset * -1}}px)`;
                    }}
                }}
            }});

            ticking = false;
        }};

        const onScroll = () => {{
            if (!ticking) {{
                window.requestAnimationFrame(updateParallax);
                ticking = true;
            }}
        }};

        window.addEventListener('scroll', onScroll, {{ passive: true }});
        updateParallax(); // Initial call

        // Add shimmer effect to stat cards on load
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach((card, index) => {{
            setTimeout(() => {{
                card.style.animation = `fadeInUp 0.6s ease-out, shimmer 2s ease-in-out ${{index * 0.2}}s`;
            }}, 100);
        }});

        // Add CSS for shimmer animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes shimmer {{
                0% {{
                    box-shadow: var(--shadow-md), var(--shadow-inset);
                }}
                50% {{
                    box-shadow: var(--shadow-lg), var(--shadow-inset),
                                0 0 30px rgba(0, 122, 255, 0.15);
                }}
                100% {{
                    box-shadow: var(--shadow-md), var(--shadow-inset);
                }}
            }}
        `;
        document.head.appendChild(style);

        // Storage Donut Chart
        const storageData = """ + charts["storage_categories"] + """;
        const storageCtx = document.getElementById('storageChart').getContext('2d');
        new Chart(storageCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(storageData),
                datasets: [{
                    data: Object.values(storageData),
                    backgroundColor: [
                        '#007AFF', '#34C759', '#FF9500', '#FF3B30',
                        '#5856D6', '#FF2D55', '#64D2FF', '#BF5AF2'
                    ],
                    borderWidth: 0,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 16,
                            font: { size: 13, weight: 600 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8,
                        titleFont: { size: 14, weight: 700 },
                        bodyFont: { size: 13 },
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + ' GB';
                            }
                        }
                    }
                }
            }
        });

        // Downloads File Types Chart
        const fileTypes = """ + charts["file_types"] + """;
        const downloadsCtx = document.getElementById('downloadsChart').getContext('2d');
        new Chart(downloadsCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(fileTypes),
                datasets: [{
                    label: 'Fichiers',
                    data: Object.values(fileTypes),
                    backgroundColor: '#007AFF',
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(128, 128, 128, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });

        // Historical Trends Chart
        const weeksLabels = """ + charts["weeks_labels"] + """;
        const storageTrend = """ + charts["storage_trend"] + """;
        const downloadsTrend = """ + charts["downloads_trend"] + """;
        const screenshotsTrend = """ + charts["screenshots_trend"] + """;
        const musicTrend = """ + charts["music_trend"] + """;

        const trendsCtx = document.getElementById('trendsChart').getContext('2d');
        new Chart(trendsCtx, {
            type: 'line',
            data: {
                labels: weeksLabels,
                datasets: [
                    {
                        label: 'Stockage (%)',
                        data: storageTrend,
                        borderColor: '#FF9500',
                        backgroundColor: 'rgba(255, 149, 0, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Téléchargements',
                        data: downloadsTrend,
                        borderColor: '#007AFF',
                        backgroundColor: 'rgba(0, 122, 255, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Screenshots',
                        data: screenshotsTrend,
                        borderColor: '#FF2D55',
                        backgroundColor: 'rgba(255, 45, 85, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Sessions musique',
                        data: musicTrend,
                        borderColor: '#5856D6',
                        backgroundColor: 'rgba(88, 86, 214, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 16,
                            font: { size: 13, weight: 600 },
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 16,
                        cornerRadius: 8,
                        titleFont: { size: 14, weight: 700 },
                        bodyFont: { size: 13 }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Stockage (%)',
                            font: { size: 12, weight: 700 }
                        },
                        grid: {
                            color: 'rgba(128, 128, 128, 0.1)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Autres métriques',
                            font: { size: 12, weight: 700 }
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });

        // Large Items List
        const largeItems = """ + charts["large_items"] + """;
        const largeItemsList = document.getElementById('largeItemsList');
        largeItems.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div>
                    <span class="item-name">${item.name}</span>
                    <br>
                    <small style="color: var(--text-secondary);">${item.type}</small>
                </div>
                <span class="item-size">${item.size_gb} GB</span>
            `;
            largeItemsList.appendChild(li);
        });

        // Auto-refresh every 5 minutes
        setTimeout(() => {
            console.log('Auto-refreshing dashboard...');
            window.location.reload();
        }, 5 * 60 * 1000);

        // Show critical notifications
        const criticalInsights = """ + json.dumps([i for i in insights if i.get("type") == "warning"]) + """;
        if (criticalInsights.length > 0) {
            setTimeout(() => {
                const notification = document.createElement('div');
                notification.className = 'notification glass';
                notification.innerHTML = `
                    <div class="notification-title">
                        ${criticalInsights[0].icon} ${criticalInsights[0].title}
                    </div>
                    <div class="notification-message">
                        ${criticalInsights[0].message}
                    </div>
                `;
                document.body.appendChild(notification);

                setTimeout(() => {
                    notification.style.animation = 'slideInRight 0.4s ease-out reverse';
                    setTimeout(() => notification.remove(), 400);
                }, 8000);
            }, 1000);
        }
    </script>
</body>
</html>"""

    return html


def create_dashboard(data: Dict) -> Path:
    """Create the HTML dashboard file."""
    print("🎨 Génération du dashboard HTML avec Liquid Glass...")

    html = generate_html(data)

    # Save to output directory
    output_file = OUTPUT_DIR / "dashboard.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Dashboard créé: {output_file}")
    return output_file


if __name__ == "__main__":
    # For testing
    test_data = {
        "week_start": "2025-10-13",
        "health_score": 85,
        "storage": {
            "disk_usage": {
                "total_gb": 500,
                "used_gb": 350,
                "free_gb": 150,
                "percent_used": 70
            },
            "categories": {
                "Documents": 45.2,
                "Images": 78.5,
                "Vidéos": 120.3,
                "Applications": 55.0
            },
            "large_items": [
                {"name": "Movies", "size_gb": 50.5, "type": "dossier"},
                {"name": "Photos Library", "size_gb": 45.2, "type": "fichier"},
            ]
        },
        "downloads": {
            "downloads": {
                "total_files": 156,
                "total_size_gb": 12.5,
                "files_this_week": 23,
                "unused_count": 45,
                "file_types": {
                    ".pdf": 34,
                    ".zip": 12,
                    ".dmg": 8
                }
            }
        },
        "apps": {
            "running_count": 15
        },
        "notes": {
            "notes": {
                "total_notes": 123,
                "notes_this_week": 5
            }
        },
        "screenshots": {
            "stats": {
                "total_count": 47,
                "on_desktop": 25
            }
        },
        "music": {
            "stats": {
                "sessions_this_week": 12
            }
        },
        "trends": {
            "storage_trend": "↗️",
            "downloads_trend": "→",
            "screenshots_trend": "↘️"
        },
        "historical": [],
        "insights": [
            {
                "icon": "💾",
                "type": "info",
                "title": "Espace disque OK",
                "message": "Il te reste 150 GB d'espace libre"
            }
        ]
    }
    create_dashboard(test_data)
