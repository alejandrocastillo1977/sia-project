import pandas as pd
import numpy as np
from pathlib import Path

# -------------------------------------------------
# CONFIGURACIÓN
# -------------------------------------------------

# Ruta por defecto del archivo de ejemplo (puedes cambiarla si deseas)
RUTA_EJEMPLO = Path("data/argos_samples/ejemplo_argos.xlsx")

# Columnas oficiales del formato ARGOS A–W (según documento de modelado de datos)
COLUMNAS_ARGOS = [
    "ID_ESTUDIANTE", "NOMBRE_ESTUDIANTE", "RECTORIA", "DESCRIPCION_RECTORIA",
    "SEDE", "DESCRIPCION_SEDE", "FACULTAD", "DESCRIPCION_FACULTAD",
    "PROGRAMA", "DESCRIPCION_PROGRAMA", "NIVEL", "DESCRIPCION_NIVEL",
    "JORNADA", "PERIODO", "NRCS", "ALFA", "NUMERI", "DESCRIPCION",
    "DEFINITIVA", "PROMEDIO_SEM", "PROM_ACU", "FORMA_CAL", "COMENTARIO"
]

# -------------------------------------------------
# FUNCIONES PRINCIPALES
# -------------------------------------------------

def resumen_validacion(df: pd.DataFrame) -> dict:
    """
    Valida columnas, tipos de nota y formato de periodo según estructura ARGOS.
    Incluye detección de errores comunes en encabezados y valores.
    """
    # Normalizar encabezados
    df.columns = df.columns.str.strip().str.upper()

    # Sinónimos y errores frecuentes en los reportes ARGOS
    equivalencias = {
        "FACULTA": "FACULTAD",
        "DESCRIPCION_ASIGNATURA": "DESCRIPCION",
        "DESCRIPION": "DESCRIPCION",    # error tipográfico frecuente en ARGOS
        "ASIGNATURA": "DESCRIPCION",
        "NOMBRE": "NOMBRE_ESTUDIANTE",
        "ALFA_NUMERI": "NRCS"           # algunos reportes combinan ambos
    }
    df.rename(columns=equivalencias, inplace=True)

    # --- 1️⃣ Validación de columnas ---
    columnas_presentes = set(df.columns)
    columnas_requeridas = set(COLUMNAS_ARGOS)
    faltantes = list(columnas_requeridas - columnas_presentes)
    columnas_validas = len(faltantes) == 0

    # --- 2️⃣ Validación de notas (acepta coma, punto, texto o espacios) ---
    if "DEFINITIVA" in df.columns:
        notas = (
            df["DEFINITIVA"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(r"[^0-9.\-]", "", regex=True)   # limpia símbolos, letras o guiones
            .str.strip()
        )

        # Convertir a numérico y eliminar valores vacíos o inválidos
        notas_num = pd.to_numeric(notas, errors="coerce")

        # Mostrar vista previa (útil para depuración)
        print("🔎 Vista previa de notas convertidas:", notas_num.head().tolist())

        notas_validas = notas_num.dropna().between(0, 5, inclusive="both").all()
    else:
        notas_validas = False

    # --- 3️⃣ Validación de periodos académicos ---
    periodos_validos = (
        df["PERIODO"].astype(str).str.match(r"^20\d{2}(05|07|13|16|18|23)$", na=False).all()
        if "PERIODO" in df.columns else False
    )

    # --- 4️⃣ Detección de duplicados ---
    if all(col in df.columns for col in ["ID_ESTUDIANTE", "NRCS", "PERIODO"]):
        duplicados = df.duplicated(subset=["ID_ESTUDIANTE", "NRCS", "PERIODO"]).any()
    else:
        duplicados = None

    # Resultado final
    return {
        "columnas_validas": columnas_validas,
        "faltantes": faltantes,
        "notas_validas": notas_validas,
        "periodos_validos": periodos_validos,
        "duplicados": duplicados,
        "total_registros": len(df)
    }

# -------------------------------------------------
# EJECUCIÓN DIRECTA PARA PRUEBAS
# -------------------------------------------------

if __name__ == "__main__":
    if not RUTA_EJEMPLO.exists():
        print(f"⚠️ No se encontró el archivo en: {RUTA_EJEMPLO}")
    else:
        df = pd.read_excel(RUTA_EJEMPLO)
        resultado = resumen_validacion(df)
        print("✅ Validación completada:\n", resultado)
