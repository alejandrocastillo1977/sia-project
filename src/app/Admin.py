import streamlit as st
from database.db_init import create_database, DB_PATH
from database.analisis_datos import validar_datos_analiticos
import os

def mostrar_admin():
    st.title("⚙️ Administración del Sistema SIA")
    st.markdown("""
    Este módulo permite realizar tareas de mantenimiento y diagnóstico:
    - **Reiniciar completamente la base de datos (sia.db)**  
    - **Validar la calidad y cantidad de datos cargados (análisis analítico)**
    """)

    st.divider()
    st.subheader("🧹 Reinicio de la base de datos")
    st.warning("""
    Esta acción eliminará completamente la base de datos actual y la recreará desde el esquema `schema.sql`.
    **⚠️ Usa esta función con precaución.**
    """)

    # --- Confirmación de seguridad ---
    confirm_text = st.text_input("Para confirmar, escribe exactamente: BORRAR TODO", type="default")

    if st.button("🗑️ Eliminar y recrear base de datos"):
        if confirm_text.strip().upper() == "BORRAR TODO":
            try:
                if DB_PATH.exists():
                    os.remove(DB_PATH)
                    st.success("✅ Base de datos eliminada correctamente.")
                else:
                    st.info("ℹ️ No existía una base de datos previa.")
                create_database()
                st.success("🎉 Base de datos recreada correctamente desde el esquema.")
            except Exception as e:
                st.error(f"❌ Error durante el reinicio: {e}")
        else:
            st.error("Debe escribir exactamente **BORRAR TODO** para proceder con la eliminación.")

    st.divider()
    st.subheader("🔍 Validación de datos analíticos")

    if st.button("🧠 Ejecutar análisis de datos"):
        with st.spinner("Analizando información de la base de datos..."):
            try:
                resultados = validar_datos_analiticos()
                st.success("✅ Análisis completado correctamente.")
                st.json(resultados)
                st.subheader("Distribución por periodo")
                for p in resultados.get("notas_por_periodo", []):
                    st.write(f"📅 {p['id_periodo']}: {p['count']} registros | Promedio {p['mean']:.2f}")
            except Exception as e:
                st.error(f"❌ Error durante el análisis: {e}")

    st.caption("Versión del módulo: Hito 8.0 – Mantenimiento con reinicio seguro y validación analítica")
