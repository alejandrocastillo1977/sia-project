import os
from pathlib import Path
from datetime import datetime

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# -------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# FUNCIÓN: EXPORTAR A EXCEL (GENÉRICO)
# -------------------------------------------------
def exportar_excel(df: pd.DataFrame, nombre_archivo: str = "reporte.xlsx") -> str:
    """
    Exporta un DataFrame a un archivo Excel con formato institucional.
    Si existen cursos de transferencia (id_curso o NRC que inicien con 'TRANSF-'),
    se colorean en azul claro.
    """
    ruta_salida = EXPORT_DIR / nombre_archivo
    with pd.ExcelWriter(ruta_salida, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")
        workbook = writer.book
        worksheet = writer.sheets["Datos"]

        formato_header = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#E0E0E0",
                "font_color": "black",
                "align": "center",
            }
        )
        formato_transferencia = workbook.add_format({"bg_color": "#E3F2FD"})
        worksheet.set_row(0, 20, formato_header)

        for i, col in enumerate(df.columns):
            col_width = max(
                len(str(col)), int(df[col].astype(str).map(len).mean() if not df.empty else 0)
            )
            worksheet.set_column(i, i, min(col_width + 3, 40))

        # 🔹 Aplicar formato a filas con cursos de transferencia
        if "id_curso" in df.columns:
            for row_num, valor in enumerate(df["id_curso"], start=1):
                if str(valor).startswith("TRANSF-"):
                    worksheet.write(
                        row_num,
                        list(df.columns).index("id_curso"),
                        valor,
                        formato_transferencia,
                    )
        elif "nrc" in df.columns:
            for row_num, valor in enumerate(df["nrc"], start=1):
                if str(valor).startswith("TRANSF-"):
                    worksheet.write(
                        row_num,
                        list(df.columns).index("nrc"),
                        valor,
                        formato_transferencia,
                    )

    print(f"✅ Archivo Excel generado: {ruta_salida}")
    return str(ruta_salida)


# -------------------------------------------------
# FUNCIÓN: EXPORTAR A EXCEL PARA MALLA
# -------------------------------------------------
def exportar_excel_malla(
    malla_cruzada: list[dict], nombre_archivo: str = "malla_curricular.xlsx"
) -> str:
    """
    Exporta la malla cruzada (lista de cuatrimestres con cursos) a Excel,
    reutilizando exportar_excel.
    """
    filas: list[dict] = []

    for bloque in malla_cruzada:
        cuat = bloque.get("cuatrimestre")
        for curso in bloque.get("cursos", []):
            filas.append(
                {
                    "cuatrimestre": cuat,
                    "codigo": curso.get("codigo"),
                    "nombre_curso": curso.get("nombre"),
                    "creditos": curso.get("creditos"),
                    "estado": curso.get("estado"),
                    "nota": curso.get("nota"),
                    "id_periodo": curso.get("id_periodo"),
                }
            )

    df = pd.DataFrame(filas)
    return exportar_excel(df, nombre_archivo)


# -------------------------------------------------
# FUNCIÓN: EXPORTAR A PDF (HISTORIAL INDIVIDUAL)
# -------------------------------------------------
def exportar_pdf(
    datos: dict, nombre_archivo: str = "reporte.pdf", df: pd.DataFrame | None = None
) -> str:
    """
    Genera un reporte PDF con formato institucional de UNIMINUTO.
    Si el curso es una transferencia, se muestra con NRC = 'TRANSF'.
    """
    ruta_salida = EXPORT_DIR / nombre_archivo
    c = canvas.Canvas(str(ruta_salida), pagesize=letter)
    width, height = letter

    # Encabezado institucional
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/2/29/Logo_uniminuto.png"
    try:
        c.drawImage(logo_url, 40, height - 80, width=120, preserveAspectRatio=True)
    except Exception:
        pass

    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0, 0.2, 0.6)
    c.drawString(200, height - 60, "UNIMINUTO – Sistema de Inteligencia Académica (SIA)")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawString(
        200,
        height - 80,
        f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    )

    c.line(40, height - 90, width - 40, height - 90)

    y = height - 120
    for clave, valor in datos.items():
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, f"{clave}:")
        c.setFont("Helvetica", 11)
        c.drawString(200, y, str(valor))
        y -= 20

    if df is not None and not df.empty:
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60, y, "📘 Historial académico:")
        y -= 25

        df = df.sort_values(by="id_periodo", ascending=True)

        columnas = ["id_periodo", "nrc", "codigo_curso", "nombre_curso", "nota", "version_periodo"]
        encabezados = ["Periodo", "NRC", "Código", "Curso", "Nota", "Versión"]
        anchos = [60, 60, 80, 210, 50, 60]

        x = 60
        c.setFont("Helvetica-Bold", 10)
        for i, head in enumerate(encabezados):
            c.drawString(x + 5, y, head)
            x += anchos[i]
        y -= 15
        c.line(60, y, width - 60, y)
        y -= 10

        c.setFont("Helvetica", 9)
        for _, fila in df.iterrows():
            x = 60
            for i, col in enumerate(columnas):
                texto = str(fila.get(col, ""))[:40]
                # 🔹 Simplificar TRANSF
                if col in ("nrc", "id_curso") and texto.startswith("TRANSF-"):
                    texto = "TRANSF"
                c.drawString(x + 5, y, texto)
                x += anchos[i]
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 80
                c.setFont("Helvetica", 9)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        40,
        40,
        "Sistema SIA – UNIMINUTO | Reporte académico generado automáticamente.",
    )
    c.save()
    print(f"✅ Archivo PDF generado: {ruta_salida}")
    return str(ruta_salida)


# -------------------------------------------------
# FUNCIÓN: EXPORTAR A PDF PARA MALLA
# -------------------------------------------------
def exportar_pdf_malla(
    datos: dict, malla_cruzada: list[dict], nombre_archivo: str = "malla_curricular.pdf"
) -> str:
    """
    Genera un PDF institucional con la malla curricular cruzada por cuatrimestre.
    """
    ruta_salida = EXPORT_DIR / nombre_archivo
    c = canvas.Canvas(str(ruta_salida), pagesize=letter)
    width, height = letter

    # Encabezado institucional
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/2/29/Logo_uniminuto.png"
    try:
        c.drawImage(logo_url, 40, height - 80, width=120, preserveAspectRatio=True)
    except Exception:
        pass

    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0, 0.2, 0.6)
    c.drawString(200, height - 60, "UNIMINUTO – Sistema de Inteligencia Académica (SIA)")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    c.drawString(
        200,
        height - 80,
        f"Malla generada: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    )

    c.line(40, height - 90, width - 40, height - 90)

    # Datos generales (estudiante, programa, etc.)
    y = height - 120
    for clave, valor in datos.items():
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, f"{clave}:")
        c.setFont("Helvetica", 11)
        c.drawString(220, y, str(valor))
        y -= 18

    # Tabla por cuatrimestre
    c.setFont("Helvetica-Bold", 12)
    y -= 10
    c.drawString(60, y, "📚 Malla curricular por cuatrimestre")
    y -= 25

    # Encabezados y anchos ajustados
    c.setFont("Helvetica-Bold", 10)
    encabezados = ["Cuat.", "Código", "Curso", "Créd.", "Estado", "Nota", "Periodo"]
    anchos = [35, 65, 200, 35, 70, 35, 55]

    def _dibujar_header(fy: float) -> float:
        x = 60
        c.setFont("Helvetica-Bold", 10)
        for i, head in enumerate(encabezados):
            c.drawString(x + 2, fy, head)
            x += anchos[i]
        fy -= 12
        c.line(60, fy, width - 60, fy)
        return fy - 10  # un poco más de espacio bajo el encabezado

    y = _dibujar_header(y)

    # Colores más fuertes por estado (fondo)
    colores_estado = {
        "APROBADO": colors.Color(0.75, 0.90, 0.75),
        "PERDIDO": colors.Color(0.98, 0.75, 0.75),
        "TRANSFERENCIA": colors.Color(0.70, 0.82, 0.97),
        "PENDIENTE": colors.Color(0.90, 0.90, 0.90),
    }

    c.setFont("Helvetica", 9)
    for bloque in malla_cruzada:
        cuat = bloque.get("cuatrimestre")
        for curso in bloque.get("cursos", []):
            if y < 60:
                c.showPage()
                y = height - 80
                y = _dibujar_header(y)
                c.setFont("Helvetica", 9)

            estado = str(curso.get("estado", "")).upper()
            bg_color = colores_estado.get(estado, colors.white)

            # --- Fila coloreada y más alta ---
            fila_altura = 20  # altura más grande para no morder texto
            y_texto = y - 5   # bajamos un poco la línea base del texto
            c.setFillColor(bg_color)
            c.rect(60, y - fila_altura + 2, sum(anchos), fila_altura, stroke=0, fill=1)
            c.setFillColor(colors.black)

            x = 60
            estado_print = {
                "APROBADO": "APR",
                "PERDIDO": "PER",
                "TRANSFERENCIA": "TRANSF",
                "PENDIENTE": "PEND",
            }.get(estado, estado[:6])

            fila_vals = [
                cuat,
                curso.get("codigo", ""),
                str(curso.get("nombre", ""))[:40],
                curso.get("creditos", ""),
                estado_print,
                "-" if curso.get("nota") is None else f"{float(curso['nota']):.1f}",
                curso.get("id_periodo", "") or "-",
            ]

            for i, val in enumerate(fila_vals):
                c.drawString(x + 2, y_texto, str(val))
                x += anchos[i]

            y -= fila_altura

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        40,
        40,
        "Sistema SIA – UNIMINUTO | Malla curricular generada automáticamente.",
    )
    c.save()
    print(f"✅ Archivo PDF de malla generado: {ruta_salida}")
    return str(ruta_salida)