import sqlite3
from pathlib import Path

# Ruta de la base de datos
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "sia.db"

print(f"📘 Conectando a la base de datos: {DB_PATH}")

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    # Revisar columnas existentes
    cur.execute("PRAGMA table_info(Curso);")
    columnas = [r[1] for r in cur.fetchall()]

    # Si la columna no existe, la crea
    if "codigo_alfanumerico" not in columnas:
        cur.execute("ALTER TABLE Curso ADD COLUMN codigo_alfanumerico TEXT;")
        conn.commit()
        print("✅ Columna 'codigo_alfanumerico' agregada correctamente.")
    else:
        print("ℹ️ La columna 'codigo_alfanumerico' ya existe, no se realizó ningún cambio.")
