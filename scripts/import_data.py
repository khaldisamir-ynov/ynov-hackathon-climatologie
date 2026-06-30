import os
import glob
import csv
import psycopg2
import time

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "climafrance"),
    "user": os.environ.get("DB_USER", "clima"),
    "password": os.environ.get("DB_PASSWORD", "clima123"),
}


def wait_for_db():
    for i in range(30):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            return True
        except psycopg2.OperationalError:
            print(f"DB not ready, retry {i+1}/30...")
            time.sleep(2)
    return False


def is_already_imported(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM historic_weather")
    count = cur.fetchone()[0]
    cur.close()
    return count > 0


def parse_float(val):
    if val is None or val.strip() == "":
        return None
    try:
        return float(val)
    except ValueError:
        return None


def parse_int(val):
    if val is None or val.strip() == "":
        return None
    try:
        return int(float(val))
    except ValueError:
        return None


def extract_dept_from_filename(filepath):
    basename = os.path.basename(filepath)
    parts = basename.replace("MENSQ_", "").split("_")
    return parts[0]


def import_historic(conn):
    cur = conn.cursor()
    csv_files = sorted(glob.glob("Data/MENSQ_*_previous-1950-2024.csv") +
                       glob.glob("Data/MENSQ_*_latest-2025-2026.csv"))

    if not csv_files:
        print("No historic CSV files found in Data/")
        return

    total_inserted = 0
    for filepath in csv_files:
        dept = extract_dept_from_filename(filepath)
        print(f"Importing {os.path.basename(filepath)} (dept {dept})...")
        batch = []

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                aaaamm = row.get("AAAAMM", "")
                if not aaaamm or len(aaaamm) < 6:
                    continue

                annee = int(aaaamm[:4])
                mois = int(aaaamm[4:6])

                batch.append((
                    parse_int(row.get("NUM_POSTE")),
                    row.get("NOM_USUEL", "").strip(),
                    dept,
                    annee,
                    mois,
                    parse_float(row.get("TM")),
                    parse_float(row.get("TX")),
                    parse_float(row.get("TN")),
                ))

                if len(batch) >= 5000:
                    cur.executemany(
                        "INSERT INTO historic_weather "
                        "(num_poste, nom_usuel, dept, annee, mois, tm, tx, tn) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        batch,
                    )
                    total_inserted += len(batch)
                    batch = []

        if batch:
            cur.executemany(
                "INSERT INTO historic_weather "
                "(num_poste, nom_usuel, dept, annee, mois, tm, tx, tn) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                batch,
            )
            total_inserted += len(batch)

        conn.commit()

    print(f"Historic import done: {total_inserted} rows inserted.")


def import_predictions(conn):
    cur = conn.cursor()
    filepath = "predictions_data/predictions_2026_2027_24.csv"

    if not os.path.exists(filepath):
        print("No predictions CSV found.")
        return

    cur.execute("SELECT COUNT(*) FROM predictions")
    if cur.fetchone()[0] > 0:
        print("Predictions already imported, skipping.")
        return

    print("Importing predictions_2026_2027_24.csv...")
    batch = []

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=",")
        for row in reader:
            num_poste = parse_int(row.get("NUM_POSTE"))
            dept = row.get("DEP", "").strip().zfill(2)
            forecast_start = row.get("forecast_start", "2026-01")
            start_year = int(forecast_start.split("-")[0])
            start_month = int(forecast_start.split("-")[1])

            for i in range(1, 25):
                tn = parse_float(row.get(f"MIN_{i}"))
                tx = parse_float(row.get(f"MAX_{i}"))
                month_offset = i - 1
                annee = start_year + (start_month - 1 + month_offset) // 12
                mois = (start_month - 1 + month_offset) % 12 + 1
                batch.append((num_poste, dept, annee, mois, tn, tx))

    if batch:
        cur.executemany(
            "INSERT INTO predictions "
            "(num_poste, dept, annee, mois, tn_pred, tx_pred) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            batch,
        )
        conn.commit()
        print(f"Predictions import done: {len(batch)} rows inserted.")


if __name__ == "__main__":
    print("Waiting for database...")
    if not wait_for_db():
        print("ERROR: Could not connect to database.")
        exit(1)

    conn = psycopg2.connect(**DB_CONFIG)

    if is_already_imported(conn):
        print("Historic data already imported, skipping.")
    else:
        import_historic(conn)

    import_predictions(conn)

    conn.close()
    print("Import complete!")
