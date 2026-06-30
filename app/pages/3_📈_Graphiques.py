import streamlit as st
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data
from style import inject_css, page_header, sidebar_brand, COLORS

st.set_page_config(page_title="Graphiques - ClimaFrance", layout="wide", page_icon="📈")
inject_css()
sidebar_brand()

page_header("📈 Evolution des temperatures", "Tendances historiques par departement")

data = load_all_data()
if data.empty:
    st.error("Aucune donnee trouvee.")
    st.stop()

dept_options = sorted(data["DEPT"].unique())
dept_labels = {}
for d in dept_options:
    rows = data[data["DEPT"] == d]
    if len(rows) > 0:
        dept_labels[d] = f"{d} - {rows['DEPT_NOM'].iloc[0]}"

st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])
with col1:
    dept = st.selectbox(
        "Departement",
        options=dept_options,
        format_func=lambda x: dept_labels.get(x, x),
        index=dept_options.index("75") if "75" in dept_options else 0,
    )
with col2:
    min_year = int(data["ANNEE"].min())
    max_year = int(data["ANNEE"].max())
    periode = st.slider("Periode", min_value=min_year, max_value=max_year, value=(min_year, max_year))
st.markdown('</div>', unsafe_allow_html=True)

filtered = data[
    (data["DEPT"] == dept)
    & (data["ANNEE"] >= periode[0])
    & (data["ANNEE"] <= periode[1])
].copy()
filtered = filtered.dropna(subset=["TM"])

yearly = filtered.groupby("ANNEE").agg(
    TM_moy=("TM", "mean"),
    TX_moy=("TX", "mean"),
    TN_moy=("TN", "mean"),
).reset_index()
yearly = yearly.round(1)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("T° moy sur la periode", f"{yearly['TM_moy'].mean():.1f}°C")
with c2:
    st.metric("T° max record", f"{yearly['TX_moy'].max():.1f}°C")
with c3:
    st.metric("T° min record", f"{yearly['TN_moy'].min():.1f}°C")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=yearly["ANNEE"], y=yearly["TX_moy"],
    name="T° max moyenne", mode="lines",
    line=dict(color=COLORS["warm"], width=2),
))
fig.add_trace(go.Scatter(
    x=yearly["ANNEE"], y=yearly["TM_moy"],
    name="T° moyenne", mode="lines",
    line=dict(color=COLORS["amber"], width=2),
))
fig.add_trace(go.Scatter(
    x=yearly["ANNEE"], y=yearly["TN_moy"],
    name="T° min moyenne", mode="lines",
    line=dict(color=COLORS["cold"], width=2),
))
fig.update_layout(
    title=f"Evolution annuelle - {dept_labels.get(dept, dept)}",
    xaxis_title="Annee",
    yaxis_title="Temperature (°C)",
    hovermode="x unified",
    template="plotly_white",
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Evolution mensuelle")

monthly = filtered.groupby("MOIS").agg(
    TM_moy=("TM", "mean"),
    TX_moy=("TX", "mean"),
    TN_moy=("TN", "mean"),
).reset_index()
monthly = monthly.round(1)

MOIS_NOMS = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Avr", 5: "Mai", 6: "Jun",
    7: "Jul", 8: "Aou", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}
monthly["Mois_nom"] = monthly["MOIS"].map(MOIS_NOMS)

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=monthly["Mois_nom"], y=monthly["TX_moy"],
    name="T° max moy", marker_color=COLORS["warm"],
))
fig2.add_trace(go.Bar(
    x=monthly["Mois_nom"], y=monthly["TM_moy"],
    name="T° moy", marker_color=COLORS["amber"],
))
fig2.add_trace(go.Bar(
    x=monthly["Mois_nom"], y=monthly["TN_moy"],
    name="T° min moy", marker_color=COLORS["cold"],
))
fig2.update_layout(
    barmode="group",
    title=f"Temperatures moyennes mensuelles - {dept_labels.get(dept, dept)}",
    xaxis_title="Mois",
    yaxis_title="Temperature (°C)",
    template="plotly_white",
    height=400,
)
st.plotly_chart(fig2, use_container_width=True)
