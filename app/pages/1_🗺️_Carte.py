import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data

st.set_page_config(page_title="Carte - ClimaFrance", layout="wide", page_icon="🗺️")
st.sidebar.title("🌡️ ClimaFrance")

st.markdown("## 🗺️ Carte des temperatures")
st.caption("Explorez les temperatures moyennes par station sur la carte de France")

data = load_all_data()
if data.empty:
    st.error("Aucune donnee trouvee.")
    st.stop()

min_year = int(data["ANNEE"].min())
max_year = int(data["ANNEE"].max())

MOIS_NOMS = {
    1: "Janvier", 2: "Fevrier", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
    7: "Juillet", 8: "Aout", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Decembre",
}

col1, col2 = st.columns([3, 1])
with col1:
    annee = st.slider("Annee", min_value=min_year, max_value=max_year, value=max_year - 1)
with col2:
    mois = st.selectbox("Mois", options=list(range(1, 13)), format_func=lambda x: MOIS_NOMS[x], index=6)

filtered = data[(data["ANNEE"] == annee) & (data["MOIS"] == mois)].copy()
filtered = filtered.dropna(subset=["LAT", "LON", "TM"])
filtered = filtered.drop_duplicates(subset=["NUM_POSTE"])

if filtered.empty:
    st.warning(f"Aucune donnee disponible pour {MOIS_NOMS[mois]} {annee}.")
    st.stop()

avg_by_dept = filtered.groupby("DEPT").agg(
    TM_mean=("TM", "mean"),
    LAT_mean=("LAT", "mean"),
    LON_mean=("LON", "mean"),
).reset_index()

st.metric("Stations affichees", len(filtered))

m = folium.Map(location=[46.8, 2.3], zoom_start=6, tiles="CartoDB positron")

t_min = filtered["TM"].quantile(0.05)
t_max = filtered["TM"].quantile(0.95)

from branca.colormap import LinearColormap
colormap = LinearColormap(
    colors=["#378ADD", "#5DCAA5", "#EF9F27", "#E24B4A"],
    vmin=t_min,
    vmax=t_max,
    caption=f"Temperature moyenne (°C) - {MOIS_NOMS[mois]} {annee}",
)
colormap.add_to(m)

for _, row in filtered.iterrows():
    color = colormap(row["TM"]) if not np.isnan(row["TM"]) else "#888"
    folium.CircleMarker(
        location=[row["LAT"], row["LON"]],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=folium.Popup(
            f"<b>{row['NOM_USUEL']}</b><br>"
            f"Dept: {row['DEPT']} - {row.get('DEPT_NOM', '')}<br>"
            f"T° moy: {row['TM']:.1f}°C<br>"
            f"T° max: {row['TX']:.1f}°C<br>"
            f"T° min: {row['TN']:.1f}°C" if not np.isnan(row.get("TX", float("nan"))) else f"<b>{row['NOM_USUEL']}</b><br>T° moy: {row['TM']:.1f}°C",
            max_width=250,
        ),
    ).add_to(m)

st_folium(m, width=None, height=550, use_container_width=True)
