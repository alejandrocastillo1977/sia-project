import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

# Asegurar que 'src' esté en sys.path para imports internos
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from database.queries import buscar_estudiantes, historial_estudiante, datos_estudiante
from modules.load_data import mapear_malla_con_historico
from modules.mallas_catalogo import (
    listar_mallas_disponibles,
    obtener_malla_por_id,
)
from modules.mallas_loader import simular_malla_desde_bytes, registrar_malla
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


def _programas_desde_historial(hist: list[dict], programa_ficha: str | None) -> str:
    """
    Construye una cadena 'prog1, prog2, ...' con todos los programas
    en los que ha estado el estudiante, dejando de último el programa
    asociado al periodo más reciente.

    Intenta primero usar la descripción larga del programa si está presente,
    y como respaldo usa el código.
    """
    if hist is None:
        hist = []

    prog_max_periodo: dict[str, str] = {}

    for reg in hist:
        # Preferimos descripción; si no existe, usamos el código
        prog = (
            reg.get("descripcion_programa")
            or reg.get("DESCRIPCION_PROGRAMA")
            or reg.get("programa")
            or ""
        )
        prog = str(prog).strip()
        if not prog:
            continue

        id_per = str(reg.get("id_periodo", "")).strip()
        actual = prog_max_periodo.get(prog)
        if actual is None or id_per > actual:
            prog_max_periodo[prog] = id_per

    # Incluir el programa de la ficha si no aparece en el histórico
    if programa_ficha:
        prog_f = str(programa_ficha).strip()
        if prog_f and prog_f not in prog_max_periodo:
            prog_max_periodo[prog_f] = ""

    if not prog_max_periodo:
        return "N/D"

    # Ordenar por último periodo (ascendente): el más reciente queda de último
    programas_ordenados = sorted(prog_max_periodo.items(), key=lambda kv: kv[1])
    lista = [p for p, _ in programas_ordenados]
    return ", ".join(lista)


def _elegir_malla() -> tuple[str, dict]:
    """
    Presenta un selectbox para elegir la malla y devuelve:
    (id_malla_seleccionada, dict_malla)
    """
    mallas_idx = listar_mallas_disponibles()

    opciones = []
    ids = []

    # Opción embebida
    opciones.append("Malla embebida – Ing. de Software Virtual")
    ids.append("embebida_isov_virtual")

    # Opciones desde índice
    for meta in mallas_idx:
        opciones.append(meta.nombre)
        ids.append(meta.id)

    seleccion = st.selectbox(
        "Malla curricular:",
        options=list(range(len(opciones))),
        format_func=lambda i: opciones[i],
        key="malla_sel_catalogo",
    )

    id_malla = ids[seleccion]
    malla = obtener_malla_por_id(id_malla) or {}

    return id_malla, malla


def _seccion_admin_mallas():
    """
    UI para cargar nuevas mallas JSON:
    - Simulación / validación.
    - Registro definitivo si la estructura es válida.
    """
    st.subheader("⚙️ Administrar mallas curriculares")

    with st.expander("Cargar nueva malla (modo avanzado)", expanded=False):
        archivo = st.file_uploader(
            "Archivo JSON de malla",
            type=["json"],
            key="uploader_malla_json",
        )

        col_id, col_nombre = st.columns(2)
        id_malla = col_id.text_input(
            "Identificador interno de la malla (sin espacios)",
            help="Ejemplo: isis_virtual, indus_presencial, etc.",
        )
        nombre_visible = col_nombre.text_input(
            "Nombre visible de la malla",
            help="Ejemplo: Ingeniería Industrial – Virtual",
        )

        if archivo is None:
            st.info("Sube un archivo JSON para poder simular la malla.")
            return

        contenido = archivo.read()

        # --- Simulación ---
        if st.button("▶️ Simular estructura de malla", key="btn_simular_malla"):
            resultado = simular_malla_desde_bytes(contenido)

            if not resultado.es_valida:
                st.error("La malla NO es válida. Revisa los errores a continuación:")
                for err in resultado.errores:
                    st.markdown(f"- {err}")
            else:
                st.success("La malla es estructuralmente válida. Resumen:")
                st.json(resultado.resumen)
                st.caption(
                    "Si estás de acuerdo con esta estructura y los créditos, puedes proceder a registrar la malla."
                )
                st.session_state["sim_malla_ok"] = True
                st.session_state["sim_malla_bytes"] = contenido
                st.session_state["sim_malla_id"] = id_malla
                st.session_state["sim_malla_nombre"] = nombre_visible

        # --- Registro definitivo ---
        if st.session_state.get("sim_malla_ok") and st.session_state.get("sim_malla_bytes"):
            st.markdown("---")
            st.markdown("### ✅ Registro definitivo de la malla")

            if not id_malla or not nombre_visible:
                st.warning(
                    "Debes diligenciar el identificador y el nombre visible antes de registrar la malla."
                )
            else:
                if st.button("💾 Registrar malla en el sistema", key="btn_registrar_malla"):
                    ok, mensaje = registrar_malla(
                        id_malla=st.session_state["sim_malla_id"] or id_malla,
                        nombre_visible=st.session_state["sim_malla_nombre"] or nombre_visible,
                        contenido=st.session_state["sim_malla_bytes"],
                    )
                    if ok:
                        st.success(mensaje)
                        st.caption(
                            "La malla ya puede seleccionarse en el selector de mallas al inicio de este módulo."
                        )
                        # Limpieza estado simulación
                        for k in ["sim_malla_ok", "sim_malla_bytes", "sim_malla_id", "sim_malla_nombre"]:
                            st.session_state.pop(k, None)
                    else:
                        st.error(mensaje)


def mostrar_malla():
    st.title("🗺️ Malla Curricular – Programas UNIMINUTO")

    st.markdown(
        """
        Esta vista cruza una **malla curricular** con el **histórico académico**
        del estudiante:

        - APROBADO: nota final ≥ 3.0.
        - PERDIDO: nota final < 3.0.
        - TRANSFERENCIA: cursos registrados con NRC simbólico `TRANSF-*`.
        - PENDIENTE: cursos de la malla que aún no aparecen en el histórico.
        """
    )

    st.divider()

    # --- Selección de malla ---
    st.subheader("🧩 Selección de malla curricular")
    id_malla, malla_dict = _elegir_malla()

    if not malla_dict:
        st.error("No se pudo cargar la malla seleccionada.")
        _seccion_admin_mallas()
        return

    st.caption(
        f"Programa (malla seleccionada): **{malla_dict.get('programa', 'Sin nombre')}** · "
        f"Créditos totales: **{malla_dict.get('creditos_totales', 'N/D')}**"
    )

    st.divider()

    # --- Búsqueda de estudiante ---
    q = st.text_input("ID del estudiante o nombre:")
    col_buscar, col_reset = st.columns([1, 1])
    buscar = col_buscar.button("Buscar", type="primary")
    limpiar = col_reset.button("Limpiar")

    if limpiar:
        st.session_state.pop("malla_sel_est", None)
        st.session_state.pop("malla_sel_hist", None)
        st.session_state.pop("malla_sel_malla", None)
        st.session_state.pop("malla_sel_id_malla", None)
        st.rerun()

    if buscar and (q or "").strip():
        resultados = buscar_estudiantes(q.strip(), limit=50)

        if not resultados:
            st.warning("No se encontraron coincidencias.")
            return

        if len(resultados) > 1:
            st.info("Se encontraron varias coincidencias. Selecciona una:")
            opciones_est = [
                f"{r['id_estudiante']} — {r['nombre']} ({r['programa']})"
                for r in resultados
            ]
            idx = st.selectbox(
                "Resultados:",
                list(range(len(opciones_est))),
                format_func=lambda i: opciones_est[i],
                key="malla_sel_idx_est",
            )
            seleccionado = resultados[idx]
        else:
            seleccionado = resultados[0]

        ficha = datos_estudiante(seleccionado["id_estudiante"]) or {}
        hist = historial_estudiante(seleccionado["id_estudiante"]) or []

        cruce = mapear_malla_con_historico(hist, malla_dict)

        # --- Validación: ¿el estudiante tiene cursos de esta malla? ---
        tiene_cursos_malla = any(
            any(
                str(c.get("estado", "")).upper() in ("APROBADO", "PERDIDO", "TRANSFERENCIA")
                for c in bloque.get("cursos", [])
            )
            for bloque in cruce
        )

        if not tiene_cursos_malla:
            programa_malla = malla_dict.get("programa", "N/D")
            st.error(
                "La malla curricular seleccionada no corresponde al histórico del estudiante. "
                f"No se encontraron cursos de la malla **{programa_malla}** en el historial del estudiante."
            )
            programas_est = _programas_desde_historial(hist, ficha.get("programa"))
            if programas_est != "N/D" and "," not in programas_est:
                st.info("Escoge la malla curricular que coincida con el programa del estudiante.")
            return

        st.session_state["malla_sel_est"] = ficha
        st.session_state["malla_sel_hist"] = hist
        st.session_state["malla_sel_malla"] = cruce
        st.session_state["malla_sel_id_malla"] = id_malla
        st.rerun()

    ficha = st.session_state.get("malla_sel_est")
    cruce = st.session_state.get("malla_sel_malla")
    hist_guardado = st.session_state.get("malla_sel_hist") or []

    if not ficha or not cruce:
        st.caption(
            "Selecciona una malla, ingresa un criterio y presiona **Buscar** para generar el reporte."
        )
        _seccion_admin_mallas()
        return

    # --- Programas en los que ha estado el estudiante ---
    programas_est = _programas_desde_historial(
        hist_guardado,
        programa_ficha=ficha.get("programa"),
    )

    st.subheader("🪪 Datos del estudiante")
    st.json(ficha)

    st.markdown(f"**Programas del estudiante:** {programas_est}")

    st.subheader("📚 Malla curricular por cuatrimestre")

    estado_color = {
        "APROBADO": "#C8E6C9",
        "PERDIDO": "#FFCDD2",
        "TRANSFERENCIA": "#BBDEFB",
        "PENDIENTE": "#F5F5F5",
    }

    # --- Resumen de créditos por estado (para encabezados y PDF) ---
    resumen_creditos = _resumen_creditos(cruce)
    total_creditos = sum(resumen_creditos.values())

    cred_aprob_transf = resumen_creditos["APROBADO"] + resumen_creditos["TRANSFERENCIA"]
    cred_pend = resumen_creditos["PENDIENTE"]
    cred_perd = resumen_creditos["PERDIDO"]

    porc_aproba = (
        (cred_aprob_transf * 100.0 / total_creditos) if total_creditos > 0 else 0.0
    )
    porc_pendie = 100.0 - porc_aproba if total_creditos > 0 else 0.0

    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
    col_res1.metric("Cred/aprob/transf", cred_aprob_transf)
    col_res2.metric("Créditos pendientes", cred_pend)
    col_res3.metric("Créditos perdidos", cred_perd)
    col_res4.metric("Porc/aproba_malla", f"{porc_aproba:.1f} %")

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
                # ahora usamos todos los programas detectados
                "Programa": programas_est,
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

    # --- Sección de administración de mallas ---
    st.divider()
    _seccion_admin_mallas()


if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap

    bootstrap.run("app.py", "", [], {})