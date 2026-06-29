# WeatherForYnov — Synthèse de l'exploration des données

> Document de travail pour validation en équipe — Hackathon YNOV, Sujet 2  
> Basé sur le notebook `notebooks/01_exploration_donnees.ipynb`

---

## 1. Contexte et périmètre

Nous avons consolidé les données climatiques mensuelles **Météo-France (MENSQ)** pour la France métropolitaine, avec pour objectif final de **prédire la température moyenne mensuelle par département**, puis de l'afficher aussi au niveau **régional**.

| Élément | Valeur |
|---------|--------|
| Période couverte | **1950 – 2026** |
| Départements | **94** (métropole, hors 79) |
| Régions | **13** |
| Observations station × mois | **520 766** |
| Observations département × mois | **67 836** |
| Stations météo (moyenne / dépt) | **~29** (max. 88) |

**Fichiers produits** (`src/data/processed/`) :
- `climat_mensuel_france.csv` — granularité station
- `climat_mensuel_departements.csv` — agrégation départementale (niveau ML principal)
- `climat_mensuel_regions.csv` — agrégation régionale (visualisation)

---

## 2. Principaux constats de l'analyse exploratoire

### 2.1 Température — vue d'ensemble

- Température moyenne mensuelle nationale : **~11,1 °C** (écart-type **~6,0 °C**)
- Saisonnalité marquée :
  - Hiver : **~4,3 °C**
  - Printemps : **~10,2 °C**
  - Été : **~18,5 °C**
  - Automne : **~11,6 °C**

### 2.2 Tendance climatique (changement climatique)

- Tendance linéaire observée : **+0,021 °C / an** sur la période 1950–2024
- Moyenne annuelle :
  - Années 1950 : **~10,8 °C**
  - Années 2010 : **~11,3 °C**
- **Interprétation** : réchauffement lent mais mesurable, cohérent avec la littérature climatique. La variable `trend_index` est pertinente comme feature ML.

### 2.3 Disparités territoriales

**Régions les plus chaudes** (moyenne historique) :
- Corse (~14,9 °C)
- Provence-Alpes-Côte d'Azur (Bouches-du-Rhône, Var…)

**Départements les plus froids** :
- Haute-Savoie (~7,6 °C)
- Savoie (~7,7 °C)
- Hautes-Pyrénées (~8,0 °C)

→ Fort contraste **littoral méditerranéen / massifs montagneux**, à prendre en compte pour la modélisation (effet altitude, latitude).

### 2.4 Précipitations

- Moyenne nationale : **~70 mm / mois**
- Corrélation faible avec la température (**r ≈ -0,11**) : les mois chauds ne sont pas systématiquement les plus secs au niveau mensuel agrégé.

### 2.5 Matrice de corrélation — enseignements clés

| Variable | Corrélation avec `temp_moy_mensuelle` | Implication |
|----------|---------------------------------------|-------------|
| `temp_max` | **+0,99** | Très redondant avec la cible → risque de fuite d'information |
| `temp_min` | **+0,98** | Idem |
| `insolation` | **+0,78** | Feature pertinente |
| `humidite` | **-0,52** | Feature pertinente (relation inverse) |
| `vent_moyen` | **-0,19** | Signal faible mais exploitable |
| `precipitations_mm` | **-0,11** | Signal faible seul |

**Point d'attention ML** : inclure `temp_max` et `temp_min` du **même mois** dans un modèle prédictif de la température moyenne mensuelle revient presque à « tricher ». Il faudra utiliser des **lags** (mois précédents) ou exclure ces variables du mois courant.

### 2.6 Qualité et complétude des données

| Variable | Taux de manquants (niveau département) |
|----------|----------------------------------------|
| `temp_moy_mensuelle` | **0 %** |
| `precipitations_mm` | **0,1 %** |
| `vent_moyen` | **1,1 %** |
| `humidite` | **10,7 %** |
| `insolation` | **10,4 %** |
| `pression_mer` | Très incomplet sur l'historique |

- Département **79 (Deux-Sèvres)** : **absent** des fichiers MENSQ fournis
- Données **2025–2026** : disponibles mais partielles selon les stations (période en cours)

---

## 3. Décisions proposées à valider en équipe

### Décision 1 — Granularité de modélisation

| Option | Pour | Contre |
|--------|------|--------|
| **A. Département** (recommandé) | Aligné avec le brief, 94 territoires, jeu `climat_mensuel_departements.csv` prêt | Hétérogénéité intra-départementale |
| B. Station | Plus précis localement | Trop de modèles, difficile à cartographier |
| C. Région seule | Simple, lisible | Perd le détail territorial demandé |

**Proposition** : modéliser au **département**, agréger en **région** pour l'affichage.

---

### Décision 2 — Variable cible

**Proposition** : `temp_moy_mensuelle` (TMM Météo-France), cohérente avec le brief « Avg Temp » et disponible sur 100 % des lignes départementales.

---

### Décision 3 — Fenêtre de prédiction (« 4 semaines passées »)

| Option | Description |
|--------|-------------|
| **A. Lags mensuels M-1, M-2, M-3** (actuel dans `02_modelisation_ml.ipynb`) | Rapide, données déjà prêtes ; approximation acceptable en hackathon |
| B. Données journalières (Open-Meteo / autre API) | Respecte exactement les 28 jours ; travail d'acquisition supplémentaire |

**Proposition court terme** : option **A** pour le MVP. Option **B** en phase 2 si le jury exige la contrainte exacte.

---

### Décision 4 — Features à retenir pour le ML

**À garder** :
- Lags (1–3 mois) : température, précipitations, humidité, vent, insolation
- Features calendaires : mois, saison, trimestre, sin/cos du mois
- `trend_index` (tendance long terme)
- Identifiant département (encodage ou modèle par groupe)

**À exclure du mois courant** (fuite d'information) :
- `temp_max`, `temp_min`, `temp_moy_jour` du mois à prédire

**À compléter via API externe** (si temps disponible) :
- Couverture nuageuse, pression, éruptions solaires (NASA)

---

### Décision 5 — Répartition des tâches équipe

| Tâche | Responsable suggéré | Livrable |
|-------|---------------------|----------|
| Pipeline données + EDA | Fait | `01_exploration_donnees.ipynb` + exports |
| Modélisation ML | À attribuer | `02_modelisation_ml.ipynb` + modèle exporté (`.pkl`) |
| App Dash/Plotly | À attribuer | Carte France interactive, filtres année/mois/région |
| Enrichissement données (79, pression, solaire) | À attribuer | Script d'acquisition + merge |
| Déploiement local + doc | À attribuer | `README` déploiement, `requirements.txt` |
| Data storytelling / slides | À attribuer | Présentation jury avec tendances + prévisions |

---

## 4. Plan d'actions — prochaines étapes

### Phase 1 — Court terme (MVP hackathon)

- [ ] Valider les décisions 1 à 4 en réunion équipe
- [ ] Finaliser le notebook ML avec split temporel strict (train < 2018, test ≥ 2018)
- [ ] Corriger le risque de data leakage (retirer features du mois courant trop corrélées)
- [ ] Choisir le modèle final (Random Forest / Gradient Boosting / XGBoost)
- [ ] Exporter les prévisions par département pour l'application

### Phase 2 — Visualisation

- [ ] Carte choroplèthe France : température observée vs prédite par département
- [ ] Slider temporel (année / mois)
- [ ] Vue agrégée par région avec indicateurs (température, précipitations, tendance)
- [ ] Graphique de tendance 1950–2026 (data storytelling changement climatique)

### Phase 3 — Enrichissements (si temps)

- [ ] Récupérer les données du département 79
- [ ] Données journalières pour respecter les 28 jours
- [ ] Données solaires (NASA) pour la feature « Solar Flares »
- [ ] Matrice de corrélation par saison et par région (analyse complémentaire)

### Phase 4 — Livraison

- [ ] Déploiement local de l'app (Dash ou Streamlit)
- [ ] Documentation du processus
- [ ] PR GitHub + répartition claire des rôles dans le README

---

## 5. Messages clés pour la présentation jury

1. **Données solides** : 75 ans d'historique, 94 départements, référentiel géographique intégré.
2. **Signal climatique détecté** : +0,02 °C/an en moyenne nationale depuis 1950.
3. **Fortes disparités territoriales** : écart de ~7 °C entre les départements les plus chauds et les plus froids.
4. **Approche ML réaliste** : prédiction mensuelle par département, avec features lag et saisonnalité.
5. **Application orientée citoyen** : visualisation par région pour anticiper les évolutions locales.

---

## 6. Points ouverts — à trancher collectivement

1. Accepte-t-on les **lags mensuels** comme proxy des 4 semaines, ou investit-on dans des **données journalières** ?
2. Comment gère-t-on le **département 79** manquant (interpolation voisins, API complémentaire, exclusion) ?
3. Quel framework pour l'app : **Dash**, **Streamlit** ou **Plotly + HTML** ?
4. Quel membre prend le **ML**, l'**app**, l'**acquisition de données** ?
5. Faut-il pousser l'analyse de corrélation **par saison / par région** avant de figer les features ?

---

*Document généré à partir des exports `src/data/processed/` — à mettre à jour après validation équipe.*
