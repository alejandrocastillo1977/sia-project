import sqlite3
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"


def registrar_evento(conn: sqlite3.Connection, usuario: str, accion: str) -> None:
    """
    Registra un evento en la tabla Auditoria.
    OJO: el esquema oficial usa columnas (usuario, accion, fecha_evento).
    """
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


def upsert_inscripcion(conn: sqlite3.Connection, id_estudiante: str, id_curso: str, id_periodo: str, nota: float) -> str:
    """
    Inserta o actualiza una inscripción según la clave (id_estudiante, id_curso, id_periodo)
    usando la MISMA conexión (evita database locked).
    Retorna 'insertado' o 'actualizado' para conteos.
    """
    cursor = conn.cursor()

    # ¿Existe ya la inscripción?
    cursor.execute(
        """
        SELECT id_inscripcion, version_periodo
        FROM Inscripcion
        WHERE id_estudiante = ? AND id_curso = ? AND id_periodo = ?
        """,
        (id_estudiante, id_curso, id_periodo),
    )
    registro = cursor.fetchone()

    if registro:
        id_inscripcion, version_actual = registro
        nueva_version = (version_actual or 1) + 1
        cursor.execute(
            """
            UPDATE Inscripcion
               SET nota = ?, version_periodo = ?
             WHERE id_inscripcion = ?
            """,
            (nota, nueva_version, id_inscripcion),
        )
        return "actualizado"
    else:
        cursor.execute(
            """
            INSERT INTO Inscripcion (id_estudiante, id_curso, id_periodo, nota)
            VALUES (?, ?, ?, ?)
            """,
            (id_estudiante, id_curso, id_periodo, nota),
        )
        return "insertado"


# ---- Prueba local opcional ----
if __name__ == "__main__":
    with sqlite3.connect(DB_PATH) as _conn:
        accion = upsert_inscripcion(_conn, "E001", "CURS101", "20251", 4.5)
        print("Acción:", accion)
        registrar_evento(_conn, "tester", "Prueba de auditoría desde upsert.py")
