import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

# Asegurar que 'src' esté en sys.path para imports internos
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from database.queries import buscar_estudiantes, historial_estudiante, datos_estudiante
from modules.load_data import mapear_malla_con_historico, obtener_malla_isov_virtual
from modules.reports import exportar_excel_malla, exportar_pdf_malla


def _resumen_creditos(malla_cruzada: list[dict]) -> dict:
    """Calcula créditos por estado a partir de la malla cruzada."""
    resumen = {"APROBADO": 0, "PERDIDO": 0, "TRANSFERENCIA": 0, "PENDIENTE": 0}
    for bloque in malla_cruzada:
        for curso in bloque.get("cursos", []):
            estado = str(curso.get("estado", "")).upper()
            creditos = int(curso.get("creditos") or 0)
            if estado in resumen:
                resumen[estado] += creditos
    return resumen


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

    # --- Resumen de créditos por estado (para encabezados y PDF) ---
    resumen_creditos = _resumen_creditos(cruce)
    total_creditos = sum(resumen_creditos.values())

    # Cred/aprob/transf = APR + TRANSF
    cred_aprob_transf = resumen_creditos["APROBADO"] + resumen_creditos["TRANSFERENCIA"]
    # Créditos pendientes = PEND, Créditos perdidos = PER
    cred_pend = resumen_creditos["PENDIENTE"]
    cred_perd = resumen_creditos["PERDIDO"]

    # Porc/aproba_malla = (Cred/aprob/transf * 100) / Créditos totales malla
    porc_aproba = (
        (cred_aprob_transf * 100.0 / total_creditos) if total_creditos > 0 else 0.0
    )
    # Porc/pendie_malla = 100% - Porc/aproba_malla
    porc_pendie = 100.0 - porc_aproba if total_creditos > 0 else 0.0

    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("Cred/aprob/transf", cred_aprob_transf)
    col_res2.metric("Créditos pendientes", cred_pend)
    col_res3.metric("Créditos perdidos", cred_perd)
    col_res4.metric("Porc/aproba_malla", f"{porc_aproba:.1f} %")

    # Segunda fila para mostrar Porc/pendie_malla de forma clara
    col_pendie, _, _, _ = st.columns(4)
    col_pendie.metric("Porc/pendie_malla", f"{porc_pendie:.1f} %")

    # --- Detalle por cuatrimestre ---
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

    # --- Exportes de malla ---
    st.subheader("📤 Exportar malla curricular")

    col_xlsx, col_pdf = st.columns(2)

    nombre_est = ficha.get("nombre", "sin_nombre").strip().replace(" ", "_")
    id_est = ficha.get("id_estudiante", "NA")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with col_xlsx:
        if st.button("📊 Descargar Excel de malla", key="btn_malla_excel"):
            nombre_archivo = f"malla_{id_est}_{nombre_est}_{timestamp}.xlsx"
            ruta_excel = exportar_excel_malla(cruce, nombre_archivo)
            st.success(f"✅ Archivo Excel de malla generado: `{ruta_excel}`")

    with col_pdf:
        if st.button("📄 Descargar PDF de malla", key="btn_malla_pdf"):
            datos_pdf = {
                "Reporte": "Malla curricular cruzada",
                "Estudiante": ficha.get("nombre", "N/D"),
                "ID Estudiante": id_est,
                "Programa": ficha.get("programa", "N/D"),
                "Créditos totales malla": total_creditos,
                "Cred/aprob/transf": cred_aprob_transf,
                "Créditos pendientes": cred_pend,
                "Créditos perdidos": cred_perd,
                "Porc/aproba_malla": f"{porc_aproba:.1f} %",
                "Porc/pendie_malla": f"{porc_pendie:.1f} %",
            }
            nombre_pdf = f"malla_{id_est}_{nombre_est}_{timestamp}.pdf"
            ruta_pdf = exportar_pdf_malla(datos_pdf, cruce, nombre_pdf)
            st.success(f"✅ PDF de malla generado: `{ruta_pdf}`")


if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap

    bootstrap.run("app.py", "", [], {})