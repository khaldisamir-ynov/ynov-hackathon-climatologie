import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data, load_predictions, DEPT_NAMES
from style import inject_css, page_header, sidebar_brand, COLORS

st.set_page_config(page_title="Predictions - ClimaFrance", layout="wide", page_icon="🔮")
inject_css()
sidebar_brand()

page_header("🔮 Predictions 2026-2027", "Temperatures predites par departement pour 2026 et 2027")

data = load_all_data()
predictions = load_predictions()

if data.empty:
    st.error("Aucune donnee historique trouvee.")
    st.stop()

if predictions.empty:
    st.warning("Aucune donnee de prediction trouvee en base.")
    st.stop()

MOIS_NOMS = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Avr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Aou", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

pred_depts = sorted(predictions["dept"].unique())
pred_years = sorted(predictions["annee"].unique())
dept_labels = {d: f"{d} - {DEPT_NAMES.get(d, d)}" for d in pred_depts}

st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])
with col1:
    dept = st.selectbox(
        "Departement",
        options=pred_depts,
        format_func=lambda x: dept_labels.get(x, x),
        index=pred_depts.index("75") if "75" in pred_depts else 0,
    )
with col2:
    annee = st.selectbox("Annee", options=pred_years, index=0)
st.markdown('</div>', unsafe_allow_html=True)

dept_preds = predictions[(predictions["dept"] == dept) & (predictions["annee"] == annee)]

pred_monthly = dept_preds.groupby("mois").agg(
    tn=("tn_pred", "mean"),
    tx=("tx_pred", "mean"),
    tm=("tm_pred", "mean"),
).reset_index().round(1)
pred_monthly["mois_nom"] = pred_monthly["mois"].map(MOIS_NOMS)
pred_monthly = pred_monthly.sort_values("mois")

if pred_monthly.empty:
    st.warning("Pas de predictions pour cette selection.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(f"T° moy {annee}", f"{pred_monthly['tm'].mean():.1f}°C")
with c2:
    hottest = pred_monthly.loc[pred_monthly["tx"].idxmax()]
    st.metric(f"Mois le + chaud ({hottest['mois_nom']})", f"{hottest['tx']:.1f}°C")
with c3:
    coldest = pred_monthly.loc[pred_monthly["tn"].idxmin()]
    st.metric(f"Mois le + froid ({coldest['mois_nom']})", f"{coldest['tn']:.1f}°C")
with c4:
    st.metric("Amplitude annuelle", f"{pred_monthly['tx'].max() - pred_monthly['tn'].min():.1f}°C")

# --- Graphique 1 : Predictions mensuelles ---
st.markdown(f"### Predictions mensuelles {annee}")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=pred_monthly["mois_nom"], y=pred_monthly["tx"],
    name="T° max predite", mode="lines+markers",
    line=dict(color=COLORS["warm"], width=2), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=pred_monthly["mois_nom"], y=pred_monthly["tm"],
    name="T° moy predite", mode="lines+markers",
    line=dict(color=COLORS["amber"], width=2), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=pred_monthly["mois_nom"], y=pred_monthly["tn"],
    name="T° min predite", mode="lines+markers",
    line=dict(color=COLORS["cold"], width=2), marker=dict(size=6),
))
fig.add_trace(go.Scatter(
    x=pred_monthly["mois_nom"].tolist() + pred_monthly["mois_nom"].tolist()[::-1],
    y=pred_monthly["tx"].tolist() + pred_monthly["tn"].tolist()[::-1],
    fill="toself", fillcolor="rgba(212,101,74,0.1)",
    line=dict(width=0), name="Intervalle min-max", showlegend=True,
))

fig.update_layout(
    title=f"Temperatures predites {annee} - {dept_labels.get(dept, dept)}",
    xaxis_title="Mois", yaxis_title="Temperature (°C)",
    template="plotly_white", height=450, hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)

# --- Graphique 2 : Historique + predictions ---
st.markdown("### Comparaison avec l'historique")

hist_dept = data[data["DEPT"] == dept].dropna(subset=["TM"])

if not hist_dept.empty:
    yearly = hist_dept.groupby("ANNEE").agg(
        TM=("TM", "mean"), TX=("TX", "mean"), TN=("TN", "mean"),
    ).reset_index().round(1).sort_values("ANNEE")

    pred_yearly = predictions[predictions["dept"] == dept].groupby("annee").agg(
        tm=("tm_pred", "mean"), tx=("tx_pred", "mean"), tn=("tn_pred", "mean"),
    ).reset_index().round(1)
    pred_yearly["annee"] = pred_yearly["annee"].astype(int)
    pred_yearly = pred_yearly.sort_values("annee")

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=yearly["ANNEE"], y=yearly["TX"],
        name="T° max historique", mode="lines",
        line=dict(color=COLORS["warm"], width=1.5), opacity=0.7,
    ))
    fig2.add_trace(go.Scatter(
        x=yearly["ANNEE"], y=yearly["TM"],
        name="T° moy historique", mode="lines",
        line=dict(color=COLORS["amber"], width=1.5), opacity=0.7,
    ))
    fig2.add_trace(go.Scatter(
        x=yearly["ANNEE"], y=yearly["TN"],
        name="T° min historique", mode="lines",
        line=dict(color=COLORS["cold"], width=1.5), opacity=0.7,
    ))

    for i, row in pred_yearly.iterrows():
        show = (i == pred_yearly.index[0])
        fig2.add_trace(go.Scatter(
            x=[row["annee"]], y=[row["tx"]],
            name="Prediction max", mode="markers",
            marker=dict(color=COLORS["warm"], size=14, symbol="star"),
            showlegend=show,
        ))
        fig2.add_trace(go.Scatter(
            x=[row["annee"]], y=[row["tm"]],
            name="Prediction moy", mode="markers",
            marker=dict(color=COLORS["amber"], size=14, symbol="star"),
            showlegend=show,
        ))
        fig2.add_trace(go.Scatter(
            x=[row["annee"]], y=[row["tn"]],
            name="Prediction min", mode="markers",
            marker=dict(color=COLORS["cold"], size=14, symbol="star"),
            showlegend=show,
        ))

    fig2.update_layout(
        title=f"Evolution annuelle + predictions - {dept_labels.get(dept, dept)}",
        xaxis_title="Annee", yaxis_title="Temperature (°C)",
        template="plotly_white", height=450, hovermode="x unified",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Pas de donnees historiques disponibles pour ce departement.")

# --- Tableau recapitulatif ---
st.markdown(f"### Detail mensuel {annee}")

display_df = pred_monthly[["mois_nom", "tn", "tm", "tx"]].copy()
display_df.columns = ["Mois", "T° min (°C)", "T° moy (°C)", "T° max (°C)"]

st.dataframe(display_df, use_container_width=True, hide_index=True)
