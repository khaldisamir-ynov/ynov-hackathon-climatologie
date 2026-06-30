import streamlit as st

st.set_page_config(
    page_title="ClimaFrance",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🌡️ ClimaFrance")
st.sidebar.caption("Exploration climatique de la France")

st.markdown("## Bienvenue sur ClimaFrance")
st.markdown(
    "Explorez les donnees climatiques historiques et les predictions futures "
    "pour tous les departements de France metropolitaine."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.page_link("pages/1_🗺️_Carte.py", label="Carte de France", icon="🗺️")
with col2:
    st.page_link("pages/2_📊_Tableau.py", label="Tableau des bornes", icon="📊")
with col3:
    st.page_link("pages/3_📈_Graphiques.py", label="Graphiques", icon="📈")
with col4:
    st.page_link("pages/4_🔮_Predictions.py", label="Predictions", icon="🔮")
