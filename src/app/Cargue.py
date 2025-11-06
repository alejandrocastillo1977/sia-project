import sys
from pathlib import Path
import streamlit as st

# Ajustar el path base del proyecto
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from modules.argos_loader import cargar_y_validar_excel, procesar_argos, cargar_a_bd

def mostrar_cargue():
    st.title("📥 Módulo de Cargue y Validación ARGOS")
    st.markdown("""
    Permite cargar reportes ARGOS (.xlsx), validar su estructura y actualizar la base de datos del Sistema de Inteligencia Académica (SIA).
    """)

    st.divider()

    uploaded_file = st.file_uploader(
        "Selecciona un archivo ARGOS (.xlsx):",
        type=["xlsx"],
        help="Carga el archivo exportado desde ARGOS con columnas A–W y formato de periodo YYYYPP."
    )

    if uploaded_file is not None:
        st.success(f"Archivo seleccionado: {uploaded_file.name}")

        modo = st.radio(
            "Selecciona el modo de ejecución:",
            ["Simulación (sin escritura)", "Cargue real a la base de datos"]
        )

        procesar = st.button("🚀 Procesar archivo")

        if procesar:
            with st.spinner("Validando y procesando archivo..."):
                df, resultados = cargar_y_validar_excel(uploaded_file)

                if df is not None:
                    st.success("✅ Validación completada correctamente.")
                    st.subheader("📋 Resultados de la validación:")
                    st.json(resultados)

                    if modo == "Simulación (sin escritura)":
                        st.subheader("⚙️ Procesamiento simulado")
                        resumen = procesar_argos(df)
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total registros", resumen["total"])
                        col2.metric("Nuevos", resumen["nuevos"])
                        col3.metric("Actualizados", resumen["actualizados"])
                        col4.metric("Errores", resumen["errores"])
                        st.caption("🧪 Modo simulado – sin escritura en la base de datos.")

                    elif modo == "Cargue real a la base de datos":
                        st.subheader("💾 Cargue real a la base de datos")
                        resumen = cargar_a_bd(df)
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total registros", resumen["total"])
                        col2.metric("Nuevos", resumen["nuevos"])
                        col3.metric("Actualizados", resumen["actualizados"])
                        col4.metric("Errores", resumen["errores"])
                        st.caption("✅ Datos cargados en la base de datos sia.db")

                else:
                    st.error("❌ Error en la validación del archivo ARGOS.")
                    st.json(resultados)
    else:
        st.warning("Por favor, selecciona un archivo para continuar.")
