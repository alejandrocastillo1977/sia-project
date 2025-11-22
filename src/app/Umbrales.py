import streamlit as st
import plotly.express as px
import pandas as pd
import io
from pathlib import Path
from datetime import datetime

from database.queries import listar_periodos, obtener_notas_por_umbral
from modules.credit_progress import (
    listar_programas_soportados,
    generar_reporte_avance_creditos,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # .../sia-project
EXPORTS_DIR = BASE_DIR / "exports" / "umbrales"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def mostrar_umbrales():
    st.header("📊 Avance en créditos por programa")
    st.write(
        "Este módulo permite identificar estudiantes según su avance en créditos "
        "frente a la malla del programa, aplicando un umbral mínimo de porcentaje."
    )

    programas = listar_programas_soportados()
    if not programas:
        st.warning(
            "No hay programas soportados actualmente para el cálculo de avance en créditos."
        )
        return

    opciones_map: dict[str, str] = {}
    for p in programas:
        cod = str(p.get("codigo_programa", "")).strip()
        nombre = str(p.get("nombre_programa", cod)).strip()
        etiqueta = f"{cod} – {nombre}" if cod else nombre
        opciones_map[etiqueta] = cod

    etiquetas = sorted(opciones_map.keys())
    etiqueta_seleccionada = st.selectbox("Programa", options=etiquetas)
    codigo_programa = opciones_map.get(etiqueta_seleccionada, "").strip()
    if not codigo_programa:
        st.error("No se pudo determinar el código del programa seleccionado.")
        return

    porcentaje_min = st.number_input(
        "Porcentaje mínimo de avance en créditos",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=1.0,
        help=(
            "Se mostrarán solo los estudiantes cuyo avance en créditos sea mayor o "
            "igual a este valor."
        ),
    )

    if st.button("Generar reporte de avance"):
        with st.spinner("Calculando avance en créditos..."):
            resultado = generar_reporte_avance_creditos(codigo_programa, porcentaje_min)

        st.subheader("Resumen del programa")
        col1, col2, col3 = st.columns(3)

        total_estudiantes = int(
            resultado.get("total_estudiantes_programa", 0) or 0
        )
        total_filtrados = int(
            resultado.get("total_con_avance_mayor_igual", 0) or 0
        )
        prom_filtrados = resultado.get("promedio_porcentaje_filtrados", None)

        col1.metric("Estudiantes con historial", total_estudiantes)
        col2.metric("Estudiantes con avance ≥ umbral", total_filtrados)

        if prom_filtrados is not None:
            col3.metric(
                "Promedio % avance (filtrados)", f"{float(prom_filtrados):.1f} %"
            )
        else:
            col3.metric("Promedio % avance (filtrados)", "—")

        st.subheader("Detalle de estudiantes que cumplen el umbral")

        lista_filtrados = resultado.get("estudiantes_filtrados") or []
        if not lista_filtrados:
            st.info(
                "No se encontraron estudiantes que cumplan el porcentaje mínimo de avance."
            )
            return

        df = pd.DataFrame(lista_filtrados)

        columnas_preferidas = [
            "id_estudiante",
            "nombre",
            "programa",
            "cred_aprob_transf",
            "cred_perdidos",
            "cred_pendientes",
            "cred_totales_malla",
            "porc_aproba_malla",
        ]
        columnas_existentes = [c for c in columnas_preferidas if c in df.columns]

        st.dataframe(df[columnas_existentes])

        csv = df[columnas_existentes].to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Descargar CSV de estudiantes filtrados",
            data=csv,
            file_name=(
                f"avance_creditos_{codigo_programa}_{int(porcentaje_min)}.csv"
            ),
            mime="text/csv",
        )

        # --- Descarga adicional: Excel formateado ---
        if not df[columnas_existentes].empty:
            output = io.BytesIO()

            # Copia de trabajo para no alterar el df original
            df_excel = df[columnas_existentes].copy()

            # Si existe la columna de porcentaje, convertirla a fracción (0.743 -> 74.3%)
            if "porc_aproba_malla" in df_excel.columns:
                df_excel["porc_aproba_malla"] = (
                    df_excel["porc_aproba_malla"].astype(float) / 100.0
                )

            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                hoja = "AvanceCreditos"
                # Dejamos algunas filas arriba para título y metadatos
                start_row = 4

                df_excel.to_excel(
                    writer,
                    sheet_name=hoja,
                    index=False,
                    startrow=start_row,
                )

                workbook = writer.book
                worksheet = writer.sheets[hoja]

                # Formatos básicos
                titulo_fmt = workbook.add_format(
                    {"bold": True, "font_size": 14}
                )
                meta_fmt = workbook.add_format(
                    {"italic": True}
                )
                header_fmt = workbook.add_format(
                    {
                        "bold": True,
                        "bg_color": "#D9E1F2",
                        "border": 1,
                    }
                )
                normal_fmt = workbook.add_format({"border": 1})
                percent_fmt = workbook.add_format(
                    {"border": 1, "num_format": "0.0%"}
                )

                # Título y metadatos arriba
                titulo = (
                    f"Reporte de avance en créditos – "
                    f"{resultado.get('codigo_programa', codigo_programa)} – "
                    f"{resultado.get('nombre_programa', '')}"
                )
                worksheet.write(0, 0, titulo, titulo_fmt)
                worksheet.write(
                    1,
                    0,
                    f"Porcentaje mínimo aplicado: {porcentaje_min:.1f} %",
                    meta_fmt,
                )
                worksheet.write(
                    2,
                    0,
                    f"Estudiantes con historial: {total_estudiantes}",
                    meta_fmt,
                )
                worksheet.write(
                    3,
                    0,
                    f"Estudiantes con avance ≥ umbral: {total_filtrados}",
                    meta_fmt,
                )

                # Encabezados de tabla con formato
                for col_idx, col_name in enumerate(df_excel.columns):
                    worksheet.write(start_row, col_idx, col_name, header_fmt)

                # Aplicar formato de bordes a las celdas de datos
                num_rows, num_cols = df_excel.shape
                for row in range(start_row + 1, start_row + 1 + num_rows):
                    for col in range(num_cols):
                        # Para la columna de porcentaje usamos percent_fmt
                        col_name = df_excel.columns[col]
                        if col_name == "porc_aproba_malla":
                            worksheet.write(
                                row,
                                col,
                                df_excel.iloc[row - start_row - 1, col],
                                percent_fmt,
                            )
                        else:
                            worksheet.write(
                                row,
                                col,
                                df_excel.iloc[row - start_row - 1, col],
                                normal_fmt,
                            )

                # Autoajuste aproximado de ancho de columnas
                for col_idx, col_name in enumerate(df_excel.columns):
                    max_len = max(
                        len(str(col_name)),
                        df_excel[col_name].astype(str).map(len).max(),
                    )
                    # pequeño margen extra
                    worksheet.set_column(col_idx, col_idx, max_len + 2)

                # Filtro automático en la fila de encabezado
                worksheet.autofilter(
                    start_row,
                    0,
                    start_row + num_rows,
                    num_cols - 1,
                )

                # Congelar panes debajo del encabezado
                worksheet.freeze_panes(start_row + 1, 0)

            output.seek(0)

            st.download_button(
                label="📊 Descargar Excel formateado",
                data=output,
                file_name=(
                    f"avance_creditos_{codigo_programa}_{int(porcentaje_min)}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )
    else:
        st.info(
            "Seleccione el programa, defina el porcentaje mínimo de avance y haga clic en "
            "'Generar reporte de avance' para ver el resultado."
        )
