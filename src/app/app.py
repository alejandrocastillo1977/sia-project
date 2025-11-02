import streamlit as st

# ---- Configuración de página (siempre primero) ----
st.set_page_config(
    page_title="SIA – Sistema de Inteligencia Académica",
    page_icon="🎓",
    layout="wide",
)

# ---- Estilos personalizados ----
st.markdown("""
    <style>
        .main { background-color: #f4f4f9; }
        h1, h2, h3 { color: #0033A0; }
        .stMetricValue { color: #0033A0 !important; }
        .sidebar .sidebar-content { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# ---- Sidebar (único) ----
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/2/29/Logo_uniminuto.png",
    width=160
)
st.sidebar.title("📚 Módulos SIA")
modulo = st.sidebar.radio(
    "Selecciona una opción:",
    ["Inicio", "Cargue ARGOS", "Tablero general", "Consulta estudiante", "Reportes por umbral"],
    key="menu_modulos"
)
st.sidebar.markdown("---")
st.sidebar.caption("Sistema de Inteligencia Académica v0.1")

# ---- Encabezado común ----
st.title("🎓 Sistema de Inteligencia Académica – UNIMINUTO")
st.write("**Prototipo UI (Hito 5):** estructura multipágina sin conexión a datos.")

# ---- Render simple por módulo (placeholder) ----
if modulo == "Inicio":
    st.subheader("🏠 Inicio")
    st.write("Bienvenido al SIA. Usa el menú lateral para navegar por los módulos.")

elif modulo == "Cargue ARGOS":
    st.subheader("📥 Cargue y validación de archivos ARGOS")
    st.info("Aquí irá el formulario para cargar archivos .xlsx, validar columnas A–W y generar resumen.")

elif modulo == "Tablero general":
    st.subheader("📊 Tablero general del programa")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estudiantes activos", "—")
    col2.metric("Promedio institucional", "—")
    col3.metric("Avance promedio", "—")
    col4.metric("Último periodo", "—")
    st.caption("KPIs reales se conectarán en Hitos 6–8.")

elif modulo == "Consulta estudiante":
    st.subheader("👤 Consulta individual de estudiante")
    st.text_input("ID estudiante", placeholder="Ej: 373569", key="id_estudiante_input")
    st.button("Consultar", key="btn_consultar")
    st.caption("En este prototipo no hay conexión a base de datos.")

elif modulo == "Reportes por umbral":
    st.subheader("📈 Reportes por umbral de avance")
    st.slider("Umbral de avance (%)", 0, 100, 60, step=5, key="slider_umbrales")
    st.button("Generar listado", key="btn_generar_listado")
    st.caption("La exportación PDF/Excel se implementará en hitos posteriores.")
