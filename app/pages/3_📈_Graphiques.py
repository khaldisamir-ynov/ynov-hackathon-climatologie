import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data

st.set_page_config(page_title="Graphiques - ClimaFrance", layout="wide", page_icon="📈")
st.sidebar.title("🌡️ ClimaFrance")

st.markdown("## 📈 Evolution des temperatures")
st.caption("Tendances historiques par departement")

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

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=yearly["ANNEE"], y=yearly["TX_moy"],
    name="T° max moyenne", mode="lines",
    line=dict(color="#E24B4A", width=2),
))
fig.add_trace(go.Scatter(
    x=yearly["ANNEE"], y=yearly["TM_moy"],
    name="T° moyenne", mode="lines",
    line=dict(color="#EF9F27", width=2),
))
fig.add_trace(go.Scatter(
    x=yearly["ANNEE"], y=yearly["TN_moy"],
    name="T° min moyenne", mode="lines",
    line=dict(color="#378ADD", width=2),
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
    name="T° max moy", marker_color="#E24B4A",
))
fig2.add_trace(go.Bar(
    x=monthly["Mois_nom"], y=monthly["TM_moy"],
    name="T° moy", marker_color="#EF9F27",
))
fig2.add_trace(go.Bar(
    x=monthly["Mois_nom"], y=monthly["TN_moy"],
    name="T° min moy", marker_color="#378ADD",
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
