import os
import sqlite3
import pandas as pd
from io import BytesIO

from modules.validators import resumen_validacion
from database.upsert import upsert_inscripcion, registrar_evento
from database.db_init import DB_PATH


# -------------------------------------------------
# CARGA Y VALIDACIÓN DEL EXCEL
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
# PROCESAMIENTO SIMULADO (para modo de prueba)
# -------------------------------------------------
def procesar_argos(df: pd.DataFrame):
    """
    Simula el procesamiento del archivo ARGOS sin afectar la base de datos.
    Retorna métricas de ejemplo coherentes con el tamaño del dataset.
    """
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
# CARGUE REAL A LA BASE DE DATOS (con 1 sola conexión)
# -------------------------------------------------
def cargar_a_bd(df: pd.DataFrame):
    """
    Inserta/actualiza datos en:
      - Estudiante
      - Curso
      - PeriodoAcademico
      - Inscripcion  (vía upsert_inscripcion con la MISMA conexión)
    y registra evento en Auditoria.
    """
    total = len(df)
    insertados = 0
    actualizados = 0
    errores = 0

    df = df.copy()
    df.columns = df.columns.str.upper()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for idx, fila in df.iterrows():
            try:
                id_estudiante = str(fila.get("ID_ESTUDIANTE", "")).strip()
                nombre_estudiante = str(fila.get("NOMBRE_ESTUDIANTE", "Desconocido")).strip()
                programa = str(fila.get("DESCRIPCION_PROGRAMA", "Pendiente")).strip()
                correo = None  # No viene en ARGOS original

                id_curso = str(fila.get("NRCS", "")).strip() or str(fila.get("ALFA", "")).strip()
                nombre_curso = str(fila.get("DESCRIPCION", "Curso sin nombre")).strip()

                id_periodo = str(fila.get("PERIODO", "")).strip()
                anio = int(id_periodo[:4]) if len(id_periodo) >= 4 and id_periodo[:4].isdigit() else None
                periodo = int(id_periodo[4:]) if len(id_periodo) > 4 and id_periodo[4:].isdigit() else None

                nota_str = str(fila.get("DEFINITIVA", "0")).replace(",", ".")
                try:
                    nota = float(nota_str)
                except ValueError:
                    nota = 0.0

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Estudiante (id_estudiante, nombre, programa, correo_institucional)
                    VALUES (?, ?, ?, ?)
                    """,
                    (id_estudiante, nombre_estudiante, programa, correo),
                )

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO Curso (id_curso, nombre)
                    VALUES (?, ?)
                    """,
                    (id_curso, nombre_curso),
                )

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO PeriodoAcademico (id_periodo, anio, periodo)
                    VALUES (?, ?, ?)
                    """,
                    (id_periodo, anio, periodo),
                )

                accion = upsert_inscripcion(conn, id_estudiante, id_curso, id_periodo, nota)
                if accion == "insertado":
                    insertados += 1
                else:
                    actualizados += 1

            except Exception as e:
                print(f"⚠️ Error procesando fila {idx}: {e}")
                errores += 1

        resumen_txt = f"Cargue ARGOS – {total} registros procesados ({actualizados} actualizados, {errores} errores)"
        registrar_evento(conn, "coordinador_academico", resumen_txt)
        conn.commit()

    return {
        "total": total,
        "nuevos": insertados,
        "actualizados": actualizados,
        "errores": errores,
    }
