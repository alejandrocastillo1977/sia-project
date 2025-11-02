import sqlite3
from pathlib import Path

# Definir rutas base
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"
SCHEMA_PATH = BASE_DIR / "src" / "database" / "schema.sql"

def create_database():
    """Crea la base de datos SQLite desde el archivo schema.sql."""
    if DB_PATH.exists():
        print(f"🔸 Base de datos ya existe: {DB_PATH}")
        return

    # Crear carpeta /data si no existe
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Leer esquema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    # Conectar y ejecutar
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema_sql)

    print(f"✅ Base de datos creada correctamente en: {DB_PATH}")

if __name__ == "__main__":
    create_database()
