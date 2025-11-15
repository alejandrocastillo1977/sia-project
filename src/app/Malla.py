import sys
from pathlib import Path

import streamlit as st

# Asegurar que 'src' esté en sys.path para imports internos
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from database.queries import buscar_estudiantes, historial_estudiante, datos_estudiante
from modules.load_data import mapear_malla_con_historico, obtener_malla_isov_virtual


def mostrar_malla():
    st.title("🗺️ Malla Curricular – Ingeniería de Software (Virtual)")
    st.markdown(
        """
        Esta vista cruza la **malla oficial** del programa con el **histórico académico**
        del estudiante:

        - APROBADO: nota final ≥ 3.0.
        - PERDIDO: nota final < 3.0.
        - TRANSFERENCIA: cursos registrados con NRC simbólico `TRANSF-*`.
        - PENDIENTE: cursos de la malla que aún no aparecen en el histórico.
        """
    )

    st.divider()

    q = st.text_input("ID del estudiante o nombre:")
    col_buscar, col_reset = st.columns([1, 1])
    buscar = col_buscar.button("Buscar", type="primary")
    limpiar = col_reset.button("Limpiar")

    if limpiar:
        st.session_state.pop("malla_sel_est", None)
        st.session_state.pop("malla_sel_hist", None)
        st.session_state.pop("malla_sel_malla", None)
        st.rerun()

    if buscar and (q or "").strip():
        resultados = buscar_estudiantes(q.strip(), limit=50)

        if not resultados:
            st.warning("No se encontraron coincidencias.")
            return

        if len(resultados) > 1:
            st.info("Se encontraron varias coincidencias. Selecciona una:")
            opciones = [
                f"{r['id_estudiante']} — {r['nombre']} ({r['programa']})"
                for r in resultados
            ]
            idx = st.selectbox(
                "Resultados:",
                list(range(len(opciones))),
                format_func=lambda i: opciones[i],
                key="malla_sel_idx",
            )
            seleccionado = resultados[idx]
        else:
            seleccionado = resultados[0]

        ficha = datos_estudiante(seleccionado["id_estudiante"]) or {}
        hist = historial_estudiante(seleccionado["id_estudiante"]) or []
        malla = obtener_malla_isov_virtual()
        cruce = mapear_malla_con_historico(hist, malla)

        st.session_state["malla_sel_est"] = ficha
        st.session_state["malla_sel_hist"] = hist
        st.session_state["malla_sel_malla"] = cruce
        st.rerun()

    ficha = st.session_state.get("malla_sel_est")
    cruce = st.session_state.get("malla_sel_malla")

    if not ficha or not cruce:
        st.caption(
            "Ingresa un criterio y presiona **Buscar** para generar el reporte de malla."
        )
        return

    st.subheader("🪪 Datos del estudiante")
    st.json(ficha)

    st.subheader("📚 Malla curricular por cuatrimestre")

    estado_color = {
        "APROBADO": "#C8E6C9",      # verde suave
        "PERDIDO": "#FFCDD2",       # rojo suave
        "TRANSFERENCIA": "#BBDEFB", # azul suave
        "PENDIENTE": "#F5F5F5",     # gris claro
    }

    for bloque in cruce:
        cuat = bloque["cuatrimestre"]
        cursos = bloque["cursos"]

        st.markdown(f"### 📦 Cuatrimestre {cuat}")

        for curso in cursos:
            bg = estado_color.get(curso["estado"], "#FFFFFF")
            nota = curso["nota"]
            nota_txt = "—" if nota is None else f"{float(nota):.1f}"
            periodo_txt = curso["id_periodo"] or "—"

            st.markdown(
                f"<div style='background-color:{bg}; padding:8px; border-radius:6px; margin-bottom:4px;'>"
                f"<strong>{curso['codigo']}</strong> – {curso['nombre']} "
                f"<br/>Créditos: {curso['creditos']} | Estado: <strong>{curso['estado']}</strong> "
                f"| Nota: {nota_txt} | Periodo: {periodo_txt}"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")


if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap

    bootstrap.run("app.py", "", [], {})