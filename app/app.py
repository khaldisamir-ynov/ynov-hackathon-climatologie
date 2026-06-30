import streamlit as st
from style import inject_css, page_header, sidebar_brand

st.set_page_config(
    page_title="ClimaFrance",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
sidebar_brand()

page_header("Bienvenue sur ClimaFrance", "Explorez les donnees climatiques historiques et les predictions futures pour la France metropolitaine.")

col1, col2, col3, col4 = st.columns(4)

cards = [
    ("🗺️", "Carte de France", "Temperatures par station sur carte interactive", "pages/1_🗺️_Carte.py"),
    ("📊", "Tableau des bornes", "Moyennes et tendances par station", "pages/2_📊_Tableau.py"),
    ("📈", "Graphiques", "Evolution des temperatures dans le temps", "pages/3_📈_Graphiques.py"),
    ("🔮", "Predictions", "Previsions a partir d'une date et d'un lieu", "pages/4_🔮_Predictions.py"),
]

for col, (icon, title, desc, page) in zip([col1, col2, col3, col4], cards):
    with col:
        st.markdown(
            f'<div class="nav-card">'
            f'<div class="icon">{icon}</div>'
            f'<div class="title">{title}</div>'
            f'<div class="desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label=f"Ouvrir {title}", icon=icon)

st.divider()

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Departements couverts", "20")
with m2:
    st.metric("Periode historique", "2000 - 2026")
with m3:
    st.metric("Pages disponibles", "4")
