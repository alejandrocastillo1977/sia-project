import sys
import sqlite3
import json
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from modules.argos_loader import cargar_y_validar_excel, procesar_argos, cargar_a_bd
from database.db_init import DB_PATH
from database.upsert import registrar_evento
from utils.cargue_historial import obtener_historial, registrar_cargue


MODO_SIMULADO = "Simulación (sin escritura)"
MODO_REAL = "Cargue real a la base de datos"


def _obtener_tamano_mb(uploaded_file) -> float:
    """Obtiene el tamaño del archivo cargado en megabytes."""

    size = getattr(uploaded_file, "size", None)
    if size is None:
        contenido = uploaded_file.getvalue()
        size = len(contenido)
        uploaded_file.seek(0)
    return round(size / (1024 ** 2), 2)


def _estimar_tiempo_procesamiento(mb: float) -> float:
    """Calcula un tiempo estimado (en segundos) del procesamiento."""

    velocidad_aproximada = 1.8  # MB/s estimados para validaciones en local
    base_segundos = 4.0  # Tiempo base de inicialización
    return max(base_segundos, base_segundos + (mb / max(velocidad_aproximada, 0.1)))


def _render_historial_sidebar() -> None:
    """Muestra los últimos cargues registrados en el panel lateral."""

    historial = obtener_historial()
    with st.sidebar.expander("🗂️ Últimos cargues ARGOS", expanded=True):
        if not historial:
            st.caption("Aún no se registran cargues en esta instancia.")
            return

        for entrada in historial:
            st.markdown(
                f"**{entrada['archivo']}**\n"
                f"- Fecha: {entrada['fecha']}\n"
                f"- Modo: {entrada['modo']}\n"
                f"- Estado: {entrada['estado']}"
            )
            st.markdown("---")


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

    _render_historial_sidebar()

    uploaded_file = st.file_uploader(
        "Selecciona un archivo ARGOS (.xlsx):",
        type=["xlsx"],
        help="Carga el archivo exportado desde ARGOS con columnas A–W y formato de periodo YYYYPP.",
    )

    if uploaded_file is not None:
        st.success(f"Archivo seleccionado: {uploaded_file.name}")
        st.toast(f"📂 `{uploaded_file.name}` listo para validación.")

        tamano_mb = _obtener_tamano_mb(uploaded_file)
        tiempo_estimado = _estimar_tiempo_procesamiento(tamano_mb)
        st.info(
            f"⏱️ Tiempo estimado de procesamiento: {tiempo_estimado:.1f} segundos "
            f"para {tamano_mb:.2f} MB."
        )

        modo = st.radio(
            "Selecciona el modo de ejecución:",
            [MODO_SIMULADO, MODO_REAL]
        )

        procesar = st.button("🚀 Procesar archivo")

        if procesar:
            modo_resumido = "Simulación" if modo == MODO_SIMULADO else "Carga real"
            progreso = st.progress(5, text="Inicializando validación...")
            paso_texto = st.empty()

            with st.spinner("Validando y procesando archivo..."):
                paso_texto.info("🔍 Validando estructura y datos del archivo...")
                df, resultados = cargar_y_validar_excel(uploaded_file)
                progreso.progress(35, text="Validación completada")

                if df is None:
                    progreso.progress(100, text="Proceso finalizado con errores")
                    st.error("❌ No se puede procesar el archivo. Se detectaron errores de estructura o datos.")
                    detalle = resultados.get("detalle", resultados)
                    registrar_error_auditoria(uploaded_file.name, detalle)
                    registrar_cargue(uploaded_file.name, modo_resumido, "Error en validación")
                    st.toast("❌ Error durante la validación del archivo.")
                    st.warning("⚠️ Corrige el formato del archivo y vuelve a intentarlo.")
                    return

                paso_texto.success("✅ Validación estructural exitosa. Preparando resumen...")
                st.subheader("📋 Resumen del archivo:")
                st.json({
                    "Registros totales": resultados["total_registros"],
                    "Duplicados detectados": resultados.get("duplicados"),
                    "Columnas válidas": resultados.get("columnas_validas"),
                    "Notas válidas": resultados.get("notas_validas"),
                    "Periodos válidos": resultados.get("periodos_validos"),
                })

                progreso.progress(55, text="Analizando registros")

                if modo == MODO_SIMULADO:
                    st.subheader("⚙️ Procesamiento simulado")
                    resumen = procesar_argos(df)
                    progreso.progress(80, text="Simulación completada")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total registros", resumen["total"])
                    col2.metric("Nuevos", resumen["nuevos"])
                    col3.metric("Actualizados", resumen["actualizados"])
                    col4.metric("Errores", resumen["errores"])
                    st.caption("🧪 Modo simulado – sin escritura en la base de datos.")
                    registrar_cargue(uploaded_file.name, modo_resumido, "Éxito")
                    st.toast("✅ Simulación completada correctamente.")

                elif modo == MODO_REAL:
                    st.subheader("💾 Cargue real a la base de datos")
                    resumen = cargar_a_bd(df)
                    progreso.progress(85, text="Escritura en base de datos finalizada")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Total registros", resumen["total"])
                    col2.metric("Nuevos", resumen["nuevos"])
                    col3.metric("Actualizados", resumen["actualizados"])
                    col4.metric("Errores", resumen["errores"])
                    col5.metric("Transferencias detectadas", resumen.get("transferencias", 0))
                    st.caption("✅ Datos cargados en la base de datos sia.db")
                    registrar_cargue(uploaded_file.name, modo_resumido, "Éxito")
                    st.toast("🎉 Cargue real completado correctamente.")

                progreso.progress(100, text="Proceso completado")
                paso_texto.empty()

    else:
        st.warning("Por favor, selecciona un archivo para continuar.")
        