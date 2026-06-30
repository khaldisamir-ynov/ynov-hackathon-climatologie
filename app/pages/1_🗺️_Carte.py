import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import json
import urllib.request
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data_loader import load_all_data, DEPT_REGIONS, DEPT_NAMES
from style import inject_css, page_header, sidebar_brand, COLORS

GEOJSON_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson"


@st.cache_data(show_spinner="Chargement des contours departements...")
def load_geojson():
    with urllib.request.urlopen(GEOJSON_URL) as resp:
        return json.loads(resp.read().decode())


st.set_page_config(page_title="Carte - ClimaFrance", layout="wide", page_icon="🗺️")
inject_css()
sidebar_brand()

page_header("🗺️ Carte des temperatures", "Temperatures moyennes par departement sur la carte de France")

data = load_all_data()
if data.empty:
    st.error("Aucune donnee trouvee.")
    st.stop()

geojson_data = load_geojson()

min_year = int(data["ANNEE"].min())
max_year = int(data["ANNEE"].max())

MOIS_NOMS = {
    1: "Janvier", 2: "Fevrier", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
    7: "Juillet", 8: "Aout", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Decembre",
}

regions = sorted(data["REGION"].dropna().unique())

st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    annee = st.slider("Annee", min_value=min_year, max_value=max_year, value=max_year - 1)
with col2:
    mois = st.selectbox("Mois", options=list(range(1, 13)), format_func=lambda x: MOIS_NOMS[x], index=6)
with col3:
    region = st.selectbox("Region", options=["Toutes"] + regions)
st.markdown('</div>', unsafe_allow_html=True)

filtered = data[(data["ANNEE"] == annee) & (data["MOIS"] == mois)].copy()
if region != "Toutes":
    filtered = filtered[filtered["REGION"] == region]

dept_agg = filtered.groupby(["DEPT", "DEPT_NOM", "REGION"]).agg(
    TM=("TM", "mean"),
    TX=("TX", "mean"),
    TN=("TN", "mean"),
    LAT=("LAT", "first"),
    LON=("LON", "first"),
).reset_index()
dept_agg = dept_agg.dropna(subset=["TM"])

if dept_agg.empty:
    st.warning(f"Aucune donnee disponible pour {MOIS_NOMS[mois]} {annee}.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Departements", len(dept_agg))
with c2:
    st.metric("T° moyenne nationale", f"{dept_agg['TM'].mean():.1f}°C")
with c3:
    warmest = dept_agg.loc[dept_agg["TM"].idxmax()]
    st.metric(f"Plus chaud ({warmest['DEPT']})", f"{warmest['TM']:.1f}°C")
with c4:
    coldest = dept_agg.loc[dept_agg["TM"].idxmin()]
    st.metric(f"Plus froid ({coldest['DEPT']})", f"{coldest['TM']:.1f}°C")

if region != "Toutes":
    center_lat = dept_agg["LAT"].mean()
    center_lon = dept_agg["LON"].mean()
    zoom = 7
else:
    center_lat, center_lon, zoom = 46.8, 2.3, 6

m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles="CartoDB positron")

temp_by_dept = dict(zip(dept_agg["DEPT"], dept_agg["TM"]))
tx_by_dept = dict(zip(dept_agg["DEPT"], dept_agg["TX"]))
tn_by_dept = dict(zip(dept_agg["DEPT"], dept_agg["TN"]))
nom_by_dept = dict(zip(dept_agg["DEPT"], dept_agg["DEPT_NOM"]))
region_by_dept = dict(zip(dept_agg["DEPT"], dept_agg["REGION"]))

t_min = dept_agg["TM"].quantile(0.05)
t_max = dept_agg["TM"].quantile(0.95)

from branca.colormap import LinearColormap
colormap = LinearColormap(
    colors=[COLORS["cold"], "#7EC8A0", COLORS["amber"], COLORS["warm"]],
    vmin=t_min,
    vmax=t_max,
    caption=f"Temperature moyenne (°C) - {MOIS_NOMS[mois]} {annee}",
)
colormap.add_to(m)

if region != "Toutes":
    filtered_codes = set(dept_agg["DEPT"].values)
    geo_filtered = {
        "type": "FeatureCollection",
        "features": [
            f for f in geojson_data["features"]
            if f["properties"].get("code") in filtered_codes
        ],
    }
else:
    geo_filtered = geojson_data

for feature in geo_filtered["features"]:
    code = feature["properties"].get("code", "")
    tm = temp_by_dept.get(code)
    nom = nom_by_dept.get(code, feature["properties"].get("nom", ""))
    if tm is not None:
        tx = tx_by_dept.get(code, 0)
        tn = tn_by_dept.get(code, 0)
        reg = region_by_dept.get(code, "")
        feature["properties"]["dept_label"] = f"{code} — {nom}"
        feature["properties"]["region"] = reg
        feature["properties"]["tm_display"] = f"🌡️ Moy : {tm:.1f}°C"
        feature["properties"]["tx_display"] = f"🔴 Max : {tx:.1f}°C"
        feature["properties"]["tn_display"] = f"🔵 Min : {tn:.1f}°C"
    else:
        feature["properties"]["dept_label"] = f"{code} — {nom}"
        feature["properties"]["region"] = ""
        feature["properties"]["tm_display"] = "Pas de donnees"
        feature["properties"]["tx_display"] = ""
        feature["properties"]["tn_display"] = ""


def style_function(feature):
    code = feature["properties"].get("code", "")
    tm = temp_by_dept.get(code)
    if tm is not None:
        color = colormap(tm)
        return {
            "fillColor": color,
            "color": "#FFFFFF",
            "weight": 1.5,
            "fillOpacity": 0.7,
        }
    return {
        "fillColor": "#E2E8F0",
        "color": "#FFFFFF",
        "weight": 1,
        "fillOpacity": 0.3,
    }


def highlight_function(feature):
    return {
        "weight": 3,
        "color": COLORS["primary"],
        "fillOpacity": 0.85,
    }


tooltip_style = (
    "background-color: white;"
    "border: 2px solid #1B6B93;"
    "border-radius: 8px;"
    "padding: 8px 12px;"
    "font-family: sans-serif;"
    "font-size: 13px;"
    "font-weight: 500;"
    "box-shadow: 0 2px 8px rgba(0,0,0,0.15);"
    "color: #1A1A2E;"
)

geojson_layer = folium.GeoJson(
    geo_filtered,
    style_function=style_function,
    highlight_function=highlight_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["dept_label", "region", "tm_display", "tx_display", "tn_display"],
        aliases=["", "", "", "", ""],
        style=tooltip_style,
        sticky=True,
    ),
)
geojson_layer.add_to(m)

for _, row in dept_agg.iterrows():
    folium.Marker(
        location=[row["LAT"], row["LON"]],
        icon=folium.DivIcon(
            html=f'<div style="font-size:10px;font-weight:700;color:#1A1A2E;'
                 f'text-align:center;text-shadow:0 0 3px #fff,0 0 3px #fff;'
                 f'pointer-events:none;">'
                 f'{row["TM"]:.0f}°</div>',
            icon_size=(36, 14),
            icon_anchor=(18, 7),
        ),
    ).add_to(m)

st_folium(m, width=None, height=580, use_container_width=True, returned_objects=[])
