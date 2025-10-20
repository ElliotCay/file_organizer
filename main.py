#!/usr/bin/env python3
"""Main script to generate the usage dashboard."""
import sys
import subprocess
from datetime import datetime

# Import collectors
from collectors.storage import collect_storage_data
from collectors.downloads import collect_downloads_data
from collectors.app_usage import collect_app_usage_data
from collectors.notes import collect_notes_data
from collectors.screenshots import collect_screenshots_data
from collectors.music import collect_music_data

# Import processors
from processors.aggregator import aggregate_all_data, save_weekly_archive

# Import dashboard generator
from dashboard.generator import create_dashboard


def print_banner():
    """Print a nice banner."""
    print("\n" + "="*60)
    print("  📊  DASHBOARD HEBDOMADAIRE - USAGE MAC")
    print("="*60 + "\n")


def open_dashboard(file_path):
    """Open the dashboard in the default browser."""
    try:
        subprocess.run(["open", str(file_path)], check=True)
        print(f"\n🌐 Dashboard ouvert dans ton navigateur!")
    except subprocess.CalledProcessError:
        print(f"\n⚠️  Impossible d'ouvrir automatiquement le dashboard.")
        print(f"Ouvre manuellement: {file_path}")


def main():
    """Main execution function."""
    print_banner()

    try:
        # Step 1: Collect data from all sources
        print("📊 ÉTAPE 1/4: Collection des données\n")
        storage_data = collect_storage_data()
        downloads_data = collect_downloads_data()
        app_data = collect_app_usage_data()
        notes_data = collect_notes_data()
        screenshots_data = collect_screenshots_data()
        music_data = collect_music_data()

        # Step 2: Aggregate all data
        print("\n📊 ÉTAPE 2/4: Agrégation des données\n")
        aggregated_data = aggregate_all_data()

        # Step 3: Save weekly archive
        print("\n📊 ÉTAPE 3/4: Sauvegarde de l'archive\n")
        save_weekly_archive(aggregated_data)

        # Step 4: Generate HTML dashboard
        print("\n📊 ÉTAPE 4/4: Génération du dashboard\n")
        dashboard_file = create_dashboard(aggregated_data)

        # Success summary
        print("\n" + "="*60)
        print("  ✅  DASHBOARD GÉNÉRÉ AVEC SUCCÈS!")
        print("="*60)
        print(f"\n📊 Score de santé: {aggregated_data['health_score']}/100")
        print(f"📁 Fichier: {dashboard_file}")
        print(f"⏰ Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n")

        # Open in browser
        open_dashboard(dashboard_file)

    except KeyboardInterrupt:
        print("\n\n⚠️  Génération annulée par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur lors de la génération du dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
