# WeatherForYnov — Synthèse de l'exploration des données

> Document de travail pour validation en équipe — Hackathon YNOV, Sujet 2  
> Basé sur le notebook `notebooks/01_exploration_donnees.ipynb` et l'export `src/data/processed/climat_source.csv`  
> *Dernière mise à jour : juin 2026*

---

## 1. Contexte et périmètre

Nous avons consolidé les données climatiques mensuelles **Météo-France (MENSQ)** pour la France métropolitaine, avec pour objectif final de **prédire la température moyenne mensuelle par département**, puis de l'afficher au niveau **régional** dans une plateforme interactive (Streamlit).

### Données brutes chargées (exploration)

| Élément | Valeur |
|---------|--------|
| Fichiers MENSQ | **189** (2 par département : historique + récent) |
| Période brute | **1950 – 2026** |
| Observations station × mois | **3 262 696** |
| Stations météo | **9 405** |
| Départements couverts | **95** (métropole + Corse, **dont le 79**) |

### Livrable EDA — fichier source unique

Après filtrage qualité **Q = 1**, enrichissement géographique et filtres finaux, un **seul fichier** est produit pour le feature engineering et la modélisation :

**`src/data/processed/climat_source.csv`**

| Élément | Valeur |
|---------|--------|
| Granularité | **département × mois** |
| Période | **2001 – 2025** (filtre `annee > 2000`) |
| Départements | **95** |
| Régions | **13** |
| Observations finales | **25 560** |
| Couples département × année complets | **2 130** (12 mois avec TMM renseignée chaque mois) |
| Colonnes | 19 (géo + calendrier + 12 variables météo) |

**Filtres appliqués :**
- Code qualité Météo-France **Q = 1** uniquement (valeurs certifiées)
- Agrégation par **moyenne des stations** du département
- Fusion du référentiel `referentiel_geo_departements.csv` (régions)
- **Après 2000** : `annee > 2000`
- **Séries complètes** : 12 mois par département et par année, avec `temp_moy_mensuelle` non nulle sur chaque mois

---

## 2. Principaux constats de l'analyse exploratoire

*Statistiques ci-dessous calculées sur `climat_source.csv` (2001–2025).*

### 2.1 Température — vue d'ensemble

- Température moyenne mensuelle nationale : **11,6 °C** (écart-type **6,0 °C**)
- Saisonnalité marquée :
  - Hiver : **4,6 °C**
  - Printemps : **10,7 °C**
  - Été : **19,1 °C**
  - Automne : **12,0 °C**

### 2.2 Tendance climatique (changement climatique)

- Tendance linéaire observée : **+0,035 °C / an** sur la période 2001–2025
- Moyenne annuelle nationale :
  - **2001** : **11,1 °C**
  - **2010–2019** : **11,4 °C**
- **Interprétation** : réchauffement mesurable sur la fenêtre récente. La variable `trend_index` reste pertinente comme feature ML.

> **Note** : l'historique brut remonte à 1950, mais le livrable modélisation est volontairement restreint à **post-2000** pour garantir la qualité et la complétude des séries.

### 2.3 Disparités territoriales

**Régions les plus chaudes** (moyenne 2001–2025) :
- Corse (~14,7 °C)
- Nouvelle-Aquitaine (~12,6 °C)
- Pays de la Loire (~12,3 °C)

**Départements les plus chauds** :
- Var (~14,7 °C)
- Bouches-du-Rhône (~14,7 °C)
- Corse-du-Sud (~14,7 °C)

**Départements les plus froids** :
- Savoie (~6,9 °C)
- Hautes-Alpes (~7,6 °C)
- Haute-Savoie (~8,4 °C)

→ Fort contraste **littoral méditerranéen / massifs montagneux**, à prendre en compte pour la modélisation (effet altitude, latitude).

### 2.4 Précipitations

- Moyenne nationale : **~76 mm / mois**
- Corrélation modérée avec la température (**r ≈ −0,18**) : les mois chauds ne sont pas systématiquement les plus secs au niveau mensuel agrégé.

### 2.5 Matrice de corrélation — enseignements clés

| Variable | Corrélation avec `temp_moy_mensuelle` | Implication |
|----------|---------------------------------------|-------------|
| `temp_max` | **+0,99** | Très redondant avec la cible → risque de fuite d'information |
| `temp_min` | **+0,98** | Idem |
| `insolation` | **+0,78** | Feature pertinente (mais 34 % de manquants) |
| `humidite` | **−0,59** | Feature pertinente (relation inverse, 55 % de manquants) |
| `vent_moyen` | **−0,24** | Signal faible mais exploitable |
| `precipitations_mm` | **−0,18** | Signal faible seul |

**Point d'attention ML** : inclure `temp_max` et `temp_min` du **même mois** dans un modèle prédictif de la température moyenne mensuelle revient presque à « tricher ». Il faudra utiliser des **lags** (mois précédents) ou exclure ces variables du mois courant.

### 2.6 Qualité et complétude des données

| Variable | Taux de manquants (`climat_source.csv`) |
|----------|----------------------------------------|
| `temp_moy_mensuelle` | **0 %** |
| `precipitations_mm` | **0 %** |
| `evapotranspiration` | **0 %** |
| `vent_moyen` | **1,0 %** |
| `rafale_max` | **1,1 %** |
| `insolation` | **34,5 %** |
| `rayonnement_global` | **37,1 %** |
| `humidite` | **55,2 %** |
| `pression_mer` | **57,5 %** |

**Points de vigilance :**
- Départements **93** (72 obs), **92** (120 obs) et **94** (240 obs) : historiques plus courts après filtrage → prévisions moins fiables
- Données **2025** : incluses si la série annuelle est complète (12 mois + TMM)
- Département **79 (Deux-Sèvres)** : **présent** (récupéré depuis la branche `aurelie`)

### 2.7 Volume disponible pour le ML

| Split temporel (exemple) | Observations |
|--------------------------|--------------|
| Train (`annee < 2018`) | **16 524** (~180 obs / dépt) |
| Test (`annee ≥ 2018`) | **9 036** (~96 obs / dépt) |

→ Volume **suffisant** pour un **modèle global multi-départements** ; insuffisant pour 95 modèles séparés complexes.

---

## 3. Décisions proposées à valider en équipe

### Décision 1 — Granularité de modélisation

| Option | Pour | Contre |
|--------|------|--------|
| **A. Département** (recommandé) | Aligné avec le brief, 95 territoires, `climat_source.csv` prêt | Hétérogénéité intra-départementale |
| B. Station (borne) | Plus précis localement | Non couvert par le livrable actuel ; volume et cartographie plus complexes |
| C. Région seule | Simple, lisible | Perd le détail territorial demandé |

**Proposition** : modéliser au **département**, agréger en **région** pour l'affichage.

---

### Décision 2 — Variable cible

**Proposition** : `temp_moy_mensuelle` (TMM Météo-France), cohérente avec le brief « Avg Temp » et disponible sur 100 % des lignes du livrable.

---

### Décision 3 — Fenêtre de prédiction (« 4 semaines passées »)

| Option | Description |
|--------|-------------|
| **A. Lags mensuels M-1, M-2, M-3** | Rapide, données déjà prêtes ; approximation acceptable en hackathon |
| B. Données journalières (Open-Meteo / autre API) | Respecte exactement les 28 jours ; travail d'acquisition supplémentaire |

**Proposition court terme** : option **A** pour le MVP. Option **B** en phase 2 si le jury exige la contrainte exacte.

---

### Décision 4 — Features à retenir pour le ML

**À garder** :
- Lags (1–3 mois) : température, précipitations, vent (humidité/insolation si complétude acceptable)
- Features calendaires : mois, saison, trimestre, sin/cos du mois
- `trend_index` (tendance long terme)
- Identifiant département (encodage ou modèle par groupe)

**À exclure du mois courant** (fuite d'information) :
- `temp_max`, `temp_min`, `temp_moy_jour` du mois à prédire

**À utiliser avec prudence** (forts taux de manquants) :
- `humidite`, `pression_mer`, `insolation`, `rayonnement_global`

**À compléter via API externe** (si temps disponible) :
- Couverture nuageuse, pression, éruptions solaires (NASA)

---

### Décision 5 — Répartition des tâches équipe

| Tâche | Responsable suggéré | Livrable |
|-------|---------------------|----------|
| Pipeline données + EDA | **Samir — fait** | `01_exploration_donnees.ipynb` + `climat_source.csv` |
| Feature engineering + ML | À attribuer | `02_modelisation_ml.ipynb` + modèle `.pkl` + `climat_predictions.csv` |
| App Streamlit | À attribuer | Carte France, tableaux, graphiques (passé + futur) |
| Enrichissement données (pression, solaire) | À attribuer | Script d'acquisition + merge |
| Déploiement local + doc | À attribuer | `README` déploiement, `requirements.txt` |
| Data storytelling / slides | À attribuer | Présentation jury avec tendances + prévisions |

---

## 4. Plan d'actions — prochaines étapes

### Phase 1 — Court terme (MVP hackathon)

- [x] Pipeline EDA et export `climat_source.csv`
- [ ] Valider les décisions 1 à 4 en réunion équipe
- [ ] Créer le notebook ML (`02_modelisation_ml.ipynb`) avec split temporel strict (train < 2018, test ≥ 2018)
- [ ] Feature engineering (lags, calendrier, trend)
- [ ] Corriger le risque de data leakage (retirer features du mois courant trop corrélées)
- [ ] Choisir le modèle final (Random Forest / Gradient Boosting / XGBoost)
- [ ] Prévision récursive 12–24 mois par département
- [ ] Exporter `climat_predictions.csv` pour l'application

### Phase 2 — Visualisation (Streamlit)

- [ ] Carte choroplèthe France : température observée vs prédite par département
- [ ] Curseur année / mois (exploration passé + futur)
- [ ] Tableau avec filtres région, département, période
- [ ] Graphiques d'évolution des températures par département
- [ ] Import du modèle (`.pkl`) ou des CSV (historique + prédictions)

### Phase 3 — Enrichissements (si temps)

- [x] Récupérer les données du département 79
- [ ] Données journalières pour respecter les 28 jours
- [ ] Données solaires (NASA) pour la feature « Solar Flares »
- [ ] Matrice de corrélation par saison et par région (analyse complémentaire)
- [ ] GeoJSON des départements pour la carte interactive

### Phase 4 — Livraison

- [ ] Déploiement local de l'app Streamlit
- [ ] Documentation du processus
- [ ] PR GitHub + répartition claire des rôles dans le README

---

## 5. Messages clés pour la présentation jury

1. **Données solides** : 25 ans d'historique qualité Q=1, **95 départements**, référentiel géographique intégré.
2. **Signal climatique détecté** : +0,035 °C/an en moyenne nationale depuis 2001.
3. **Fortes disparités territoriales** : écart de ~8 °C entre les départements les plus chauds et les plus froids.
4. **Approche ML réaliste** : prédiction mensuelle par département (modèle global), avec features lag et saisonnalité ; prévision récursive sur 12–24 mois.
5. **Application orientée citoyen** : plateforme Streamlit avec carte, tableaux et graphiques par région/département.

---

## 6. Points ouverts — à trancher collectivement

1. Accepte-t-on les **lags mensuels** comme proxy des 4 semaines, ou investit-on dans des **données journalières** ?
2. Quel framework pour l'app : **Streamlit** (recommandé), Dash ou Plotly + HTML ?
3. Quel membre prend le **ML**, l'**app**, l'**acquisition de données** ?
4. Faut-il pousser l'analyse de corrélation **par saison / par région** avant de figer les features ?
5. Quelles variables à fort taux de manquants (`humidite`, `pression_mer`) exclure du MVP ?

---

*Document aligné sur `notebooks/01_exploration_donnees.ipynb` et `src/data/processed/climat_source.csv`.*
