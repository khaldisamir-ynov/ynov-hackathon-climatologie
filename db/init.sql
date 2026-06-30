CREATE TABLE IF NOT EXISTS historic_weather (
    id SERIAL PRIMARY KEY,
    num_poste INTEGER NOT NULL,
    nom_usuel VARCHAR(100),
    dept VARCHAR(3),
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    tm DOUBLE PRECISION,
    tx DOUBLE PRECISION,
    tn DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    num_poste INTEGER NOT NULL,
    dept VARCHAR(3) NOT NULL,
    annee INTEGER NOT NULL,
    mois INTEGER NOT NULL,
    tn_pred DOUBLE PRECISION,
    tx_pred DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_historic_dept ON historic_weather(dept);
CREATE INDEX IF NOT EXISTS idx_historic_annee_mois ON historic_weather(annee, mois);
CREATE INDEX IF NOT EXISTS idx_historic_dept_annee ON historic_weather(dept, annee, mois);
CREATE INDEX IF NOT EXISTS idx_predictions_dept ON predictions(dept);
CREATE INDEX IF NOT EXISTS idx_predictions_dept_annee ON predictions(dept, annee, mois);
