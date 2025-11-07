import streamlit as st
from pathlib import Path
import os
from database.db_init import create_database, DB_PATH

# --- CONFIGURACIÓN: puedes cambiar a "produccion" cuando despliegues ---
MODO = "desarrollo"  # opciones: "desarrollo" o "produccion"

def mostrar_admin():
    st.title("⚙️ Panel de Mantenimiento – Base de Datos")

    st.markdown("""
    Este módulo permite **reiniciar completamente la base de datos local (`sia.db`)**.<br>
    ⚠️ **Advertencia:** esta acción eliminará todos los datos actuales
    y volverá a crear la estructura vacía a partir de `schema.sql`.
    """, unsafe_allow_html=True)

    st.divider()

    if DB_PATH.exists():
        st.info(f"📂 Base de datos actual: `{DB_PATH}`")
        st.caption(f"Última modificación: {os.path.getmtime(DB_PATH):.0f}")
    else:
        st.warning("⚠️ No se encontró la base de datos actual. Se creará una nueva si ejecutas el reinicio.")

    # --- Control de acceso según modo ---
    if MODO == "produccion":
        st.error("🚫 Este entorno está en modo PRODUCCIÓN. No se permite reiniciar la base de datos desde la interfaz.")
        return

    st.markdown("### 🧩 Reinicio de base de datos (solo modo desarrollo)")
    st.caption("Esta opción solo está disponible en entornos locales o de prueba.")

    # Confirmación explícita
    confirm_text = st.text_input("Escribe 'BORRAR TODO' para confirmar el reinicio:")

    if confirm_text.strip().upper() == "BORRAR TODO":
        if st.button("🧹 Borrar y reiniciar base de datos"):
            try:
                if DB_PATH.exists():
                    os.remove(DB_PATH)
                    st.warning("🗑️ Base de datos anterior eliminada.")

                create_database()
                st.success("✅ Base de datos recreada correctamente (estructura vacía).")
            except Exception as e:
                st.error(f"❌ Error al intentar reiniciar la base de datos: {e}")
    else:
        st.caption("✏️ Debes escribir 'BORRAR TODO' para habilitar la opción de reinicio.")
