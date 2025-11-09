# src/modules/validators.py
import pandas as pd
from pathlib import Path

# -------------------------------------------------
# CONFIGURACIÓN Y ESTRUCTURA BASE ARGOS
# -------------------------------------------------

RUTA_EJEMPLO = Path("data/argos_samples/ejemplo_argos.xlsx")

# Layout esperado ARGOS (A–W) usando NOMBRES CANÓNICOS
LAYOUT_ARGOS = [
    "ID_ESTUDIANTE", "NOMBRE_ESTUDIANTE", "RECTORIA", "DESCRIPCION_RECTORIA",
    "SEDE", "DESCRIPCION_SEDE", "FACULTAD", "DESCRIPCION_FACULTAD",
    "PROGRAMA", "DESCRIPCION_PROGRAMA", "NIVEL", "DESCRIPCION_NIVEL",
    "JORNADA", "PERIODO", "NRCS", "ALFA", "NUMERI", "DESCRIPCION",
    "DEFINITIVA", "PROMEDIO_SEM", "PROM_ACU", "FORMA_CAL", "COMENTARIO"
]

# Mapa de posiciones críticas (A–W indexadas desde 0)
POSICIONES_CLAVE = {
    13: "PERIODO",
    14: "NRCS",
    15: "ALFA",
    16: "NUMERI",
    17: "DESCRIPCION",
    18: "DEFINITIVA"
}

# Alias frecuentes -> nombre canónico
EQUIVALENCIAS = {
    "FACULTA": "FACULTAD",
    "DESCRIPION": "DESCRIPCION",
    "DESCRIPCION_ASIGNATURA": "DESCRIPCION",
    "ALFA_NUMERI": "NRCS",
    "NOMBRE": "NOMBRE_ESTUDIANTE",
}


def resumen_validacion(df: pd.DataFrame) -> dict:
    """
    Valida estructura híbrida (por nombre y posición).
    - Detecta errores de encabezado.
    - Repara alias comunes.
    - Evalúa notas, periodos y duplicados.
    """
    # Debug: encabezados crudos tal como llegan desde pandas
    print("🧾 [RAW] Encabezados detectados por pandas:", df.columns.tolist())

    # Normalizar nombres
    df.columns = df.columns.str.strip().str.upper()
    df.rename(columns=EQUIVALENCIAS, inplace=True)

    # Debug: encabezados ya normalizados/canónicos
    print("🧾 [NORM] Encabezados normalizados:", df.columns.tolist())

    # 1️⃣ Validación nominal (contra layout canónico)
    columnas_presentes = list(df.columns)
    faltantes = [col for col in LAYOUT_ARGOS if col not in columnas_presentes]
    columnas_validas = len(faltantes) == 0

    # 2️⃣ Validación por posición de columnas clave
    posicion_correcta = True
    errores_pos = []
    for idx, nombre_esperado in POSICIONES_CLAVE.items():
        if idx >= len(df.columns):
            posicion_correcta = False
            errores_pos.append(f"Falta columna en posición {idx+1} ({nombre_esperado})")
        elif df.columns[idx] != nombre_esperado:
            posicion_correcta = False
            errores_pos.append(
                f"Columna {idx+1} esperada '{nombre_esperado}' pero se encontró '{df.columns[idx]}'"
            )

    # 3️⃣ Validación de notas
    if "DEFINITIVA" in df.columns:
        notas = (
            df["DEFINITIVA"].astype(str)
            .str.replace(",", ".", regex=False)
            .str.replace(r"[^0-9.\-]", "", regex=True)
            .str.strip()
        )
        notas_num = pd.to_numeric(notas, errors="coerce")
        notas_validas = notas_num.dropna().between(0, 5, inclusive="both").all()
    else:
        notas_validas = False

    # 4️⃣ Validación de periodos (semestres/trimestres frecuentes)
    periodos_validos = (
        df["PERIODO"].astype(str).str.match(r"^20\d{2}(05|07|13|16|18|23|25|28)$", na=False).all()
        if "PERIODO" in df.columns else False
    )

    # 5️⃣ Duplicados (clave natural: estudiante + NRC + periodo)
    duplicados = (
        df.duplicated(subset=["ID_ESTUDIANTE", "NRCS", "PERIODO"]).any()
        if all(col in df.columns for col in ["ID_ESTUDIANTE", "NRCS", "PERIODO"])
        else None
    )

    return {
        "columnas_validas": columnas_validas,
        "faltantes": faltantes,
        "posicion_correcta": posicion_correcta,
        "errores_posicion": errores_pos,
        "notas_validas": notas_validas,
        "periodos_validos": periodos_validos,
        "duplicados": duplicados,
        "total_registros": len(df)
    }


# -------------------------------------------------
# PRUEBA LOCAL
# -------------------------------------------------
if __name__ == "__main__":
    if not RUTA_EJEMPLO.exists():
        print(f"⚠️ No se encontró el archivo en: {RUTA_EJEMPLO}")
    else:
        df = pd.read_excel(RUTA_EJEMPLO)
        resultado = resumen_validacion(df)
        print("✅ Validación híbrida completada:")
        for k, v in resultado.items():
            print(f"{k}: {v}")
