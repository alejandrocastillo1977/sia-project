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
from Admin import mostrar_admin
from Umbrales import mostrar_umbrales
from Auditoria import mostrar_auditoria  # 👈 Nuevo módulo agregado
from Home import main as mostrar_inicio

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
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/2/29/Logo_uniminuto.png",
    width=160
)
st.sidebar.title("📚 Módulos SIA")

modulo = st.sidebar.radio(
    "Selecciona una opción:",
    [
        "Inicio",
        "Cargue ARGOS",
        "Tablero general",
        "Consulta estudiante",
        "Reportes por umbral",
        "🧾 Auditoría del sistema",  # 👈 Nueva opción visible en el menú
        "⚙️ Mantenimiento"
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Versión v1.3.0 – Hito 9 (Exportes, Reportes y Auditoría)")

# ---- ENCABEZADO ----
st.title("🎓 Sistema de Inteligencia Académica – UNIMINUTO")

# ---- RUTEO ENTRE MÓDULOS ----
if modulo == "Inicio":
    mostrar_inicio()

elif modulo == "Cargue ARGOS":
    mostrar_cargue()

elif modulo == "Tablero general":
    mostrar_tablero()

elif modulo == "Consulta estudiante":
    mostrar_consulta()

elif modulo == "Reportes por umbral":
    mostrar_umbrales()

elif modulo == "🧾 Auditoría del sistema":
    mostrar_auditoria()  # 👈 Conecta el nuevo módulo

elif modulo == "⚙️ Mantenimiento":
    mostrar_admin()
