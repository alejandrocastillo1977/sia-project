import sqlite3
from pathlib import Path

# Ruta de la base de datos
DB_PATH = Path("data/sia.db")


def ejecutar_consulta(query, params=()):
    """
    Ejecuta una consulta SQL genérica y devuelve los resultados como lista de diccionarios.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columnas = [col[0] for col in cursor.description]
        resultados = cursor.fetchall()
    return [dict(zip(columnas, fila)) for fila in resultados]


# -------------------------------------------------
# CONSULTAS ESPECÍFICAS
# -------------------------------------------------

def listar_estudiantes():
    """
    Retorna todos los estudiantes registrados en la tabla Estudiante.
    """
    query = """
        SELECT id_estudiante, nombre, programa, correo_institucional
        FROM Estudiante
        ORDER BY nombre;
    """
    return ejecutar_consulta(query)


def historial_estudiante(id_estudiante):
    """
    Devuelve el historial académico de un estudiante (sus cursos y notas por periodo).
    """
    query = """
        SELECT 
            i.id_periodo, 
            c.id_curso, 
            c.nombre AS nombre_curso,
            i.nota,
            i.version_periodo
        FROM Inscripcion i
        JOIN Curso c ON i.id_curso = c.id_curso
        WHERE i.id_estudiante = ?
        ORDER BY i.id_periodo;
    """
    return ejecutar_consulta(query, (id_estudiante,))


def kpi_programa():
    """
    Devuelve KPIs agregados del programa:
    - total de estudiantes registrados
    - promedio general de notas (ponderado sobre inscripciones)
    """
    query = """
        SELECT
            COUNT(DISTINCT e.id_estudiante) AS total_estudiantes,
            ROUND(AVG(i.nota), 2) AS promedio_general
        FROM Estudiante e
        LEFT JOIN Inscripcion i ON e.id_estudiante = i.id_estudiante;
    """
    return ejecutar_consulta(query)


# -------------------------------------------------
# PRUEBA LOCAL
# -------------------------------------------------
if __name__ == "__main__":
    print("📋 Estudiantes registrados:")
    print(listar_estudiantes())

    print("\n📘 Historial del estudiante E001:")
    print(historial_estudiante("E001"))

    print("\n📊 KPIs del programa:")
    print(kpi_programa())
