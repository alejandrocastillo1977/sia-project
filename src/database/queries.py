import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"


def _connect():
    return sqlite3.connect(DB_PATH)


def obtener_kpis_programa() -> Dict[str, Any]:
    """
    Retorna KPIs globales del programa:
      - total_estudiantes
      - promedio_general (promedio de 'nota' sobre Inscripcion)
      - total_cursos
      - total_inscripciones
    """
    with _connect() as conn:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM Estudiante;")
        total_estudiantes = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM Curso;")
        total_cursos = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM Inscripcion;")
        total_inscripciones = cur.fetchone()[0] or 0

        cur.execute("SELECT AVG(nota) FROM Inscripcion WHERE nota IS NOT NULL;")
        prom = cur.fetchone()[0]
        promedio_general = round(prom, 2) if prom is not None else None

    return {
        "total_estudiantes": total_estudiantes,
        "promedio_general": promedio_general,
        "total_cursos": total_cursos,
        "total_inscripciones": total_inscripciones,
    }


def listar_estudiantes(limit: int = 200) -> List[Dict[str, Any]]:
    """
    Lista básica de estudiantes para el tablero.
    """
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id_estudiante,
                   COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                   COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                   e.correo_institucional
            FROM Estudiante e
            ORDER BY e.id_estudiante
            LIMIT ?;
        """, (limit,))
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def buscar_estudiantes(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Búsqueda por ID exacto o nombre contiene (case-insensitive).
    """
    q = (query or "").strip()
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if q.isdigit():
            # prioriza coincidencia por ID
            cur.execute("""
                SELECT e.id_estudiante,
                       COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                       COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                       e.correo_institucional
                FROM Estudiante e
                WHERE e.id_estudiante = ?
                LIMIT ?;
            """, (q, limit))
        else:
            cur.execute("""
                SELECT e.id_estudiante,
                       COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                       COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                       e.correo_institucional
                FROM Estudiante e
                WHERE UPPER(e.nombre) LIKE '%' || UPPER(?) || '%'
                ORDER BY e.nombre
                LIMIT ?;
            """, (q, limit))
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def historial_estudiante(id_estudiante: str) -> List[Dict[str, Any]]:
    """
    Retorna el historial académico (inscripciones) de un estudiante con joins a Curso y PeriodoAcademico.
    """
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT i.id_periodo,
                   p.anio,
                   p.periodo,
                   i.id_curso,
                   c.nombre AS nombre_curso,
                   i.nota,
                   i.version_periodo
            FROM Inscripcion i
            LEFT JOIN Curso c ON c.id_curso = i.id_curso
            LEFT JOIN PeriodoAcademico p ON p.id_periodo = i.id_periodo
            WHERE i.id_estudiante = ?
            ORDER BY i.id_periodo DESC, i.id_curso;
        """, (id_estudiante,))
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def datos_estudiante(id_estudiante: str) -> Optional[Dict[str, Any]]:
    """
    Datos de cabecera del estudiante.
    """
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id_estudiante,
                   COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                   COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                   e.correo_institucional
            FROM Estudiante e
            WHERE e.id_estudiante = ?;
        """, (id_estudiante,))
        row = cur.fetchone()
    return dict(row) if row else None
