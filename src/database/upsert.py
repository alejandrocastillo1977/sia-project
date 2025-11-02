import sqlite3
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"

def upsert_inscripcion(id_estudiante, id_curso, id_periodo, nota):
    """
    Inserta o actualiza una inscripción según la clave (id_estudiante, id_curso, id_periodo).
    Si existe, actualiza la nota y aumenta la versión.
    Si no existe, inserta nuevo registro.
    """

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Verificar si ya existe la inscripción
        cursor.execute("""
            SELECT id_inscripcion, version_periodo FROM Inscripcion
            WHERE id_estudiante = ? AND id_curso = ? AND id_periodo = ?
        """, (id_estudiante, id_curso, id_periodo))

        registro = cursor.fetchone()

        if registro:
            id_inscripcion, version_actual = registro
            nueva_version = version_actual + 1
            cursor.execute("""
                UPDATE Inscripcion
                SET nota = ?, version_periodo = ?
                WHERE id_inscripcion = ?
            """, (nota, nueva_version, id_inscripcion))
            print(f"🔁 Registro actualizado (versión {nueva_version}).")

        else:
            cursor.execute("""
                INSERT INTO Inscripcion (id_estudiante, id_curso, id_periodo, nota)
                VALUES (?, ?, ?, ?)
            """, (id_estudiante, id_curso, id_periodo, nota))
            print("✅ Nuevo registro insertado.")

        conn.commit()

def test_upsert():
    """Pequeña prueba manual del UPSERT."""
    # Datos de prueba
    upsert_inscripcion("E001", "CURS101", "20251", 4.5)
    upsert_inscripcion("E001", "CURS101", "20251", 3.8)  # Debería actualizar

if __name__ == "__main__":
    test_upsert()
