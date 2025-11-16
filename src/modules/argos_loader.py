import sqlite3
import time
from io import BytesIO

import pandas as pd

from modules.validators import resumen_validacion
from database.upsert import upsert_inscripcion, upsert_curso, registrar_evento
from database.db_init import DB_PATH


# -------------------------------------------------
# CARGA Y VALIDACIÓN DEL EXCEL ARGOS
# -------------------------------------------------
def cargar_y_validar_excel(file_buffer: BytesIO):
    """
    Lee el Excel ARGOS, valida estructura y formatos,
    y retorna (df, resultados dict) o (None, errores dict).
    """
    try:
        df = pd.read_excel(file_buffer, dtype=str)
        df.columns = df.columns.str.strip().str.upper()

        resultados = resumen_validacion(df)
        resultados["total_registros"] = len(df)

        if (
            resultados.get("columnas_validas")
            and resultados.get("notas_validas")
            and resultados.get("periodos_validos")
        ):
            return df, resultados
        else:
            return None, resultados

    except Exception as e:
        return None, {"error": str(e)}


# -------------------------------------------------
# PROCESAMIENTO SIMULADO (modo de prueba)
# -------------------------------------------------
def procesar_argos(df: pd.DataFrame):
    """Simula métricas de procesamiento."""
    total = len(df)
    nuevos = int(total * 0.6)
    actualizados = int(total * 0.35)
    errores = total - (nuevos + actualizados)
    return {
        "total": total,
        "nuevos": nuevos,
        "actualizados": actualizados,
        "errores": errores,
    }


# -------------------------------------------------
# CARGUE REAL A LA BASE DE DATOS
# -------------------------------------------------
def cargar_a_bd(df: pd.DataFrame):
    """
    Inserta/actualiza datos en:
      - Estudiante
      - Curso (incluye código alfanumérico: ALFA + NUMERI)
      - PeriodoAcademico
      - Inscripcion (con snapshot de curso y programa)
    y registra evento en Auditoria.

    🔸 Procesa cursos con NRCS == 'TRANSFERENCIA' asignándoles
       un NRC simbólico 'TRANSF-{ALFA}{NUMERI}'.
    """
    # --- Medición de tiempo real de procesamiento ---
    inicio = time.perf_counter()

    total = len(df)
    insertados = 0
    actualizados = 0
    errores = 0
    transferencias = 0

    df = df.copy()
    df.columns = df.columns.str.upper()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for idx, fila in df.iterrows():
            try:
                # --- Extracción de campos principales ---
                id_estudiante = str(fila.get("ID_ESTUDIANTE", "")).strip()
                nombre_estudiante = str(fila.get("NOMBRE_ESTUDIANTE", "Desconocido")).strip()

                # Código y descripción de programa
                programa_codigo = str(fila.get("PROGRAMA", "")).strip()  # ISUT / ISOF / etc.
                programa_desc = str(fila.get("DESCRIPCION_PROGRAMA", "Pendiente")).strip()

                correo = None  # No viene en ARGOS

                nrc_valor = str(fila.get("NRCS", "")).strip().upper()
                alfa = str(fila.get("ALFA", "")).strip()
                numeri = str(fila.get("NUMERI", "")).strip()
                nombre_curso = str(
                    fila.get("DESCRIPCION") or fila.get("DESCRIPION") or "Curso sin nombre"
                ).strip()

                # --- Detección de cursos de transferencia ---
                if nrc_valor == "TRANSFERENCIA":
                    id_curso = f"TRANSF-{alfa}{numeri or 'GEN'}"
                    transferencias += 1
                else:
                    id_curso = nrc_valor

                # --- Periodo y nota ---
                id_periodo = str(fila.get("PERIODO", "")).strip()
                anio = int(id_periodo[:4]) if len(id_periodo) >= 4 and id_periodo[:4].isdigit() else None
                periodo = int(id_periodo[4:]) if len(id_periodo) > 4 and id_periodo[4:].isdigit() else None

                nota_str = str(fila.get("DEFINITIVA", "0")).replace(",", ".")
                try:
                    nota = float(nota_str)
                except ValueError:
                    nota = 0.0

                # --- Inserciones / actualizaciones ---

                # Estudiante: conservamos programa "actual" como última descripción vista
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Estudiante (id_estudiante, nombre, programa, correo_institucional)
                    VALUES (?, ?, ?, ?)
                    """,
                    (id_estudiante, nombre_estudiante, programa_desc, correo),
                )
                cursor.execute(
                    """
                    UPDATE Estudiante
                       SET nombre = COALESCE(?, nombre),
                           programa = COALESCE(?, programa)
                     WHERE id_estudiante = ?
                    """,
                    (nombre_estudiante or None, programa_desc or None, id_estudiante),
                )

                # Curso (catálogo actual)
                upsert_curso(conn, id_curso, nombre_curso, creditos=None, alfa=alfa, numeri=numeri)

                # Periodo académico
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO PeriodoAcademico (id_periodo, anio, periodo)
                    VALUES (?, ?, ?)
                    """,
                    (id_periodo, anio, periodo),
                )

                # Inscripción (con snapshot de curso y programa)
                accion = upsert_inscripcion(
                    conn,
                    id_estudiante=id_estudiante,
                    id_curso=id_curso,
                    id_periodo=id_periodo,
                    nota=nota,
                    alfa=alfa or None,
                    numeri=numeri or None,
                    nombre_curso=nombre_curso or None,
                    codigo_alfanumerico=(f"{alfa} {numeri}".strip() if (alfa or numeri) else None),
                    programa=programa_codigo or None,
                    descripcion_programa=programa_desc or None,
                )

                if accion == "insertado":
                    insertados += 1
                else:
                    actualizados += 1

            except Exception as e:
                print(f"⚠️ Error procesando fila {idx + 1}: {e}")
                errores += 1

        # --- Fin de procesamiento y cálculo de tiempo ---
        fin = time.perf_counter()
        duracion = fin - inicio

        resumen_txt = (
            f"Cargue ARGOS – {total} registros procesados "
            f"({insertados} nuevos, {actualizados} actualizados, {errores} errores, "
            f"{transferencias} cursos por transferencia) "
            f"en {duracion:.2f} segundos"
        )
        registrar_evento(conn, "coordinador_academico", resumen_txt)
        conn.commit()

    print("📦", resumen_txt)

    return {
        "total": total,
        "nuevos": insertados,
        "actualizados": actualizados,
        "errores": errores,
        "transferencias": transferencias,
        "tiempo_segundos": round(duracion, 2),
    }