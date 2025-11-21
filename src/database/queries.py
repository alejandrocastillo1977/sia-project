import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"


def _connect():
    return sqlite3.connect(DB_PATH)


def obtener_kpis_programa() -> Dict[str, Any]:
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
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT e.id_estudiante,
                   COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                   COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                   e.correo_institucional
            FROM Estudiante e
            ORDER BY e.id_estudiante
            LIMIT ?;
        """,
            (limit,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def buscar_estudiantes(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    q = (query or "").strip()
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if q.isdigit():
            cur.execute(
                """
                SELECT e.id_estudiante,
                       COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                       COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                       e.correo_institucional
                FROM Estudiante e
                WHERE e.id_estudiante = ?
                LIMIT ?;
            """,
                (q, limit),
            )
        else:
            cur.execute(
                """
                SELECT e.id_estudiante,
                       COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                       COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                       e.correo_institucional
                FROM Estudiante e
                WHERE UPPER(e.nombre) LIKE '%' || UPPER(?) || '%'
                ORDER BY e.nombre
                LIMIT ?;
            """,
                (q, limit),
            )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def historial_estudiante(id_estudiante: str) -> List[Dict[str, Any]]:
    """
    Historial del estudiante con preferencia por el snapshot de Inscripcion.
    """
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT 
                i.id_periodo,
                p.anio,
                p.periodo,
                i.id_curso AS nrc,
                COALESCE(NULLIF(TRIM(i.codigo_alfanumerico), ''), c.codigo_alfanumerico) AS codigo_curso,
                COALESCE(NULLIF(TRIM(i.nombre_curso), ''), c.nombre) AS nombre_curso,
                c.codigo_programa AS codigo_programa,
                i.nota,
                i.version_periodo
            FROM Inscripcion i
            LEFT JOIN Curso c ON c.id_curso = i.id_curso
            LEFT JOIN PeriodoAcademico p ON p.id_periodo = i.id_periodo
            WHERE i.id_estudiante = ?
            ORDER BY i.id_periodo ASC, i.id_curso;
        """,
            (id_estudiante,),
        )
        rows = cur.fetchall()
    return [dict(r) for r in rows]


def datos_estudiante(id_estudiante: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT e.id_estudiante,
                   COALESCE(NULLIF(TRIM(e.nombre), ''), 'Desconocido') AS nombre,
                   COALESCE(NULLIF(TRIM(e.programa), ''), 'Pendiente') AS programa,
                   e.correo_institucional
            FROM Estudiante e
            WHERE e.id_estudiante = ?;
        """,
            (id_estudiante,),
        )
        row = cur.fetchone()
    return dict(row) if row else None


from database.db_init import DB_PATH


def obtener_notas_por_umbral(tipo: str, id_periodo: str, umbral: float):
    """
    Retorna inscripciones por umbral, prefiriendo snapshot de Inscripcion.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    operador = "<" if tipo == "bajo" else ">="

    query = f"""
        SELECT 
            e.id_estudiante,
            e.nombre,
            e.programa,
            i.id_curso,
            c.codigo_programa AS codigo_programa,
            COALESCE(NULLIF(TRIM(i.codigo_alfanumerico), ''), c.codigo_alfanumerico) AS codigo_alfanumerico,
            COALESCE(NULLIF(TRIM(i.nombre_curso), ''), c.nombre) AS nombre_curso,
            i.nota,
            i.version_periodo,
            i.id_periodo
        FROM Inscripcion i
        JOIN Estudiante e ON i.id_estudiante = e.id_estudiante
        LEFT JOIN Curso c ON i.id_curso = c.id_curso
        WHERE i.id_periodo = ?
          AND i.nota {operador} ?
        ORDER BY e.nombre ASC;
    """

    cursor.execute(query, (id_periodo, umbral))
    resultados = cursor.fetchall()

    df = [dict(row) for row in resultados]
    conn.close()
    return df


def listar_periodos() -> list[str]:
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT id_periodo FROM PeriodoAcademico ORDER BY id_periodo DESC;")
        rows = [r[0] for r in cur.fetchall()]
    return rows


# --- Auditoría: listar eventos ---
from typing import Optional, List, Dict, Any

# --- Auditoría: listar eventos ---
from typing import Optional, List, Dict, Any


def listar_eventos_auditoria(
    limit: int = 500,
    usuario: Optional[str] = None,  # filtro específico por usuario (substring)
    desde: Optional[str] = None,  # 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'
    hasta: Optional[str] = None,  # 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS'
    filtro: Optional[str] = None,  # 🔹 NUEVO: búsqueda libre en usuario/accion
) -> List[Dict[str, Any]]:
    """
    Devuelve eventos de la tabla Auditoria con filtros opcionales.
    - usuario: substring case-insensitive en la columna 'usuario'
    - filtro:  substring case-insensitive que busca en 'usuario' o 'accion'
    - desde/hasta: se comparan con datetime(fecha_evento)
    - limit: tope de filas
    """
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        sql = """
            SELECT id_evento, usuario, accion, fecha_evento
            FROM Auditoria
            WHERE 1=1
        """
        params: list[Any] = []

        if usuario:
            sql += " AND UPPER(usuario) LIKE '%' || UPPER(?) || '%'"
            params.append(usuario)

        if filtro:
            sql += " AND (UPPER(usuario) LIKE '%' || UPPER(?) || '%' OR UPPER(accion) LIKE '%' || UPPER(?) || '%')"
            params.extend([filtro, filtro])

        if desde:
            sql += " AND datetime(fecha_evento) >= datetime(?)"
            params.append(desde)

        if hasta:
            sql += " AND datetime(fecha_evento) <= datetime(?)"
            params.append(hasta)

        sql += " ORDER BY datetime(fecha_evento) DESC LIMIT ?"
        params.append(int(limit))

        cur.execute(sql, params)
        rows = cur.fetchall()

    return [dict(r) for r in rows]
    