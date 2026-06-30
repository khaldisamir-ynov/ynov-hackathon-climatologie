import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data, DEPT_REGIONS

st.set_page_config(page_title="Tableau - ClimaFrance", layout="wide", page_icon="📊")
st.sidebar.title("🌡️ ClimaFrance")

st.markdown("## 📊 Tableau des bornes")
st.caption("Moyennes et predictions par station meteorologique")

data = load_all_data()
if data.empty:
    st.error("Aucune donnee trouvee.")
    st.stop()

regions = sorted(data["REGION"].dropna().unique())
col1, col2, col3 = st.columns(3)

with col1:
    region = st.selectbox("Region", options=["Toutes"] + regions)

if region != "Toutes":
    dept_options = sorted(data[data["REGION"] == region]["DEPT"].unique())
else:
    dept_options = sorted(data["DEPT"].unique())

with col2:
    dept_labels = {d: f"{d} - {data[data['DEPT'] == d]['DEPT_NOM'].iloc[0]}" for d in dept_options if len(data[data['DEPT'] == d]) > 0}
    dept = st.selectbox("Departement", options=["Tous"] + list(dept_labels.keys()), format_func=lambda x: "Tous" if x == "Tous" else dept_labels.get(x, x))

min_year = int(data["ANNEE"].min())
max_year = int(data["ANNEE"].max())
with col3:
    periode = st.slider("Periode", min_value=min_year, max_value=max_year, value=(max_year - 5, max_year))

filtered = data[(data["ANNEE"] >= periode[0]) & (data["ANNEE"] <= periode[1])]
if region != "Toutes":
    filtered = filtered[filtered["REGION"] == region]
if dept != "Tous":
    filtered = filtered[filtered["DEPT"] == dept]

filtered = filtered.dropna(subset=["TM"])

stats = filtered.groupby(["DEPT", "DEPT_NOM", "NUM_POSTE", "NOM_USUEL"]).agg(
    TM_moy=("TM", "mean"),
    TX_max=("TX", "max"),
    TN_min=("TN", "min"),
    nb_mois=("TM", "count"),
).reset_index()

stats["TM_moy"] = stats["TM_moy"].round(1)
stats["TX_max"] = stats["TX_max"].round(1)
stats["TN_min"] = stats["TN_min"].round(1)

last_5 = data[(data["ANNEE"] >= max_year - 4) & (data["ANNEE"] <= max_year)]
last_5 = last_5.dropna(subset=["TM"])
prev_5 = data[(data["ANNEE"] >= max_year - 9) & (data["ANNEE"] <= max_year - 5)]
prev_5 = prev_5.dropna(subset=["TM"])

trend_recent = last_5.groupby("NUM_POSTE")["TM"].mean()
trend_prev = prev_5.groupby("NUM_POSTE")["TM"].mean()
trend = (trend_recent - trend_prev).round(2)
trend.name = "Tendance"

stats = stats.merge(trend.reset_index(), on="NUM_POSTE", how="left")

display_df = stats[["DEPT", "DEPT_NOM", "NOM_USUEL", "TM_moy", "TX_max", "TN_min", "Tendance", "nb_mois"]].copy()
display_df.columns = ["Dept", "Departement", "Station", "T° moy (°C)", "T° max (°C)", "T° min (°C)", "Tendance (°C)", "Nb mois"]
display_df = display_df.sort_values(["Dept", "Station"])

st.metric("Stations", len(display_df))

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Tendance (°C)": st.column_config.NumberColumn(
            format="%.2f",
            help="Difference de temperature moyenne entre les 5 dernieres annees et les 5 precedentes",
        ),
    },
)
