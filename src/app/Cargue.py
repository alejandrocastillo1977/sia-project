import streamlit as st

def mostrar_cargue():
    # ---- CONFIGURACIÓN BÁSICA ----
    st.title("📥 Módulo de Cargue y Validación ARGOS")
    st.markdown(
        "Permite cargar reportes ARGOS (.xlsx), validar su estructura y actualizar la base de datos del Sistema de Inteligencia Académica (SIA)."
    )

    st.divider()

    # ---- SUBIR ARCHIVO ----
    uploaded_file = st.file_uploader(
        "Selecciona un archivo ARGOS (.xlsx):",
        type=["xlsx"],
        help="Carga el archivo descargado desde ARGOS con columnas A–W y formato de periodo YYYYPP.",
    )

    # ---- BOTÓN DE PROCESAMIENTO ----
    if uploaded_file is not None:
        st.success(f"Archivo seleccionado: {uploaded_file.name}")
        procesar = st.button("🚀 Procesar archivo")

        if procesar:
            with st.spinner("Validando y procesando archivo..."):
                # Aquí se conectará la lógica de validación (Hito 6.3)
                st.info("🔧 Procesamiento en desarrollo (Hito 6.3).")
    else:
        st.warning("Por favor, selecciona un archivo para continuar.")

    # ---- PANEL DE RESULTADOS (placeholder) ----
    st.divider()
    st.subheader("📊 Resumen de procesamiento (simulado)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total registros", "—")
    col2.metric("Nuevos", "—")
    col3.metric("Actualizados", "—")
    col4.metric("Errores", "—")

    st.caption("Los valores reales se mostrarán tras la implementación de los validadores en el Hito 6.3.")


# Permite ejecutar este módulo individualmente (solo para pruebas)
if __name__ == "__main__":
    mostrar_cargue()
