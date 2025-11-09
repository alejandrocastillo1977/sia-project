import os
from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime

# -------------------------------------------------
# CONFIGURACIÓN DE RUTAS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------
# FUNCIÓN: EXPORTAR A EXCEL
# -------------------------------------------------
def exportar_excel(df: pd.DataFrame, nombre_archivo: str = "reporte.xlsx") -> str:
    """
    Exporta un DataFrame a un archivo Excel con formato institucional.
    Retorna la ruta absoluta del archivo generado.
    """
    ruta_salida = EXPORT_DIR / nombre_archivo
    with pd.ExcelWriter(ruta_salida, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")
        workbook = writer.book
        worksheet = writer.sheets["Datos"]

        formato_header = workbook.add_format({
            "bold": True,
            "bg_color": "#E0E0E0",
            "font_color": "black",
            "align": "center"
        })
        worksheet.set_row(0, 20, formato_header)

        for i, col in enumerate(df.columns):
            col_width = max(len(str(col)), int(df[col].astype(str).map(len).mean()))
            worksheet.set_column(i, i, min(col_width + 3, 40))

    print(f"✅ Archivo Excel generado: {ruta_salida}")
    return str(ruta_salida)


# -------------------------------------------------
# FUNCIÓN: EXPORTAR A PDF
# -------------------------------------------------
def exportar_pdf(datos: dict, nombre_archivo: str = "reporte.pdf", df: pd.DataFrame = None) -> str:
    """
    Genera un reporte PDF con formato institucional de UNIMINUTO.
    Incluye NRC y código alfanumérico del curso.
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
    c.drawString(200, height - 80, f"Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

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
                c.drawString(x + 5, y, texto)
                x += anchos[i]
            y -= 14
            if y < 80:
                c.showPage()
                y = height - 80
                c.setFont("Helvetica", 9)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 40, "Sistema SIA – UNIMINUTO | Reporte académico generado automáticamente.")
    c.save()
    print(f"✅ Archivo PDF generado: {ruta_salida}")
    return str(ruta_salida)


