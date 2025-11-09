import sqlite3
from pathlib import Path
import pandas as pd

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"

def validar_datos_analiticos():
    """
    Valida la integridad y suficiencia de los datos para análisis.
    Retorna un diccionario con métricas descriptivas.
    """
    if not DB_PATH.exists():
        return {"error": f"No se encontró la base de datos en {DB_PATH}"}

    with sqlite3.connect(DB_PATH) as conn:
        # ---- 1️⃣ Conteos básicos ----
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM Estudiante;")
        total_estudiantes = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Curso;")
        total_cursos = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM Inscripcion;")
        total_inscripciones = cur.fetchone()[0]

        # ---- 2️⃣ Análisis de notas ----
        df_notas = pd.read_sql_query("""
            SELECT nota, id_periodo, version_periodo
            FROM Inscripcion
            WHERE nota IS NOT NULL;
        """, conn)

        if df_notas.empty:
            return {"error": "No hay registros de notas en la tabla Inscripcion."}

        rango_notas = (float(df_notas["nota"].min()), float(df_notas["nota"].max()))
        promedio_general = round(float(df_notas["nota"].mean()), 2)
        desviacion = round(float(df_notas["nota"].std()), 2)
        total_periodos = df_notas["id_periodo"].nunique()
        versiones_distintas = df_notas["version_periodo"].nunique()

        # ---- 3️⃣ Distribución por periodo ----
        notas_por_periodo = (
            df_notas.groupby("id_periodo")["nota"]
            .agg(["count", "mean", "min", "max"])
            .round(2)
            .reset_index()
            .to_dict(orient="records")
        )

    return {
        "total_estudiantes": total_estudiantes,
        "total_cursos": total_cursos,
        "total_inscripciones": total_inscripciones,
        "promedio_general": promedio_general,
        "rango_notas": rango_notas,
        "desviacion": desviacion,
        "total_periodos": total_periodos,
        "versiones_distintas": versiones_distintas,
        "notas_por_periodo": notas_por_periodo,
    }

# ---- Prueba local ----
if __name__ == "__main__":
    resumen = validar_datos_analiticos()
    print("📊 Resultado de validación analítica:\n")
    for clave, valor in resumen.items():
        print(f"{clave}: {valor}")
