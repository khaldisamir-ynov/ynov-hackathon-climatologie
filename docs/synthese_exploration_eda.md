# WeatherForYnov — Synthèse de l'exploration des données

> Document de travail pour validation en équipe — Hackathon YNOV, Sujet 2  
> Basé sur le notebook `notebooks/01_exploration_donnees.ipynb` et l'export `src/data/processed/climat_source.csv`  
> *Dernière mise à jour : juin 2026*

---

## 1. Contexte et périmètre

Nous avons consolidé les données climatiques mensuelles **Météo-France (MENSQ)** pour la France métropolitaine. L'objectif est de **prédire la température moyenne mensuelle** et de l'afficher dans une plateforme interactive (Streamlit) : carte par borne, tableaux et graphiques filtrables par région / département / station.

### Données brutes chargées (exploration)

| Élément | Valeur |
|---------|--------|
| Fichiers MENSQ | **189** (2 par département : historique + récent) |
| Période brute | **1950 – 2026** |
| Observations station × mois | **3 262 696** |
| Stations météo (brut) | **9 405** |
| Départements couverts | **95** (métropole + Corse, **dont le 79**) |

### Livrable EDA — fichier source unique

Après filtrage qualité **Q = 1**, enrichissement géographique et filtres finaux, un **seul fichier** est produit pour le feature engineering, la modélisation et l'application :

**`src/data/processed/climat_source.csv`**

| Élément | Valeur |
|---------|--------|
| Granularité | **station (NUM_POSTE) × mois** |
| Période | **2001 – 2025** (filtre `annee > 2000`) |
| Stations (bornes) | **2 336** |
| Départements | **95** |
| Régions | **13** |
| Observations finales | **334 500** |
| Couples station × année complets | **27 875** (12 mois avec TMM renseignée chaque mois) |
| Colonnes | **24** |

**Colonnes principales :**
`NUM_POSTE`, `nom_station`, `lat`, `lon`, `alti`, `code_departement`, `nom_departement`, `code_region`, `nom_region`, `annee`, `mois`, `date`, + 12 variables météo.

**Filtres appliqués :**
- Code qualité Météo-France **Q = 1** uniquement (valeurs certifiées)
- **Pas d'agrégation départementale** : chaque ligne conserve son identifiant **NUM_POSTE**
- Fusion du référentiel `referentiel_geo_departements.csv` (régions)
- **Après 2000** : `annee > 2000`
- **Séries complètes** : 12 mois par **NUM_POSTE** et par année, avec `temp_moy_mensuelle` non nulle sur chaque mois

---

## 2. Principaux constats de l'analyse exploratoire

*Statistiques ci-dessous calculées sur `climat_source.csv` (2001–2025, niveau station).*

### 2.1 Température — vue d'ensemble

- Température moyenne mensuelle (toutes stations) : **11,6 °C** (écart-type **6,4 °C**)
- Saisonnalité marquée :
  - Hiver : **4,6 °C**
  - Printemps : **10,6 °C**
  - Été : **19,2 °C**
  - Automne : **12,1 °C**

### 2.2 Tendance climatique (changement climatique)

- Tendance linéaire observée au niveau station : **−0,012 °C / an** sur 2001–2025 (signal plus hétérogène qu'en agrégation départementale)
- Moyenne annuelle (moyenne des stations par an) :
  - **2001** : **11,7 °C**
  - **2010–2019** : **11,3 °C**
- **Interprétation** : la tendance globale est plus lisible en agrégant par département ou par année pour le data storytelling. La variable `trend_index` reste pertinente comme feature ML.

> **Note** : l'historique brut remonte à 1950, mais le livrable est restreint à **post-2000** pour garantir la qualité et la complétude des séries.

### 2.3 Disparités territoriales

**Régions les plus chaudes** (moyenne des stations, 2001–2025) :
- Corse (~14,9 °C)
- Provence-Alpes-Côte d'Azur (~12,6 °C)
- Nouvelle-Aquitaine (~12,6 °C)

**Départements les plus chauds** :
- Corse-du-Sud (~14,9 °C)
- Bouches-du-Rhône (~14,8 °C)
- Var (~14,7 °C)

**Départements les plus froids** :
- Savoie (~7,5 °C)
- Hautes-Alpes (~7,7 °C)
- Haute-Savoie (~8,7 °C)

→ Fort contraste **littoral méditerranéen / massifs montagneux** ; l'altitude (`alti`) et la latitude sont des features géographiques pertinentes au niveau station.

### 2.4 Précipitations

- Moyenne : **~75 mm / mois**
- Corrélation faible avec la température (**r ≈ −0,17**)

### 2.5 Matrice de corrélation — enseignements clés

| Variable | Corrélation avec `temp_moy_mensuelle` | Implication |
|----------|---------------------------------------|-------------|
| `temp_max` | **+0,98** | Très redondant avec la cible → risque de fuite d'information |
| `temp_min` | **+0,98** | Idem |
| `insolation` | **+0,78** | Feature pertinente (mais ~89 % de manquants au niveau station) |
| `humidite` | **−0,57** | Feature pertinente (relation inverse, ~80 % de manquants) |
| `vent_moyen` | **−0,13** | Signal faible |
| `precipitations_mm` | **−0,17** | Signal faible seul |

**Point d'attention ML** : inclure `temp_max` et `temp_min` du **même mois** revient presque à « tricher ». Utiliser des **lags** (mois précédents) ou exclure ces variables du mois courant.

### 2.6 Qualité et complétude des données

| Variable | Taux de manquants (niveau station) |
|----------|--------------------------------------|
| `temp_moy_mensuelle` | **0 %** |
| `temp_moy_jour` | **0,1 %** |
| `evapotranspiration` | **0,2 %** |
| `precipitations_mm` | **2,1 %** |
| `vent_moyen` | **48,4 %** |
| `rafale_max` | **49,1 %** |
| `humidite` | **79,8 %** |
| `rayonnement_global` | **87,8 %** |
| `insolation` | **89,0 %** |
| `pression_mer` | **94,9 %** |

**Points de vigilance :**
- Certaines stations n'ont qu'**1 année complète** après filtrage (ex. 12 obs seulement) → séries trop courtes pour le ML
- Médiane train par station : **~132 observations** (≈ 11 ans) — largement suffisant pour un modèle global
- Données **2025** : incluses si la série annuelle de la station est complète
- Département **79 (Deux-Sèvres)** : **présent**

### 2.7 Volume disponible pour le ML

| Split temporel (exemple) | Observations |
|--------------------------|--------------|
| Train (`annee < 2018`) | **184 836** |
| Test (`annee ≥ 2018`) | **149 664** |
| Stations dans le jeu | **2 336** |
| Observations / station (médiane, train) | **~132** |

→ Volume **largement suffisant** pour un **modèle global multi-stations** (avec `NUM_POSTE` ou `code_departement` en feature). La prédiction peut se faire :
- **par station** (fine, pour l'app borne par borne), ou
- **par département** (agrégation des prédictions ou ré-agrégation des données)

---

## 3. Décisions proposées à valider en équipe

### Décision 1 — Granularité de modélisation

| Option | Pour | Contre |
|--------|------|--------|
| **A. Station (NUM_POSTE)** (livrable actuel) | Aligné avec l'app (bornes, GPS, tableaux détaillés), 334 k obs | Modèle plus complexe, hétérogénéité inter-stations |
| **B. Département** (agrégation) | Simple, lisible, aligné brief initial | Perd le détail par borne ; nécessite une étape d'agrégation |
| C. Région seule | Très simple | Perd le détail territorial |

**Proposition** : entraîner un **modèle global sur les stations** (`climat_source.csv`), afficher **par borne** dans l'app et proposer une **vue agrégée département / région** pour la carte choroplèthe.

---

### Décision 2 — Variable cible

**Proposition** : `temp_moy_mensuelle` (TMM Météo-France), cohérente avec le brief « Avg Temp » et disponible sur 100 % des lignes du livrable.

---

### Décision 3 — Fenêtre de prédiction (« 4 semaines passées »)

| Option | Description |
|--------|-------------|
| **A. Lags mensuels M-1, M-2, M-3** | Rapide, données déjà prêtes ; approximation acceptable en hackathon |
| B. Données journalières (Open-Meteo / autre API) | Respecte exactement les 28 jours ; travail d'acquisition supplémentaire |

**Proposition court terme** : option **A** pour le MVP.

---

### Décision 4 — Features à retenir pour le ML

**À garder** :
- Lags (1–3 mois) : température, précipitations
- Features calendaires : mois, saison, sin/cos du mois
- `trend_index` (tendance long terme)
- Identifiant **NUM_POSTE** ou `code_departement` (encodage)
- Coordonnées : `lat`, `lon`, `alti` (effet géographique)

**À exclure du mois courant** (fuite d'information) :
- `temp_max`, `temp_min`, `temp_moy_jour` du mois à prédire

**À utiliser avec prudence** (forts manquants au niveau station) :
- `humidite`, `pression_mer`, `insolation`, `vent_moyen`, `rayonnement_global`

---

### Décision 5 — Répartition des tâches équipe

| Tâche | Responsable suggéré | Livrable |
|-------|---------------------|----------|
| Pipeline données + EDA | **Samir — fait** | `01_exploration_donnees.ipynb` + `climat_source.csv` |
| Feature engineering + ML | À attribuer | `02_modelisation_ml.ipynb` + modèle `.pkl` + `climat_predictions.csv` |
| App Streamlit | À attribuer | Carte (lat/lon), tableaux par NUM_POSTE, graphiques |
| Enrichissement données (pression, solaire) | À attribuer | Script d'acquisition + merge |
| Déploiement local + doc | À attribuer | `README` déploiement, `requirements.txt` |
| Data storytelling / slides | À attribuer | Présentation jury |

---

## 4. Plan d'actions — prochaines étapes

### Phase 1 — Court terme (MVP hackathon)

- [x] Pipeline EDA et export `climat_source.csv` (niveau station + NUM_POSTE)
- [ ] Valider les décisions 1 à 4 en réunion équipe
- [ ] Créer le notebook ML (`02_modelisation_ml.ipynb`) avec split temporel strict (train < 2018, test ≥ 2018)
- [ ] Feature engineering (lags, calendrier, trend, lat/lon/alti)
- [ ] Modèle global multi-stations (Random Forest / XGBoost)
- [ ] Prévision récursive 12–24 mois par NUM_POSTE
- [ ] Exporter `climat_predictions.csv` pour l'application

### Phase 2 — Visualisation (Streamlit)

- [ ] Carte France avec points stations (`lat`, `lon`) ou choroplèthe départementale (agrégation)
- [ ] Curseur année / mois (passé + futur)
- [ ] Tableau par **NUM_POSTE** / nom_station avec filtres région, département, période
- [ ] Graphiques d'évolution par station ou par département
- [ ] Import du modèle (`.pkl`) ou des CSV (historique + prédictions)

### Phase 3 — Enrichissements (si temps)

- [x] Récupérer les données du département 79
- [x] Ajouter NUM_POSTE et coordonnées GPS des stations
- [ ] Données journalières pour respecter les 28 jours
- [ ] Données solaires (NASA)
- [ ] GeoJSON des départements (vue agrégée carte)

### Phase 4 — Livraison

- [ ] Déploiement local de l'app Streamlit
- [ ] Documentation du processus
- [ ] PR GitHub + répartition claire des rôles dans le README

---

## 5. Messages clés pour la présentation jury

1. **Données solides** : 334 500 observations qualité Q=1, **2 336 stations**, **95 départements**, coordonnées GPS intégrées.
2. **Granularité adaptée à l'app** : chaque borne (`NUM_POSTE`) est identifiable pour cartes et tableaux interactifs.
3. **Fortes disparités territoriales** : écart de ~7 °C entre stations/départements les plus chauds et les plus froids.
4. **Approche ML réaliste** : modèle global multi-stations, features lag + saisonnalité + géographie ; prévision récursive 12–24 mois.
5. **Application orientée citoyen** : plateforme Streamlit avec exploration passé/futur par région, département et borne météo.

---

## 6. Points ouverts — à trancher collectivement

1. Modélisation **par station** ou **par département** (avec agrégation) pour le jury ?
2. Accepte-t-on les **lags mensuels** comme proxy des 4 semaines ?
3. Quelles variables à fort taux de manquants exclure du MVP (`humidite`, `pression_mer`, `vent_moyen`) ?
4. Carte : **points stations** (lat/lon) ou **choroplèthe départements** (agrégation) ?
5. Répartition des rôles : ML, app Streamlit, slides ?

---

*Document aligné sur `notebooks/01_exploration_donnees.ipynb` et `src/data/processed/climat_source.csv` (granularité station × mois).*
