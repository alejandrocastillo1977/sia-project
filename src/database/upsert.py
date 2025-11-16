import sqlite3
from pathlib import Path

# ======================================================
# CONFIGURACIÓN DE RUTA BASE
# ======================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"


# ======================================================
# FUNCIÓN: REGISTRAR EVENTO EN AUDITORÍA
# ======================================================
def registrar_evento(conn: sqlite3.Connection, usuario: str, accion: str) -> None:
    """Registra un evento en la tabla Auditoria."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Auditoria (usuario, accion)
            VALUES (?, ?)
            """,
            (usuario, accion),
        )
        conn.commit()
        print(f"🧾 Evento registrado en auditoría: {accion}")
    except Exception as e:
        print(f"⚠️ Error registrando evento en auditoría: {e}")


# ======================================================
# FUNCIÓN: UPSERT CURSO (CON CÓDIGO ALFANUMÉRICO)
# ======================================================
def upsert_curso(
    conn: sqlite3.Connection,
    id_curso: str,
    nombre: str,
    creditos: int = None,
    alfa: str = None,
    numeri: str = None,
) -> None:
    """
    Inserta o actualiza un curso con su código alfanumérico.
    - id_curso: NRC (columna NRCS)
    - codigo_alfanumerico: concatenación de ALFA + NUMERI
    Admite id_curso simbólicos como TRANSF-XXXX (transferencias).
    """
    if not id_curso:
        print("⚠️ No se puede registrar curso sin 'id_curso'.")
        return

    # 🔹 Permitir NRC simbólico (transferencias)
    id_curso = str(id_curso).strip().upper()

    codigo_alfanumerico = None
    alfa = (alfa or "").strip()
    numeri = (numeri or "").strip()
    if alfa and numeri:
        codigo_alfanumerico = f"{alfa} {numeri}"
    elif alfa:
        codigo_alfanumerico = alfa
    elif numeri:
        codigo_alfanumerico = numeri

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO Curso (id_curso, nombre, creditos, codigo_alfanumerico)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id_curso) DO UPDATE SET
            nombre = excluded.nombre,
            creditos = excluded.creditos,
            codigo_alfanumerico = excluded.codigo_alfanumerico;
        """,
        (id_curso, nombre, creditos, codigo_alfanumerico),
    )
    conn.commit()
    print(f"📘 Curso actualizado/insertado: {id_curso} → {codigo_alfanumerico or 'N/A'}")


# ======================================================
# FUNCIÓN: UPSERT INSCRIPCIÓN (con snapshot del curso y programa)
# ======================================================
def upsert_inscripcion(
    conn: sqlite3.Connection,
    id_estudiante: str,
    id_curso: str,
    id_periodo: str,
    nota: float,
    *,
    alfa: str | None = None,
    numeri: str | None = None,
    nombre_curso: str | None = None,
    codigo_alfanumerico: str | None = None,
    programa: str | None = None,
    descripcion_programa: str | None = None,
) -> str:
    """
    Inserta o actualiza una inscripción según la clave (id_estudiante, id_curso, id_periodo)
    usando la MISMA conexión.

    🔹 Ahora también guarda un snapshot del programa (programa, descripcion_programa)
    junto con el snapshot del curso.
    """
    cursor = conn.cursor()

    id_estudiante = (id_estudiante or "").strip()
    id_curso = (id_curso or "").strip().upper()
    id_periodo = (id_periodo or "").strip()

    if not (id_estudiante and id_curso and id_periodo):
        raise ValueError("Inscripción inválida: faltan id_estudiante, id_curso o id_periodo.")

    alfa = (alfa or "").strip()
    numeri = (numeri or "").strip()
    programa = (programa or "").strip()
    descripcion_programa = (descripcion_programa or "").strip()

    if not codigo_alfanumerico:
        if alfa and numeri:
            codigo_alfanumerico = f"{alfa} {numeri}"
        elif alfa:
            codigo_alfanumerico = alfa
        elif numeri:
            codigo_alfanumerico = numeri

    cursor.execute(
        """
        SELECT id_inscripcion,
               version_periodo,
               alfa,
               numeri,
               codigo_alfanumerico,
               nombre_curso,
               programa,
               descripcion_programa
          FROM Inscripcion
         WHERE id_estudiante = ? AND id_curso = ? AND id_periodo = ?
        """,
        (id_estudiante, id_curso, id_periodo),
    )
    registro = cursor.fetchone()

    if registro:
        (
            id_inscripcion,
            version_actual,
            alfa_db,
            numeri_db,
            codigo_db,
            nombre_db,
            programa_db,
            desc_prog_db,
        ) = registro
        nueva_version = (version_actual or 1) + 1

        set_alfa = alfa_db or alfa or None
        set_numeri = numeri_db or numeri or None
        set_codigo = codigo_db or codigo_alfanumerico or None
        set_nombre = nombre_db or (nombre_curso or None)
        set_programa = programa_db or programa or None
        set_desc_prog = desc_prog_db or descripcion_programa or None

        cursor.execute(
            """
            UPDATE Inscripcion
               SET nota = ?,
                   version_periodo = ?,
                   alfa = COALESCE(alfa, ?),
                   numeri = COALESCE(numeri, ?),
                   codigo_alfanumerico = COALESCE(codigo_alfanumerico, ?),
                   nombre_curso = COALESCE(nombre_curso, ?),
                   programa = COALESCE(programa, ?),
                   descripcion_programa = COALESCE(descripcion_programa, ?)
             WHERE id_inscripcion = ?
            """,
            (
                nota,
                nueva_version,
                set_alfa,
                set_numeri,
                set_codigo,
                set_nombre,
                set_programa,
                set_desc_prog,
                id_inscripcion,
            ),
        )
        conn.commit()
        print(f"🔁 Actualizada inscripción de {id_estudiante} en curso {id_curso}.")
        return "actualizado"

    else:
        cursor.execute(
            """
            INSERT INTO Inscripcion
                (id_estudiante, id_curso, id_periodo, nota,
                 alfa, numeri, codigo_alfanumerico, nombre_curso,
                 programa, descripcion_programa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                id_estudiante,
                id_curso,
                id_periodo,
                nota,
                alfa or None,
                numeri or None,
                codigo_alfanumerico or None,
                nombre_curso or None,
                programa or None,
                descripcion_programa or None,
            ),
        )
        conn.commit()
        print(f"🆕 Nueva inscripción de {id_estudiante} en curso {id_curso}.")
        return "insertado"