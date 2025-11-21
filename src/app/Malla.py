import sys
import json
from pathlib import Path
from datetime import datetime

import streamlit as st

# Asegurar que 'src' esté en sys.path para imports internos
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from database.queries import buscar_estudiantes, historial_estudiante, datos_estudiante
from modules.load_data import (
    mapear_malla_con_historico,
    obtener_malla_isov_virtual,
    validar_y_normalizar_malla,
)
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
    MALLA_CFG_KEY = "malla_cfg_activa"
    MALLA_RESUMEN_KEY = "malla_resumen_info"
    MALLA_EST_KEY = "malla_sel_est"
    MALLA_HIST_KEY = "malla_sel_hist"
    MALLA_CRUCE_KEY = "malla_sel_malla"
    MALLA_PROG_HIST_KEY = "malla_sel_programas_hist"

    st.title("🗺️ Malla Curricular – Reporte cruzado por programa")
    st.markdown(
        """
        Esta vista cruza una **malla curricular seleccionada** con el **histórico académico**
        del estudiante:

        - APROBADO: nota final ≥ 3.0.
        - PERDIDO: nota final < 3.0.
        - TRANSFERENCIA: cursos registrados con NRC simbólico `TRANSF-*`.
        - PENDIENTE: cursos de la malla que aún no aparecen en el histórico.

        Primero selecciona o carga la **malla curricular** y luego busca al estudiante.
        """
    )

    st.divider()

    # -------------------------------------------------
    # 1️⃣ Selección / carga de malla curricular
    # -------------------------------------------------
    st.subheader("1️⃣ Selección de malla curricular")

    malla_cfg = st.session_state.get(MALLA_CFG_KEY)
    malla_resumen = st.session_state.get(MALLA_RESUMEN_KEY)

    origen = st.radio(
        "Origen de la malla a utilizar:",
        ["Malla por defecto (ISOF)", "Cargar malla desde archivo JSON"],
        key="malla_origen",
    )

    # Malla por defecto (ISOF)
    if origen == "Malla por defecto (ISOF)":
        if st.button(
            "Usar malla por defecto – Ingeniería de Software (ISOF)",
            key="btn_malla_defecto",
        ):
            base = obtener_malla_isov_virtual()
            try:
                malla_norm = validar_y_normalizar_malla(base)
            except Exception as e:  # pragma: no cover - solo mensaje en UI
                st.error(f"Error al preparar la malla por defecto: {e}")
            else:
                plan = malla_norm.get("plan") or []
                total_cuat = len(plan)
                total_cursos = sum(len(b.get("cursos", [])) for b in plan)

                st.session_state[MALLA_CFG_KEY] = malla_norm
                st.session_state[MALLA_RESUMEN_KEY] = {
                    "codigo_programa": malla_norm["codigo_programa"],
                    "nombre_malla": malla_norm["nombre_malla"],
                    "creditos_totales": malla_norm.get("creditos_totales", 0),
                    "cuatrimestres": total_cuat,
                    "total_cursos": total_cursos,
                }
                malla_cfg = malla_norm
                malla_resumen = st.session_state[MALLA_RESUMEN_KEY]
                st.success(
                    f"Malla por defecto '{malla_norm['nombre_malla']}' "
                    f"para programa {malla_norm['codigo_programa']} lista para usar."
                )

    # Malla desde JSON
    else:
        archivo_json = st.file_uploader(
            "Cargar archivo JSON de malla curricular",
            type=["json"],
            key="malla_json",
            help="Debe contener 'codigo_programa', 'nombre_malla', 'creditos_totales' y 'plan'.",
        )
        if archivo_json is not None and st.button(
            "Validar y usar malla JSON", key="btn_validar_malla_json"
        ):
            try:
                data = json.load(archivo_json)
                malla_norm = validar_y_normalizar_malla(data)
            except Exception as e:  # pragma: no cover - solo mensaje en UI
                st.error(f"No se pudo validar la malla: {e}")
                st.session_state.pop(MALLA_CFG_KEY, None)
                st.session_state.pop(MALLA_RESUMEN_KEY, None)
                malla_cfg = None
                malla_resumen = None
            else:
                plan = malla_norm.get("plan") or []
                total_cuat = len(plan)
                total_cursos = sum(len(b.get("cursos", [])) for b in plan)

                st.session_state[MALLA_CFG_KEY] = malla_norm
                st.session_state[MALLA_RESUMEN_KEY] = {
                    "codigo_programa": malla_norm["codigo_programa"],
                    "nombre_malla": malla_norm["nombre_malla"],
                    "creditos_totales": malla_norm.get("creditos_totales", 0),
                    "cuatrimestres": total_cuat,
                    "total_cursos": total_cursos,
                }
                malla_cfg = malla_norm
                malla_resumen = st.session_state[MALLA_RESUMEN_KEY]
                st.success(
                    f"Malla '{malla_norm['nombre_malla']}' para programa "
                    f"{malla_norm['codigo_programa']} lista para usar."
                )

    if malla_cfg and malla_resumen:
        with st.expander("📋 Malla seleccionada", expanded=True):
            st.write(f"**Programa (código):** {malla_resumen['codigo_programa']}")
            st.write(f"**Nombre de la malla:** {malla_resumen['nombre_malla']}")
            st.write(f"**Créditos totales:** {malla_resumen['creditos_totales']}")
            st.write(f"**Cuatrimestres:** {malla_resumen['cuatrimestres']}")
            st.write(f"**Cursos en la malla:** {malla_resumen['total_cursos']}")
    else:
        st.info("Selecciona o carga una malla curricular válida para continuar.")

    st.divider()
    st.subheader("2️⃣ Búsqueda de estudiante y cruce de malla")

    if not malla_cfg:
        st.caption("Selecciona primero una malla curricular válida para habilitar la búsqueda.")
        return

    # -------------------------------------------------
    # Búsqueda de estudiante
    # -------------------------------------------------
    q = st.text_input("ID del estudiante o nombre:")
    col_buscar, col_reset = st.columns([1, 1])
    buscar = col_buscar.button("Buscar", type="primary")
    limpiar = col_reset.button("Limpiar")

    if limpiar:
        for key in (
            MALLA_EST_KEY,
            MALLA_HIST_KEY,
            MALLA_CRUCE_KEY,
            "malla_sel_idx",
            MALLA_PROG_HIST_KEY,
        ):
            st.session_state.pop(key, None)
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

        if not hist:
            st.info("Este estudiante no tiene inscripciones registradas.")
            st.session_state[MALLA_EST_KEY] = ficha
            st.session_state[MALLA_HIST_KEY] = hist
            st.session_state[MALLA_CRUCE_KEY] = None
            st.session_state[MALLA_PROG_HIST_KEY] = []
        else:
            programas_hist = sorted(
                {
                    str(reg.get("codigo_programa") or "").upper()
                    for reg in hist
                    if reg.get("codigo_programa")
                }
            )
            st.session_state[MALLA_PROG_HIST_KEY] = programas_hist

            cod_malla = str(malla_cfg.get("codigo_programa", "")).upper()
            if not cod_malla or cod_malla not in programas_hist:
                lista_prog = ", ".join(programas_hist) if programas_hist else "Ninguno"
                st.warning(
                    "El estudiante no tiene inscripciones en el programa de la malla seleccionada "
                    f"({cod_malla or 'N/D'}). "
                    f"Programas en su histórico: {lista_prog}."
                )
                st.session_state[MALLA_EST_KEY] = ficha
                st.session_state[MALLA_HIST_KEY] = hist
                st.session_state[MALLA_CRUCE_KEY] = None
            else:
                cruce = mapear_malla_con_historico(hist, malla_cfg)
                st.session_state[MALLA_EST_KEY] = ficha
                st.session_state[MALLA_HIST_KEY] = hist
                st.session_state[MALLA_CRUCE_KEY] = cruce

    ficha = st.session_state.get(MALLA_EST_KEY)
    cruce = st.session_state.get(MALLA_CRUCE_KEY)
    programas_hist = st.session_state.get(MALLA_PROG_HIST_KEY) or []
    malla_cfg = st.session_state.get(MALLA_CFG_KEY) or malla_cfg
    malla_resumen = st.session_state.get(MALLA_RESUMEN_KEY) or malla_resumen

    if not ficha:
        st.caption(
            "Selecciona o carga una malla, luego ingresa un criterio y presiona **Buscar** "
            "para generar el reporte de malla."
        )
        return

    st.subheader("🪪 Datos del estudiante")
    st.json(ficha)
    if programas_hist:
        st.caption(
            "Programas en el histórico del estudiante: " + ", ".join(programas_hist)
        )

    if not cruce:
        st.info(
            "No se puede generar la malla para este estudiante con la malla seleccionada. "
            "Verifica que pertenezca al programa correspondiente."
        )
        return

    st.subheader("📚 Malla curricular por cuatrimestre")

    estado_color = {
        "APROBADO": "#C8E6C9",  # verde suave
        "PERDIDO": "#FFCDD2",  # rojo suave
        "TRANSFERENCIA": "#BBDEFB",  # azul suave
        "PENDIENTE": "#F5F5F5",  # gris claro
    }

    # --- Resumen de créditos por estado (para encabezados y PDF) ---
    resumen_creditos = _resumen_creditos(cruce)
    total_creditos_malla = int(
        malla_resumen.get("creditos_totales", 0) if malla_resumen else 0
    )
    if total_creditos_malla <= 0:
        total_creditos_malla = sum(resumen_creditos.values())

    # Cred/aprob/transf = APR + TRANSF
    cred_aprob_transf = resumen_creditos["APROBADO"] + resumen_creditos["TRANSFERENCIA"]
    # Créditos pendientes = PEND, Créditos perdidos = PER
    cred_pend = resumen_creditos["PENDIENTE"]
    cred_perd = resumen_creditos["PERDIDO"]

    # Porc/aproba_malla = (Cred/aprob/transf * 100) / Créditos totales malla
    porc_aproba = (
        (cred_aprob_transf * 100.0 / total_creditos_malla)
        if total_creditos_malla > 0
        else 0.0
    )
    # Porc/pendie_malla = 100% - Porc/aproba_malla
    porc_pendie = 100.0 - porc_aproba if total_creditos_malla > 0 else 0.0

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
            programas_txt = ", ".join(programas_hist) if programas_hist else "N/D"
            programa_malla_texto = (
                (malla_cfg.get("programa") or "").strip()
                or (malla_cfg.get("nombre_malla") or "").strip()
                or malla_cfg.get("codigo_programa", "N/D")
            )
            datos_pdf = {
                "Reporte": "Malla curricular cruzada",
                "Estudiante": ficha.get("nombre", "N/D"),
                "ID Estudiante": id_est,
                "Programa": f"{programa_malla_texto} (histórico: {programas_txt})",
                "Créditos totales malla": total_creditos_malla,
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