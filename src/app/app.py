import streamlit as st
from pathlib import Path

# ---- CONFIGURACIÓN GENERAL ----
st.set_page_config(
    page_title="SIA – Sistema de Inteligencia Académica",
    page_icon="🎓",
    layout="wide",
)

# ---- IMPORTACIÓN DE MÓDULOS PRINCIPALES ----
from Cargue import mostrar_cargue
from Tablero import mostrar_tablero
from Consulta import mostrar_consulta
from Admin import mostrar_admin  # 👈 Nuevo módulo agregado

# ---- ESTILOS PERSONALIZADOS ----
st.markdown("""
    <style>
        .main {
            background-color: #f4f4f9;
        }
        h1, h2, h3 {
            color: #0033A0;
        }
        .stMetricValue {
            color: #0033A0 !important;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

# ---- SIDEBAR ----
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/29/Logo_uniminuto.png", width=160)
st.sidebar.title("📚 Módulos SIA")

modulo = st.sidebar.radio(
    "Selecciona una opción:",
    [
        "Inicio",
        "Cargue ARGOS",
        "Tablero general",
        "Consulta estudiante",
        "Reportes por umbral",
        "⚙️ Mantenimiento"  # 👈 Nueva opción visible en menú lateral
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Versión prototipo v1.2 – Hito 8")

# ---- ENCABEZADO ----
st.title("🎓 Sistema de Inteligencia Académica – UNIMINUTO")

# ---- RUTEO ENTRE MÓDULOS ----
if modulo == "Inicio":
    st.subheader("🏠 Inicio")
    st.write("Bienvenido al SIA. Usa el menú lateral para navegar por los módulos.")

elif modulo == "Cargue ARGOS":
    mostrar_cargue()

elif modulo == "Tablero general":
    mostrar_tablero()

elif modulo == "Consulta estudiante":
    mostrar_consulta()

elif modulo == "Reportes por umbral":
    st.subheader("📈 Reportes por umbral de avance")
    st.caption("Implementación prevista para el Hito 9.")

elif modulo == "⚙️ Mantenimiento":  # 👈 Nuevo bloque de mantenimiento
    mostrar_admin()
