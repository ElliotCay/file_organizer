# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
**Usage Dashboard** - An interactive HTML dashboard that visualizes weekly Mac usage statistics. The dashboard opens automatically every Monday morning and provides insights on:
- Application usage and time tracking
- Storage analysis and file management
- Downloads and recent files
- Communication patterns
- Notes and productivity metrics
- System health and performance

## Technology Stack
Python for data collection and processing, HTML/CSS/JavaScript for the interactive dashboard frontend. The dashboard should follow macOS design language (Big Sur/Sonoma style) and be responsive for iPhone/iPad viewing.

## Project Structure
```
usage_dashboard/
├── main.py              # Main script - orchestrates everything
├── config.py            # Configuration constants and paths
├── collectors/          # Data collection modules
│   ├── storage.py      # Disk space and file categorization
│   ├── downloads.py    # Downloads folder analysis
│   └── app_usage.py    # Application tracking (running and installed apps)
├── processors/          # Data processing and insights
│   └── aggregator.py   # Aggregate data and generate insights/health score
├── dashboard/           # HTML dashboard generation
│   └── generator.py    # Creates static HTML with embedded Chart.js
├── data/                # Local data storage (gitignored)
│   ├── *.json          # Current week data
│   └── archives/       # Historical weekly archives
└── output/              # Generated dashboards (gitignored)
    └── dashboard.html  # Current dashboard
```

## Key Architecture Principles

### Data Collection
- Each collector module runs independently and outputs standardized JSON
- Collectors should handle missing data gracefully
- Privacy-first: all data stays local, no external APIs
- Incremental updates to avoid re-processing historical data

### Dashboard Generation
- Static HTML generation (no server required after generation)
- Data embedded as JSON for client-side interactivity
- Chart.js or D3.js for visualizations
- Supports both light/dark mode based on system preferences

### Scheduling
- Use macOS `launchd` for Monday morning automation
- Manual trigger script for on-demand dashboard generation
- Weekly archives stored with timestamps

## Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run Dashboard
```bash
# Generate and open the dashboard
python main.py

# Run individual collectors (for testing)
python collectors/storage.py
python collectors/downloads.py
python collectors/app_usage.py

# Generate dashboard from existing data (for testing)
python dashboard/generator.py
```

### Project Development
- All data files are in `data/` and are gitignored (local only)
- Output HTML is in `output/dashboard.html`
- Weekly archives saved to `data/archives/week_YYYY-MM-DD.json`

## macOS-Specific Considerations
- Use `osascript` for accessing Mac system information
- SQLite databases for Messages app access (~/Library/Messages/chat.db)
- File metadata via `mdls` command
- Application usage might require screen time API or accessibility permissions
- Notes app data in ~/Library/Group Containers/group.com.apple.notes/

## Data Sources
- Application usage: Screen Time API or log parsing
- Storage: `du`, `df`, file system metadata
- Downloads: Monitor ~/Downloads with file stats
- Messages: SQLite database queries
- Notes: Core Data or SQLite access
- System performance: `system_profiler`, boot logs

## Dashboard Features (Implemented)

### Current Features
- **Health Score**: 0-100 score based on disk space, unused downloads, and running apps
- **Storage Analysis**: Donut chart showing disk usage by file category (Documents, Images, Videos, etc.)
- **Space Eaters**: Top 5 largest files/folders
- **Downloads Stats**: File counts, sizes, unused files (30+ days), file type breakdown
- **App Tracking**: Running apps count, installed apps, recently installed apps
- **Automated Insights**: Smart recommendations based on system state
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Mode**: Automatic based on system preferences
- **Interactive Charts**: Chart.js visualizations with hover details

### Future Enhancements (Not Yet Implemented)
- Messages/communication tracking (requires SQLite access to Messages.app database)
- Notes analysis (requires access to Notes.app data)
- Real application usage time tracking (requires Screen Time API or accessibility permissions)
- Historical trends and week-over-week comparisons
- Export to PDF functionality

## French Language
Interface text should be in French as per the original specification in `directives.md`.
