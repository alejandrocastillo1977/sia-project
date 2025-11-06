import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from database.queries import buscar_estudiantes, historial_estudiante, datos_estudiante


def mostrar_consulta():
    st.title("🔎 Consulta de Estudiante")
    st.write("Busca un estudiante por **ID** o por **nombre** y visualiza su historial académico.")

    q = st.text_input("ID del estudiante o nombre:")
    btn = st.button("Buscar")

    if btn and q.strip():
        resultados = buscar_estudiantes(q.strip(), limit=50)

        if not resultados:
            st.warning("No se encontraron coincidencias.")
            return

        # Si hay más de uno, permitir seleccionar
        if len(resultados) > 1:
            st.info(f"Se encontraron {len(resultados)} coincidencias. Selecciona una para ver el detalle.")
            opciones = [f"{r['id_estudiante']} — {r['nombre']} ({r['programa']})" for r in resultados]
            idx = st.selectbox("Resultados:", list(range(len(opciones))), format_func=lambda i: opciones[i])
            seleccionado = resultados[idx]
        else:
            seleccionado = resultados[0]

        st.subheader("🪪 Datos del estudiante")
        ficha = datos_estudiante(seleccionado["id_estudiante"])
        st.json(ficha)

        st.subheader("📘 Historial académico")
        hist = historial_estudiante(seleccionado["id_estudiante"])
        if hist:
            st.dataframe(hist, use_container_width=True, hide_index=True)
        else:
            st.info("Este estudiante no tiene inscripciones registradas.")


if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap
    bootstrap.run("app.py", "", [], {})
