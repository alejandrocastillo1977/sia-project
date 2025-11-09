import sys
from pathlib import Path
import streamlit as st
import sqlite3
import json

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from modules.argos_loader import cargar_y_validar_excel, procesar_argos, cargar_a_bd
from database.db_init import DB_PATH
from database.upsert import registrar_evento


def registrar_error_auditoria(nombre_archivo: str, errores: dict):
    """Registra en la tabla Auditoria los intentos fallidos de cargue ARGOS."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            descripcion_error = json.dumps(errores, ensure_ascii=False)
            accion = f"❌ Cargue fallido: {nombre_archivo} – {descripcion_error[:480]}"
            registrar_evento(conn, "coordinador_academico", accion)
    except Exception as e:
        print(f"⚠️ No se pudo registrar el evento de error: {e}")


def mostrar_cargue():
    st.title("📥 Módulo de Cargue y Validación ARGOS")
    st.markdown("""
    Permite cargar reportes ARGOS (.xlsx), validar su estructura híbrida (A–W)
    y actualizar la base de datos del Sistema de Inteligencia Académica (SIA).
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

                if df is None:
                    st.error("❌ No se puede procesar el archivo. Se detectaron errores de estructura o datos.")
                    detalle = resultados.get("detalle", resultados)
                    registrar_error_auditoria(uploaded_file.name, detalle)
                    st.warning("⚠️ Corrige el formato del archivo y vuelve a intentarlo.")
                    return

                st.success("✅ Validación estructural y de datos completada correctamente.")
                st.subheader("📋 Resumen del archivo:")
                st.json({
                    "Registros totales": resultados["total_registros"],
                    "Duplicados detectados": resultados.get("duplicados"),
                    "Columnas válidas": resultados.get("columnas_validas"),
                    "Notas válidas": resultados.get("notas_validas"),
                    "Periodos válidos": resultados.get("periodos_validos"),
                })

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
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Total registros", resumen["total"])
                    col2.metric("Nuevos", resumen["nuevos"])
                    col3.metric("Actualizados", resumen["actualizados"])
                    col4.metric("Errores", resumen["errores"])
                    col5.metric("Transferencias detectadas", resumen.get("transferencias", 0))
                    st.caption("✅ Datos cargados en la base de datos sia.db")

    else:
        st.warning("Por favor, selecciona un archivo para continuar.")
