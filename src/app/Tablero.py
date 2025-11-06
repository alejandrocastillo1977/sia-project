import sys
from pathlib import Path

# Asegurar que 'src' esté en sys.path para imports relativos
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
from database.queries import obtener_kpis_programa, listar_estudiantes


def mostrar_tablero():
    st.title("📊 Tablero General del Programa")
    st.write(
        "Este tablero muestra los indicadores clave de desempeño académico (KPIs) y el listado de estudiantes activos en el Sistema de Inteligencia Académica (SIA)."
    )

    # KPIs
    kpis = obtener_kpis_programa()
    st.subheader("🎯 Indicadores globales del programa")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de estudiantes", f"{kpis['total_estudiantes']}")
    prom_txt = f"{kpis['promedio_general']}" if kpis["promedio_general"] is not None else "—"
    c2.metric("Promedio general", prom_txt)
    c3.metric("Cursos registrados", f"{kpis['total_cursos']}")
    c4.metric("Inscripciones", f"{kpis['total_inscripciones']}")

    st.divider()

    # Listado de estudiantes
    st.subheader("👩‍🎓 Listado de estudiantes registrados")
    limite = st.slider("Límite de filas a mostrar:", min_value=50, max_value=1000, value=200, step=50)
    data = listar_estudiantes(limit=limite)

    if data:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("No hay estudiantes registrados para mostrar en este momento.")


if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap
    bootstrap.run("app.py", "", [], {})
