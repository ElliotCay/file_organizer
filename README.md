# 📊 Dashboard Hebdomadaire - Usage Mac

Un dashboard HTML interactif qui visualise tes statistiques d'utilisation Mac de la semaine.

## ✨ Fonctionnalités

- **Analyse de stockage** : Visualise l'utilisation de ton disque par catégorie (Documents, Images, Vidéos, etc.)
- **Suivi des téléchargements** : Statistiques sur tes fichiers téléchargés et détection des fichiers inutilisés
- **Applications** : Liste des apps actives et récemment installées
- **Score de santé système** : Score global basé sur l'espace disque, les téléchargements et les apps
- **Insights automatiques** : Recommandations personnalisées pour optimiser ton Mac
- **Design moderne** : Interface style macOS avec mode sombre/clair automatique

## 🚀 Installation

1. **Créer un environnement virtuel** (recommandé) :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

## 📊 Utilisation

### Générer le dashboard

Exécute simplement le script principal :

```bash
python main.py
```

Le script va :
1. Collecter les données (stockage, téléchargements, applications)
2. Agréger et analyser les données
3. Générer un dashboard HTML
4. Ouvrir automatiquement le dashboard dans ton navigateur

### Fichiers générés

- `output/dashboard.html` : Le dashboard HTML actuel
- `data/*.json` : Données collectées (storage, downloads, app_usage)
- `data/archives/week_YYYY-MM-DD.json` : Archives hebdomadaires

## 📁 Structure du projet

```
usage_dashboard/
├── main.py                 # Script principal
├── config.py              # Configuration
├── collectors/            # Modules de collecte de données
│   ├── storage.py        # Analyse du stockage
│   ├── downloads.py      # Analyse des téléchargements
│   └── app_usage.py      # Suivi des applications
├── processors/            # Traitement des données
│   └── aggregator.py     # Agrégation et insights
├── dashboard/             # Génération du dashboard
│   └── generator.py      # Génération HTML
├── data/                  # Données collectées (gitignored)
└── output/                # Dashboard généré (gitignored)
```

## 🎨 Aperçu du Dashboard

Le dashboard inclut :

- **En-tête** : Score de santé global et statistiques clés
- **Insights** : Recommandations automatiques et alertes
- **Stockage** : Graphique en donut de l'utilisation par catégorie
- **Top Space Eaters** : Les 5 fichiers/dossiers les plus volumineux
- **Téléchargements** : Statistiques et répartition par type de fichier
- **Responsive** : Compatible desktop, tablette et mobile

## 🔧 Configuration

Modifie `config.py` pour personnaliser :

- Les seuils d'alerte (espace disque, fichiers inutilisés)
- Les catégories de fichiers
- Les chemins de données
- Les limites (top apps, top contacts, etc.)

## 🔄 Automatisation (optionnel)

Pour générer automatiquement le dashboard chaque lundi matin, utilise `launchd` sur macOS :

1. Crée un fichier `~/Library/LaunchAgents/com.usage.dashboard.plist` :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.usage.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/chemin/vers/venv/bin/python</string>
        <string>/chemin/vers/usage_dashboard/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

2. Charge le service :
```bash
launchctl load ~/Library/LaunchAgents/com.usage.dashboard.plist
```

## 🔒 Confidentialité & Sécurité

- **100% local** : Toutes les données restent sur ton Mac (aucun envoi vers des serveurs externes)
- **Pas de télémétrie** : Aucun tracking, aucune analyse d'usage
- **Code open source** : Tu peux auditer tout le code
- **Données gitignorées** : Les dossiers `data/` et `output/` contenant tes informations personnelles sont automatiquement exclus du repository
- Le suivi réel du temps d'utilisation des apps nécessiterait des permissions d'accessibilité supplémentaires
- Les données de Messages ne sont pas collectées dans cette version (nécessiterait un accès à la base de données SQLite)

## 🐛 Dépannage

**Le dashboard ne s'ouvre pas automatiquement** :
- Ouvre manuellement `output/dashboard.html` dans ton navigateur

**Erreurs de permissions** :
- Certains dossiers système peuvent nécessiter des permissions spéciales
- Le script ignore automatiquement les fichiers inaccessibles

**Données manquantes** :
- Vérifie que les chemins dans `config.py` correspondent à ton système
- Certaines fonctionnalités peuvent nécessiter des permissions supplémentaires

## 📄 Licence

Projet personnel - Usage libre
