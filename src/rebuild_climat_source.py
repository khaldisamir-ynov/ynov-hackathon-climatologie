"""Regénère climat_source.csv avec filtre Q0/Q1/Q9."""
from pathlib import Path
import re
import gc
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "src" / "data"
PROCESSED_DIR = DATA_DIR / "processed"
GEO_PATH = DATA_DIR / "referentiel_geo_departements.csv"
SOURCE_CSV = PROCESSED_DIR / "climat_source.csv"

ALLOWED_Q_CODES = {0, 1, 9}

VARIABLES = {
    "precipitations_mm": ("RR", "QRR"),
    "temp_max": ("TX", "QTX"),
    "temp_min": ("TN", "QTN"),
    "temp_moy_jour": ("TM", "QTM"),
    "temp_moy_mensuelle": ("TMM", "QTMM"),
    "humidite": ("UMM", "QUMM"),
    "pression_mer": ("PMERM", "QPMERM"),
    "vent_moyen": ("FFM", "QFFM"),
    "insolation": ("INST", "QINST"),
    "rayonnement_global": ("GLOT", "QGLOT"),
    "evapotranspiration": ("ETP", "QETP"),
    "rafale_max": ("FXIAB", "QFXIAB"),
}

ID_COLS = [
    "NUM_POSTE", "nom_station", "lat", "lon", "alti",
    "code_departement", "nom_departement", "code_region", "nom_region",
]
TIME_COLS = ["annee", "mois", "date"]
METEO_COLS = list(VARIABLES.keys())
SOURCE_COLUMNS = ID_COLS + TIME_COLS + METEO_COLS


def apply_quality_filter(df, value_col, quality_col):
    values = pd.to_numeric(df[value_col], errors="coerce")
    quality = pd.to_numeric(df[quality_col], errors="coerce")
    allowed = quality.isin(ALLOWED_Q_CODES)
    has_value = quality.isin({1, 9})
    return values.where(allowed & has_value)


def keep_allowed_quality_rows(df):
    mask = pd.Series(True, index=df.index)
    for _, q_col in VARIABLES.values():
        if q_col not in df.columns:
            continue
        q = pd.to_numeric(df[q_col], errors="coerce")
        mask &= q.isna() | q.isin(ALLOWED_Q_CODES)
    return df[mask].copy()


USECOLS = ["NUM_POSTE", "NOM_USUEL", "LAT", "LON", "ALTI", "AAAAMM"] + sorted(
    {c for pair in VARIABLES.values() for c in pair}
)

files_by_dept = defaultdict(list)
for path in sorted(DATA_DIR.glob("MENSQ_*_*.csv")):
    m = re.match(r"MENSQ_(\d+)_", path.name)
    if m:
        files_by_dept[m.group(1).zfill(2)].append(path)

station_monthly_parts = []
for dept, paths in sorted(files_by_dept.items()):
    chunk = pd.concat([pd.read_csv(p, sep=";", usecols=USECOLS) for p in paths], ignore_index=True)
    chunk["code_departement"] = dept
    chunk["annee"] = chunk["AAAAMM"].astype(str).str[:4].astype(int)
    chunk["mois"] = chunk["AAAAMM"].astype(str).str[4:6].astype(int)
    chunk = keep_allowed_quality_rows(chunk)

    station_meta = chunk.groupby("NUM_POSTE", as_index=False).agg(
        nom_station=("NOM_USUEL", "first"),
        lat=("LAT", "first"),
        lon=("LON", "first"),
        alti=("ALTI", "first"),
    )

    clean = chunk[["NUM_POSTE", "code_departement", "annee", "mois"]].copy()
    for target, (value_col, quality_col) in VARIABLES.items():
        clean[target] = apply_quality_filter(chunk, value_col, quality_col)

    clean = clean.merge(station_meta, on="NUM_POSTE", how="left")
    clean = clean.drop_duplicates(subset=["NUM_POSTE", "annee", "mois"], keep="last")
    station_monthly_parts.append(clean)
    del chunk, clean, station_meta
    gc.collect()

station_monthly = pd.concat(station_monthly_parts, ignore_index=True)
station_monthly["date"] = pd.to_datetime(
    {"year": station_monthly["annee"], "month": station_monthly["mois"], "day": 1}
)
station_monthly["NUM_POSTE"] = station_monthly["NUM_POSTE"].astype(str).str.zfill(8)

geo = pd.read_csv(GEO_PATH, sep=";")
geo["code_departement"] = geo["code_departement"].astype(str).str.zfill(2)
station_monthly = station_monthly.merge(geo, on="code_departement", how="left")

post2000 = station_monthly[station_monthly["annee"] > 2000].copy()
complete_pairs = (
    post2000.groupby(["NUM_POSTE", "annee"])
    .filter(lambda g: g["mois"].nunique() == 12 and g["temp_moy_mensuelle"].notna().all())
    [["NUM_POSTE", "annee"]]
    .drop_duplicates()
)

built_df = post2000.merge(complete_pairs, on=["NUM_POSTE", "annee"], how="inner")
built_df = built_df[SOURCE_COLUMNS].sort_values(["NUM_POSTE", "annee", "mois"]).reset_index(drop=True)
built_df["code_departement"] = built_df["code_departement"].astype(str).str.zfill(2)
built_df.to_csv(SOURCE_CSV, index=False)

print(f"Export: {SOURCE_CSV}")
print(f"Lignes: {len(built_df):,} | Stations: {built_df['NUM_POSTE'].nunique()}")
print(f"Période: {built_df['annee'].min()}-{built_df['annee'].max()}")
