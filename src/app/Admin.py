import os
import shutil
from pathlib import Path

import streamlit as st

from database.analisis_datos import validar_datos_analiticos
from database.db_init import DB_PATH, create_database


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORTS_TEMP = PROJECT_ROOT / "exports" / "temp"
BACKUPS_TEMP = PROJECT_ROOT / "backups" / "tmp"


def _limpiar_directorio_temporal(path: Path) -> int:
    """Elimina archivos y subcarpetas de un directorio temporal."""

    if not path.exists():
        return 0

    eliminados = 0
    for elemento in path.iterdir():
        try:
            if elemento.is_dir():
                shutil.rmtree(elemento)
            else:
                elemento.unlink(missing_ok=True)
            eliminados += 1
        except Exception as exc:  # pragma: no cover - solo para retroalimentación en UI
            st.warning(f"No se pudo eliminar {elemento.name}: {exc}")

    return eliminados


def mostrar_admin():
    st.title("⚙️ Administración del Sistema SIA")
    st.markdown("""
    Este módulo permite realizar tareas de mantenimiento y diagnóstico:
    - **Reiniciar completamente la base de datos (sia.db)**
    - **Validar la calidad y cantidad de datos cargados (análisis analítico)**
    - **Liberar archivos temporales generados por exportes o respaldos**
    """)

    st.divider()
    st.subheader("🧹 Reinicio de la base de datos")
    st.warning("""
    Esta acción eliminará completamente la base de datos actual y la recreará desde el esquema `schema.sql`.
    **⚠️ Usa esta función con precaución.**
    """)

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

    st.divider()
    st.subheader("🧹 Limpieza de caché y temporales")
    st.write(
        "Elimina archivos generados automáticamente en exportes o respaldos "
        "para liberar espacio y evitar inconsistencias."
    )

    if st.button("🧼 Limpiar archivos temporales"):
        EXPORTS_TEMP.mkdir(parents=True, exist_ok=True)
        BACKUPS_TEMP.mkdir(parents=True, exist_ok=True)

        eliminados = _limpiar_directorio_temporal(EXPORTS_TEMP)
        eliminados += _limpiar_directorio_temporal(BACKUPS_TEMP)

        if eliminados == 0:
            st.info("No se encontraron archivos temporales para eliminar.")
        else:
            st.success(f"🧹 Limpieza completada. Se eliminaron {eliminados} elementos temporales.")

    st.caption("Versión del módulo: Hito 10 – Funcionalidades de mantenimiento ampliadas")
    