import streamlit as st

# ---- CONFIGURACIÓN GENERAL ----
st.set_page_config(
    page_title="SIA – Sistema de Inteligencia Académica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- IMPORTACIÓN DE MÓDULOS PRINCIPALES ----
from Cargue import mostrar_cargue
from Tablero import mostrar_tablero
from Consulta import mostrar_consulta
from Admin import mostrar_admin
from Umbrales import mostrar_umbrales
from Auditoria import mostrar_auditoria  # 👈 Nuevo módulo agregado
from Home import main as mostrar_inicio
from utils.cargue_historial import obtener_historial

# ---- ESTILOS PERSONALIZADOS ----
st.markdown("""
    <style>
        :root {
            --color-primario: #0B2F6B;
            --color-secundario: #FDB813;
            --color-fondo: #F5F7FA;
        }
        .main {
            background: linear-gradient(180deg, var(--color-fondo) 0%, #FFFFFF 40%);
        }
        h1, h2, h3 {
            color: var(--color-primario);
        }
        .stMetricValue {
            color: var(--color-primario) !important;
        }
        .stButton button {
            background-color: var(--color-secundario);
            color: var(--color-primario);
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }
        .stButton button:hover {
            background-color: #ffcf4d;
            color: var(--color-primario);
        }
        .stRadio > label {
            color: var(--color-primario);
            font-weight: 600;
        }
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
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
st.sidebar.caption("Versión v1.4.0 – Hito 10 (Funcionalidades actualizadas)")


def _render_sidebar_historial(modulo_actual: str) -> None:
    """Renderiza el historial de cargues en el panel lateral."""

    if modulo_actual == "Cargue ARGOS":
        return  # Se muestra un panel más detallado dentro del módulo

    st.sidebar.markdown("### 🗂️ Últimos cargues")
    historial = obtener_historial()
    if not historial:
        st.sidebar.caption("Aún no se registran cargues recientes.")
        return

    for entrada in historial:
        st.sidebar.markdown(
            f"**{entrada['archivo']}**  \n"
            f"{entrada['fecha']} · {entrada['modo']} · {entrada['estado']}"
        )
        st.sidebar.markdown("---")

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

_render_sidebar_historial(modulo)
