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
├── docs/          # Documentation et descriptifs
└── src/           # Code source (à compléter par l'équipe)
```

## Équipe

| Membre | Rôle |
|--------|------|
| — | — |

## Ressources

- Descriptif des données : `docs/climatologie-donnees-mensuelles-descriptif.pdf`
