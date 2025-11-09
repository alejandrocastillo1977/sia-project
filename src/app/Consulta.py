import sys
from pathlib import Path
import pandas as pd
import streamlit as st
from datetime import datetime
import re

# --- Ajuste de rutas base ---
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# --- Importaciones internas ---
from database.queries import buscar_estudiantes, historial_estudiante, datos_estudiante
from modules.reports import exportar_excel, exportar_pdf  # Exportes a disco

# --- Claves de estado para esta vista ---
KEY_Q = "consulta_q"
KEY_FICHA = "consulta_ficha"
KEY_HIST_DF = "consulta_hist_df"
KEY_OPCIONES = "consulta_opciones"
KEY_IDX = "consulta_idx"
KEY_ID = "consulta_id"


def _reset_state():
    """Limpia las variables temporales del estado de sesión."""
    for k in [KEY_FICHA, KEY_HIST_DF, KEY_OPCIONES, KEY_IDX, KEY_ID]:
        st.session_state.pop(k, None)


def _sanear_nombre(nombre: str) -> str:
    """Limpia espacios, acentos y caracteres especiales para usar en nombres de archivo."""
    if not nombre:
        return "sin_nombre"
    nombre_limpio = re.sub(r"[^A-Za-z0-9_]", "_", nombre.strip().title())
    return "_".join(nombre_limpio.split())


def mostrar_consulta():
    st.title("🔎 Consulta de Estudiante")
    st.write("Busca un estudiante por **ID** o **nombre** y visualiza su historial académico.")

    # Input y botón de búsqueda
    q = st.text_input("ID del estudiante o nombre:", key=KEY_Q)
    col_buscar, col_reset = st.columns([1, 1])
    buscar = col_buscar.button("Buscar", type="primary")
    limpiar = col_reset.button("Limpiar")

    if limpiar:
        _reset_state()
        st.rerun()  # Reinicia la vista

    # --- Fase de búsqueda ---
    if buscar and (q or "").strip():
        _reset_state()
        resultados = buscar_estudiantes(q.strip(), limit=50)

        if not resultados:
            st.warning("No se encontraron coincidencias.")
            return

        # Si hay más de un resultado, permitir seleccionar
        if len(resultados) > 1:
            st.info(f"Se encontraron {len(resultados)} coincidencias. Selecciona una para ver el detalle.")
            opciones = [f"{r['id_estudiante']} — {r['nombre']} ({r['programa']})" for r in resultados]
            st.session_state[KEY_OPCIONES] = resultados

            idx = st.selectbox(
                "Resultados:",
                list(range(len(opciones))),
                format_func=lambda i: opciones[i],
                key=KEY_IDX,
            )
            seleccionado = resultados[idx]
        else:
            st.session_state[KEY_OPCIONES] = resultados
            st.session_state[KEY_IDX] = 0
            seleccionado = resultados[0]

        # Persistimos la selección y los datos
        st.session_state[KEY_ID] = seleccionado["id_estudiante"]
        ficha = datos_estudiante(seleccionado["id_estudiante"]) or {}
        st.session_state[KEY_FICHA] = ficha

        hist = historial_estudiante(seleccionado["id_estudiante"]) or []
        st.session_state[KEY_HIST_DF] = pd.DataFrame(hist) if hist else pd.DataFrame()

        # Refresca la vista para mostrar exportes sin perder estado
        st.rerun()

    # --- Render a partir del estado (cuando ya hay selección previa) ---
    ficha = st.session_state.get(KEY_FICHA)
    df: pd.DataFrame = st.session_state.get(KEY_HIST_DF)

    if ficha is not None:
        st.subheader("🪪 Datos del estudiante")
        st.json(ficha)

        st.subheader("📘 Historial académico")
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)

            # --- EXPORTES INDIVIDUALES ---
            st.markdown("### 📤 Exportar historial académico")
            col1, col2 = st.columns(2)

            # Generar nombre limpio
            nombre_est = _sanear_nombre(ficha.get("nombre", "sin_nombre"))
            id_est = ficha.get("id_estudiante", "NA")

            # Botón Excel
            with col1:
                if st.button("📊 Descargar Excel", key="btn_export_excel"):
                    nombre_archivo = f"historial_{id_est}_{nombre_est}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    ruta_excel = exportar_excel(df.copy(), nombre_archivo)
                    st.success(f"✅ Archivo Excel generado: `{ruta_excel}`")

            # Botón PDF
            with col2:
                if st.button("📄 Descargar PDF", key="btn_export_pdf"):
                    datos_pdf = {
                        "Reporte": "Historial académico individual",
                        "Estudiante": ficha.get("nombre", "N/D"),
                        "ID Estudiante": id_est,
                        "Programa": ficha.get("programa", "N/D"),
                        "Total cursos": len(df),
                        "Fecha de generación": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    nombre_pdf = f"reporte_{id_est}_{nombre_est}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    ruta_pdf = exportar_pdf(datos_pdf, nombre_pdf, df)
                    st.success(f"✅ PDF generado: `{ruta_pdf}`")

        else:
            st.info("Este estudiante no tiene inscripciones registradas.")
    else:
        st.caption("Ingresa un criterio y presiona **Buscar** para iniciar la consulta.")


# --- Ejecución directa para pruebas locales ---
if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap
    bootstrap.run("app.py", "", [], {})
