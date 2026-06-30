# Hackathon YNOV — Climatologie

Dépôt de travail collaboratif pour le hackathon sur les données climatologiques mensuelles.

## Objectif

Ce projet regroupe le code, les analyses et la documentation produits par l'équipe pendant le hackathon.

## Démarrage rapide

```bash
# Cloner le dépôt
git clone https://github.com/khaldisamir-ynov/ynov-hackathon-climatologie.git
cd ynov-hackathon-climatologie

# Créer une branche pour votre travail
git checkout -b feature/nom-de-votre-feature

# Lancer l'application (via Docker)

 cd ynov-hackathon-climatologie
 docker compose up --build -d
 docker compose logs import-data -f (cela peut prendre quelques minutes)

Pour voir la progression du chargement des données (3M-environ) ouvrir un nouveau terminal et faire :
 docker compose exec db psql -U clima -d climafrance -c "SELECT COUNT(*) FROM historic_weather;"

```

## Organisation du travail

1. **Toujours travailler sur une branche** — ne pas pousser directement sur `main`
2. **Créer une Pull Request** pour fusionner votre travail
3. **Communiquer** dans les issues GitHub pour répartir les tâches

## Structure du projet

```
.
├── README.md
├── docs/                          # Documentation et descriptifs PDF
├── Data/                          # Données climatologiques CSV (1950-2026, 95 départements)
├── predictions_data/              # Données de prédictions CSV
├── app/                           # Application Streamlit (ClimaFrance)
│   ├── app.py                     # Page d'accueil
│   ├── data_loader.py             # Chargement des données depuis PostgreSQL
│   ├── style.py                   # Styles CSS
│   └── pages/
│       ├── 1_🗺️_Carte.py         # Carte interactive des températures
│       ├── 2_📊_Tableau.py        # Tableau des moyennes par station
│       ├── 3_📈_Graphiques.py     # Évolution temporelle
│       └── 4_🔮_Predictions.py    # Prévisions 2026-2027
├── notebooks/                     # Notebooks d'analyse et modélisation
│   ├── 01_exploration_donnees.ipynb   # Exploration initiale des données
│   ├── 02_lstm_temperature.ipynb      # Modèle LSTM pour les températures
│   ├── 03_build_lstm_dataset.ipynb    # Construction du dataset LSTM
│   └── 04_lstm_multi_output.ipynb     # LSTM multi-sorties (min/max)
├── notebook aurelie/              # Analyses exploratoires (Aurélie)
│   ├── 01_analyse des données.ipynb   # Analyse descriptive des données
│   ├── 02_exploration series temporelles.ipynb  # Séries temporelles
│   └── 03_modele de prediction.ipynb  # Modèle de prédiction
├── EDA.ipynb                      # Analyse exploratoire principale (EDA)
├── src/                           # Scripts et notebooks de modélisation avancée
│   ├── rebuild_climat_source.py   # Reconstruction des sources climatiques
│   ├── data/
│   │   └── process_raw.py         # Traitement des données brutes
│   └── lstm/                      # Notebooks LSTM avancés
│       ├── lstm_data_process*.ipynb   # Pré-traitement des données LSTM
│       ├── lstm_min_max*.ipynb        # Modèles min/max températures
│       └── playground.ipynb           # Expérimentations
└── scripts/
    └── import_data.py             # Import des CSV vers PostgreSQL
```

## Notebooks — Guide

| Notebook | Emplacement | Description |
|---|---|---|
| `EDA.ipynb` | racine | Analyse exploratoire principale des données climatiques |
| `01_exploration_donnees.ipynb` | `notebooks/` | Exploration initiale des données (Samir) |
| `02_lstm_temperature.ipynb` | `notebooks/` | Premier modèle LSTM de prédiction des températures |
| `03_build_lstm_dataset.ipynb` | `notebooks/` | Construction et préparation du dataset pour LSTM |
| `04_lstm_multi_output.ipynb` | `notebooks/` | LSTM avec sorties multiples (Tmin et Tmax) |
| `01_analyse des données.ipynb` | `notebook aurelie/` | Analyse descriptive et statistiques des données (Aurélie) |
| `02_exploration series temporelles.ipynb` | `notebook aurelie/` | Étude des séries temporelles climatiques (Aurélie) |
| `03_modele de prediction.ipynb` | `notebook aurelie/` | Modèle de prédiction (Aurélie) |
| `lstm_data_process*.ipynb` | `src/lstm/` | Pré-traitement avancé pour les modèles LSTM |
| `lstm_min_max*.ipynb` | `src/lstm/` | Modèles LSTM pour prédire Tmin et Tmax |
| `playground.ipynb` | `src/lstm/` | Expérimentations et tests divers |

## Équipe

| Membre | Rôle |
|--------|------|
| — | — |

## Ressources

- Descriptif des données : `docs/climatologie-donnees-mensuelles-descriptif.pdf`
