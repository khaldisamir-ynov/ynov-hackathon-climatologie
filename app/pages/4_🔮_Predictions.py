import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data

st.set_page_config(page_title="Predictions - ClimaFrance", layout="wide", page_icon="🔮")
st.sidebar.title("🌡️ ClimaFrance")

st.markdown("## 🔮 Predictions")
st.caption("Prediction de temperature pour un departement et une date")

data = load_all_data()
if data.empty:
    st.error("Aucune donnee trouvee.")
    st.stop()

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
model_path = os.path.join(MODEL_DIR, "model.pkl")
model_available = os.path.exists(model_path)

dept_options = sorted(data["DEPT"].unique())
dept_labels = {}
for d in dept_options:
    rows = data[data["DEPT"] == d]
    if len(rows) > 0:
        dept_labels[d] = f"{d} - {rows['DEPT_NOM'].iloc[0]}"

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    dept = st.selectbox(
        "Departement",
        options=dept_options,
        format_func=lambda x: dept_labels.get(x, x),
        index=dept_options.index("75") if "75" in dept_options else 0,
    )
with col2:
    date_pred = st.date_input("Date de prediction", value=pd.Timestamp("2027-07-01"))
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🔮 Predire", type="primary", use_container_width=True)


def predict_with_historical(dept_code, year, month):
    dept_data = data[(data["DEPT"] == dept_code) & (data["MOIS"] == month)]
    dept_data = dept_data.dropna(subset=["TM"])
    if dept_data.empty:
        return None, None, None

    yearly_avg = dept_data.groupby("ANNEE").agg(
        TM=("TM", "mean"), TX=("TX", "mean"), TN=("TN", "mean")
    ).reset_index()

    if len(yearly_avg) < 5:
        return None, None, None

    from numpy.polynomial import polynomial as P
    x = yearly_avg["ANNEE"].values.astype(float)

    results = {}
    for col in ["TM", "TX", "TN"]:
        y = yearly_avg[col].dropna().values
        x_clean = x[: len(y)]
        if len(x_clean) < 5:
            results[col] = None
            continue
        coeffs = P.polyfit(x_clean, y, deg=2)
        results[col] = round(float(P.polyval(year, coeffs)), 1)

    return results.get("TM"), results.get("TX"), results.get("TN")


def predict_with_model(dept_code, year, month):
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    features = pd.DataFrame({"DEPT": [int(dept_code)], "ANNEE": [year], "MOIS": [month]})
    pred = model.predict(features)
    if hasattr(pred, "__len__") and len(pred[0]) >= 3:
        return round(pred[0][0], 1), round(pred[0][1], 1), round(pred[0][2], 1)
    return round(float(pred[0]), 1), None, None


if predict_btn:
    year = date_pred.year
    month = date_pred.month

    MOIS_NOMS = {
        1: "Janvier", 2: "Fevrier", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Aout", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Decembre",
    }

    st.markdown(f"### Prediction pour {dept_labels.get(dept, dept)} - {MOIS_NOMS[month]} {year}")

    if model_available:
        tm, tx, tn = predict_with_model(dept, year, month)
        st.info("Prediction effectuee avec le modele ML importe.")
    else:
        tm, tx, tn = predict_with_historical(dept, year, month)
        st.info("Prediction basee sur la tendance historique (aucun modele ML importe).")

    if tm is None:
        st.warning("Pas assez de donnees pour effectuer une prediction.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Temperature moyenne", f"{tm}°C")
        with c2:
            if tx is not None:
                st.metric("Temperature max", f"{tx}°C")
        with c3:
            if tn is not None:
                st.metric("Temperature min", f"{tn}°C")

        dept_data = data[(data["DEPT"] == dept) & (data["MOIS"] == month)].dropna(subset=["TM"])
        yearly = dept_data.groupby("ANNEE")["TM"].mean().reset_index()
        yearly = yearly.sort_values("ANNEE")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly["ANNEE"], y=yearly["TM"].round(1),
            name="Historique", mode="lines+markers",
            line=dict(color="#378ADD", width=2),
            marker=dict(size=3),
        ))
        fig.add_trace(go.Scatter(
            x=[year], y=[tm],
            name="Prediction", mode="markers",
            marker=dict(color="#D85A30", size=12, symbol="star"),
        ))
        fig.update_layout(
            title=f"T° moyenne en {MOIS_NOMS[month]} - {dept_labels.get(dept, dept)}",
            xaxis_title="Annee",
            yaxis_title="Temperature (°C)",
            template="plotly_white",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("### Importer un modele ML")
st.caption("Votre equipe data peut fournir un modele pickle (.pkl) entraine pour ameliorer les predictions.")

uploaded = st.file_uploader("Charger un modele (.pkl)", type=["pkl"])
if uploaded:
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(model_path, "wb") as f:
        f.write(uploaded.read())
    st.success("Modele importe avec succes ! Relancez une prediction.")
    st.rerun()
