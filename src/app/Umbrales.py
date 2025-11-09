import streamlit as st
import plotly.express as px
import pandas as pd

from database.queries import listar_periodos, obtener_notas_por_umbral

def mostrar_umbrales():
    st.title("📈 Reporte de Umbrales de Desempeño Académico")

    st.markdown("""
    Este módulo permite identificar estudiantes **en riesgo** o **destacados** según su nota promedio por curso y periodo.
    """)

    # --- Filtros principales ---
    periodos = listar_periodos()
    if not periodos:
        st.warning("⚠️ No hay periodos académicos registrados en la base de datos.")
        return

    col1, col2, col3 = st.columns(3)
    periodo_sel = col1.selectbox("📅 Periodo académico", periodos)
    tipo = col2.radio("Tipo de umbral", ["🔻 En riesgo (< 3.0)", "🌟 Destacados (≥ 4.5)"])
    umbral = 3.0 if "riesgo" in tipo.lower() else 4.5

    # --- Consultar datos ---
    datos = obtener_notas_por_umbral("bajo" if "riesgo" in tipo.lower() else "alto", periodo_sel, umbral)

    if not datos:
        st.info("No se encontraron registros con esas condiciones.")
        return

    df = pd.DataFrame(datos)

    # --- Métricas generales ---
    st.subheader("📊 Métricas del grupo seleccionado")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total estudiantes", df["id_estudiante"].nunique())
    col2.metric("Total registros", len(df))
    col3.metric("Promedio de nota", round(df["nota"].mean(), 2))

    # --- Tabla detallada ---
    st.subheader("👩‍🎓 Detalle de registros")
    st.dataframe(df[["id_estudiante", "nombre", "programa", "id_curso", "nombre_curso", "nota", "version_periodo"]], use_container_width=True)

    # --- Gráfico de distribución ---
    st.subheader("📉 Distribución de notas")
    fig = px.histogram(df, x="nota", nbins=20, color_discrete_sequence=["#0033A0"], title="Distribución de notas en el grupo seleccionado")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Versión del módulo: Hito 8.2 – Umbrales de Desempeño")
