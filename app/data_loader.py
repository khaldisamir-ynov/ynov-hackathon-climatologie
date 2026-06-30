import os
import numpy as np
import pandas as pd
import psycopg2
import streamlit as st

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "climafrance"),
    "user": os.environ.get("DB_USER", "clima"),
    "password": os.environ.get("DB_PASSWORD", "clima123"),
}

DEPT_NAMES = {
    "01": "Ain", "02": "Aisne", "03": "Allier", "04": "Alpes-de-Haute-Provence",
    "05": "Hautes-Alpes", "06": "Alpes-Maritimes", "07": "Ardeche", "08": "Ardennes",
    "09": "Ariege", "10": "Aube", "11": "Aude", "12": "Aveyron",
    "13": "Bouches-du-Rhone", "14": "Calvados", "15": "Cantal", "16": "Charente",
    "17": "Charente-Maritime", "18": "Cher", "19": "Correze", "21": "Cote-d'Or",
    "22": "Cotes-d'Armor", "23": "Creuse", "24": "Dordogne", "25": "Doubs",
    "26": "Drome", "27": "Eure", "28": "Eure-et-Loir", "29": "Finistere",
    "30": "Gard", "31": "Haute-Garonne", "32": "Gers", "33": "Gironde",
    "34": "Herault", "35": "Ille-et-Vilaine", "36": "Indre", "37": "Indre-et-Loire",
    "38": "Isere", "39": "Jura", "40": "Landes", "41": "Loir-et-Cher",
    "42": "Loire", "43": "Haute-Loire", "44": "Loire-Atlantique", "45": "Loiret",
    "46": "Lot", "47": "Lot-et-Garonne", "48": "Lozere", "49": "Maine-et-Loire",
    "50": "Manche", "51": "Marne", "52": "Haute-Marne", "53": "Mayenne",
    "54": "Meurthe-et-Moselle", "55": "Meuse", "56": "Morbihan", "57": "Moselle",
    "58": "Nievre", "59": "Nord", "60": "Oise", "61": "Orne",
    "62": "Pas-de-Calais", "63": "Puy-de-Dome", "64": "Pyrenees-Atlantiques",
    "65": "Hautes-Pyrenees", "66": "Pyrenees-Orientales", "67": "Bas-Rhin",
    "68": "Haut-Rhin", "69": "Rhone", "70": "Haute-Saone", "71": "Saone-et-Loire",
    "72": "Sarthe", "73": "Savoie", "74": "Haute-Savoie", "75": "Paris",
    "76": "Seine-Maritime", "77": "Seine-et-Marne", "78": "Yvelines",
    "79": "Deux-Sevres", "80": "Somme", "81": "Tarn", "82": "Tarn-et-Garonne",
    "83": "Var", "84": "Vaucluse", "85": "Vendee", "86": "Vienne",
    "87": "Haute-Vienne", "88": "Vosges", "89": "Yonne", "90": "Territoire de Belfort",
    "91": "Essonne", "92": "Hauts-de-Seine", "93": "Seine-Saint-Denis",
    "94": "Val-de-Marne", "95": "Val-d'Oise", "20": "Corse",
}

DEPT_REGIONS = {
    "44": "Pays de la Loire", "49": "Pays de la Loire", "53": "Pays de la Loire",
    "72": "Pays de la Loire", "85": "Pays de la Loire",
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    "14": "Normandie", "27": "Normandie", "50": "Normandie", "61": "Normandie", "76": "Normandie",
    "59": "Hauts-de-France", "60": "Hauts-de-France", "62": "Hauts-de-France",
    "80": "Hauts-de-France", "02": "Hauts-de-France",
    "75": "Ile-de-France", "77": "Ile-de-France", "78": "Ile-de-France",
    "91": "Ile-de-France", "92": "Ile-de-France", "93": "Ile-de-France",
    "94": "Ile-de-France", "95": "Ile-de-France",
    "08": "Grand Est", "10": "Grand Est", "51": "Grand Est", "52": "Grand Est",
    "54": "Grand Est", "55": "Grand Est", "57": "Grand Est", "67": "Grand Est",
    "68": "Grand Est", "88": "Grand Est",
    "21": "Bourgogne-Franche-Comte", "25": "Bourgogne-Franche-Comte",
    "39": "Bourgogne-Franche-Comte", "58": "Bourgogne-Franche-Comte",
    "70": "Bourgogne-Franche-Comte", "71": "Bourgogne-Franche-Comte",
    "89": "Bourgogne-Franche-Comte", "90": "Bourgogne-Franche-Comte",
    "18": "Centre-Val de Loire", "28": "Centre-Val de Loire", "36": "Centre-Val de Loire",
    "37": "Centre-Val de Loire", "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",
    "01": "Auvergne-Rhone-Alpes", "03": "Auvergne-Rhone-Alpes", "07": "Auvergne-Rhone-Alpes",
    "15": "Auvergne-Rhone-Alpes", "26": "Auvergne-Rhone-Alpes", "38": "Auvergne-Rhone-Alpes",
    "42": "Auvergne-Rhone-Alpes", "43": "Auvergne-Rhone-Alpes", "63": "Auvergne-Rhone-Alpes",
    "69": "Auvergne-Rhone-Alpes", "73": "Auvergne-Rhone-Alpes", "74": "Auvergne-Rhone-Alpes",
    "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
    "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
    "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
    "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",
    "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie",
    "31": "Occitanie", "32": "Occitanie", "34": "Occitanie", "46": "Occitanie",
    "48": "Occitanie", "65": "Occitanie", "66": "Occitanie", "81": "Occitanie",
    "82": "Occitanie",
    "04": "Provence-Alpes-Cote d'Azur", "05": "Provence-Alpes-Cote d'Azur",
    "06": "Provence-Alpes-Cote d'Azur", "13": "Provence-Alpes-Cote d'Azur",
    "83": "Provence-Alpes-Cote d'Azur", "84": "Provence-Alpes-Cote d'Azur",
    "20": "Corse",
}

DEPT_COORDS = {
    "01": (46.2, 5.3), "02": (49.5, 3.6), "03": (46.3, 3.2), "04": (44.1, 6.2),
    "05": (44.7, 6.3), "06": (43.8, 7.2), "07": (44.7, 4.6), "08": (49.6, 4.6),
    "09": (42.9, 1.5), "10": (48.3, 4.1), "11": (43.1, 2.4), "12": (44.3, 2.6),
    "13": (43.5, 5.1), "14": (49.1, -0.4), "15": (45.0, 2.7), "16": (45.7, 0.2),
    "17": (45.9, -0.8), "18": (47.1, 2.4), "19": (45.3, 1.8), "20": (42.2, 9.1),
    "21": (47.3, 4.8), "22": (48.4, -3.0), "23": (46.1, 2.1), "24": (45.0, 0.7),
    "25": (47.2, 6.4), "26": (44.7, 5.2), "27": (49.1, 1.2), "28": (48.4, 1.5),
    "29": (48.4, -4.3), "30": (44.0, 4.1), "31": (43.6, 1.4), "32": (43.6, 0.6),
    "33": (44.8, -0.6), "34": (43.6, 3.5), "35": (48.1, -1.7), "36": (46.8, 1.6),
    "37": (47.3, 0.7), "38": (45.3, 5.7), "39": (46.7, 5.7), "40": (43.9, -0.8),
    "41": (47.6, 1.3), "42": (45.7, 4.2), "43": (45.1, 3.6), "44": (47.3, -1.8),
    "45": (47.9, 2.1), "46": (44.5, 1.4), "47": (44.3, 0.5), "48": (44.5, 3.5),
    "49": (47.4, -0.6), "50": (48.9, -1.3), "51": (49.0, 3.9), "52": (48.1, 5.3),
    "53": (48.1, -0.8), "54": (48.8, 6.2), "55": (49.0, 5.4), "56": (47.8, -2.8),
    "57": (49.0, 6.7), "58": (47.1, 3.5), "59": (50.4, 3.1), "60": (49.4, 2.4),
    "61": (48.6, 0.1), "62": (50.5, 2.3), "63": (45.7, 3.1), "64": (43.3, -0.8),
    "65": (43.0, 0.2), "66": (42.6, 2.5), "67": (48.6, 7.5), "68": (47.9, 7.2),
    "69": (45.8, 4.6), "70": (47.6, 6.2), "71": (46.6, 4.4), "72": (47.9, 0.2),
    "73": (45.5, 6.4), "74": (46.0, 6.3), "75": (48.9, 2.3), "76": (49.7, 1.1),
    "77": (48.6, 2.9), "78": (48.8, 1.9), "79": (46.5, -0.3), "80": (49.9, 2.3),
    "81": (43.8, 2.2), "82": (44.0, 1.3), "83": (43.5, 6.3), "84": (44.1, 5.1),
    "85": (46.7, -1.3), "86": (46.6, 0.3), "87": (45.9, 1.3), "88": (48.2, 6.5),
    "89": (47.8, 3.6), "90": (47.6, 6.9), "91": (48.5, 2.2), "92": (48.8, 2.2),
    "93": (48.9, 2.5), "94": (48.8, 2.5), "95": (49.1, 2.2),
}


def get_db_connection():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except psycopg2.OperationalError:
        return None


def _get_row_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM historic_weather")
    count = cur.fetchone()[0]
    cur.close()
    return count


CHUNK_SIZE = 200_000


def load_historic_data():
    return load_all_data()


def load_predictions():
    if "_predictions_cache" in st.session_state:
        return st.session_state["_predictions_cache"]

    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()

    progress_text = st.empty()
    progress_bar = st.empty()

    try:
        progress_text.markdown("🔌 **Connexion** — chargement des predictions...")
        progress_bar.progress(0.3)

        df = pd.read_sql(
            "SELECT num_poste, dept, annee, mois, tn_pred, tx_pred FROM predictions",
            conn,
        )
        conn.close()

        progress_bar.progress(0.8)

        if not df.empty:
            df["dept"] = df["dept"].str.zfill(2)
            df["tm_pred"] = ((df["tn_pred"] + df["tx_pred"]) / 2).round(1)

        progress_text.markdown(f"✅ **{len(df):,}** lignes de predictions chargees.")
        progress_bar.progress(1.0)

        import time
        time.sleep(0.5)
        progress_text.empty()
        progress_bar.empty()

        st.session_state["_predictions_cache"] = df
        return df
    except Exception:
        if conn:
            conn.close()
        progress_text.empty()
        progress_bar.empty()
        return pd.DataFrame()


def load_all_data():
    if "_historic_cache" in st.session_state:
        return st.session_state["_historic_cache"]

    conn = get_db_connection()
    if conn is None:
        return _generate_mock_data()

    progress_text = st.empty()
    progress_bar = st.empty()

    try:
        progress_text.markdown("🔌 **Connexion a la base de donnees...**")
        progress_bar.progress(0.0)

        total = _get_row_count(conn)
        if total == 0:
            conn.close()
            progress_text.empty()
            progress_bar.empty()
            return _generate_mock_data()

        progress_text.markdown(f" **Chargement de {total:,} lignes** — 0%")
        progress_bar.progress(0.05)

        chunks = []
        loaded = 0
        for chunk in pd.read_sql(
            "SELECT num_poste, nom_usuel, dept, annee, mois, tm, tx, tn "
            "FROM historic_weather",
            conn,
            chunksize=CHUNK_SIZE,
        ):
            chunks.append(chunk)
            loaded += len(chunk)
            pct = min(loaded / total, 0.85)
            progress_bar.progress(pct)
            progress_text.markdown(
                f" **Chargement** — {loaded:,} / {total:,} lignes ({int(pct*100)}%)"
            )

        conn.close()

        progress_text.markdown("🔧 **Enrichissement des donnees** (noms, regions, coordonnees)...")
        progress_bar.progress(0.90)

        df = pd.concat(chunks, ignore_index=True)
        df.columns = ["NUM_POSTE", "NOM_USUEL", "DEPT", "ANNEE", "MOIS", "TM", "TX", "TN"]
        df["DEPT"] = df["DEPT"].str.zfill(2)
        df["DEPT_NOM"] = df["DEPT"].map(DEPT_NAMES).fillna("Inconnu")
        df["REGION"] = df["DEPT"].map(DEPT_REGIONS).fillna("Autre")
        df["LAT"] = df["DEPT"].map(lambda d: DEPT_COORDS.get(d, (None, None))[0])
        df["LON"] = df["DEPT"].map(lambda d: DEPT_COORDS.get(d, (None, None))[1])

        progress_bar.progress(1.0)
        progress_text.markdown(
            f" **{len(df):,} lignes chargees** — "
            f"{df['DEPT'].nunique()} departements, "
            f"periode {int(df['ANNEE'].min())}-{int(df['ANNEE'].max())}"
        )

        import time
        time.sleep(1.0)
        progress_text.empty()
        progress_bar.empty()

        st.session_state["_historic_cache"] = df
        return df

    except Exception as e:
        if conn:
            conn.close()
        print(f"DB error: {e}")
        progress_text.empty()
        progress_bar.empty()
        return _generate_mock_data()


MONTHLY_BASE_TEMP = {
    1: 3.5, 2: 4.5, 3: 8.0, 4: 11.0, 5: 15.0, 6: 18.5,
    7: 21.0, 8: 20.5, 9: 17.0, 10: 12.5, 11: 7.5, 12: 4.5,
}


def _generate_mock_data():
    """Fallback mock data when database is not available."""
    rng = np.random.default_rng(42)
    rows = []
    for dept in DEPT_COORDS:
        lat, lon = DEPT_COORDS[dept]
        lat_factor = (lat - 43.0) / 7.0
        station_name = f"STATION_{DEPT_NAMES.get(dept, dept).upper().replace(' ', '_')[:12]}"
        num_poste = int(dept) * 100000 + 1
        for year in range(2000, 2027):
            for month in range(1, 13):
                if year == 2026 and month > 6:
                    continue
                base = MONTHLY_BASE_TEMP[month]
                tm = round(base - lat_factor * 3 + rng.normal(0, 1.2) + (year - 2000) * 0.03, 1)
                tx = round(tm + 5 + rng.normal(0, 0.8), 1)
                tn = round(tm - 5 + rng.normal(0, 0.8), 1)
                rr = round(max(0, 40 + rng.normal(0, 25)), 1)
                rows.append({
                    "NUM_POSTE": num_poste, "NOM_USUEL": station_name,
                    "LAT": lat, "LON": lon, "ALTI": int(100 + rng.integers(0, 500)),
                    "DEPT": dept, "ANNEE": year, "MOIS": month,
                    "TM": tm, "TX": tx, "TN": tn, "RR": rr,
                    "DEPT_NOM": DEPT_NAMES.get(dept, "Inconnu"),
                    "REGION": DEPT_REGIONS.get(dept, "Autre"),
                })
    return pd.DataFrame(rows)
