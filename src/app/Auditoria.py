import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from database.queries import listar_eventos_auditoria
from database.db_init import DB_PATH

# ==============================================================
# 🔒 CONFIGURACIÓN GENERAL
# ==============================================================

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


def exportar_auditoria_csv():
    """
    Crea una copia de seguridad (snapshot) de la tabla Auditoria en formato CSV.
    El archivo se guarda dentro de la carpeta /backups con marca de tiempo.
    """
    try:
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = BACKUP_DIR / f"auditoria_snapshot_{fecha}.csv"

        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("SELECT * FROM Auditoria ORDER BY fecha_evento DESC;", conn)
            if not df.empty:
                df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
                return str(ruta_salida)
            else:
                return None
    except Exception as e:
        print(f"⚠️ Error al generar backup de auditoría: {e}")
        return None


# ==============================================================
# 🧾 INTERFAZ PRINCIPAL
# ==============================================================

def mostrar_auditoria():
    st.title("🧾 Auditoría del Sistema SIA")
    st.markdown("""
    Este módulo muestra todos los eventos registrados en el sistema, incluyendo:
    - Cargues exitosos o fallidos de archivos ARGOS.
    - Reinicios de base de datos y validaciones.
    - Acciones administrativas y de diagnóstico.
    """)

    # --- Crear backup automático al abrir el módulo ---
    with st.spinner("Generando copia de respaldo de la auditoría..."):
        ruta_backup = exportar_auditoria_csv()

    if ruta_backup:
        st.success(f"💾 Copia de seguridad creada: `{ruta_backup}`")
    else:
        st.info("ℹ️ No se generó copia (la tabla Auditoria está vacía).")

    st.divider()

    # --- Filtros de búsqueda ---
    col1, col2 = st.columns([3, 1])
    filtro = col1.text_input("🔍 Buscar por palabra clave (ej: fallido, ARGOS, coordinador):", "")
    limite = col2.number_input("Número de registros a mostrar:", min_value=10, max_value=500, value=100, step=10)

    with st.spinner("Cargando eventos de auditoría..."):
        eventos = listar_eventos_auditoria(limit=limite, filtro=filtro.strip() or None)

    if not eventos:
        st.info("No se encontraron eventos en la auditoría con los filtros actuales.")
        return

    df = pd.DataFrame(eventos)
    df["fecha_evento"] = pd.to_datetime(df["fecha_evento"], errors="coerce")

    st.metric("Eventos totales cargados", len(df))
    st.dataframe(df, use_container_width=True)

    # --- Detalle de evento individual ---
    st.divider()
    seleccion = st.selectbox("Selecciona un evento para ver detalle:", df["id_evento"].astype(str))
    evento_sel = df[df["id_evento"].astype(str) == seleccion].iloc[0]

    st.subheader(f"🧩 Detalle del evento #{evento_sel['id_evento']}")
    st.write(f"**Usuario:** {evento_sel['usuario']}")
    st.write(f"**Fecha:** {evento_sel['fecha_evento']}")
    st.code(evento_sel["accion"], language="json")

    st.caption("💾 Los eventos se registran automáticamente en cada operación crítica del sistema.")
    st.caption("🗂️ Además, se genera un respaldo CSV de la tabla Auditoria cada vez que se abre este módulo.")
