import os
import pandas as pd
from io import BytesIO
from src.modules.validators import resumen_validacion

# -------------------------------------------------
# FUNCIÓN PRINCIPAL DE CARGA
# -------------------------------------------------
def cargar_y_validar_excel(file_buffer: BytesIO):
    """
    Carga un archivo Excel ARGOS, aplica validaciones y retorna:
      - DataFrame limpio (si pasa validaciones)
      - Diccionario con resultados de validación
    """
    try:
        # Intentar leer el archivo Excel
        df = pd.read_excel(file_buffer, dtype=str)

        # Estandarizar nombres de columnas (eliminar espacios, mayúsculas)
        df.columns = df.columns.str.strip().str.upper()

        # Aplicar validaciones definidas en validators.py
        resultados = resumen_validacion(df)

        # Añadir el total de registros leídos
        resultados["total_registros"] = len(df)

        # Si todo está correcto, retorna también el DataFrame
        if (
            resultados["columnas_validas"]
            and resultados["notas_validas"]
            and resultados["periodos_validos"]
        ):
            return df, resultados
        else:
            # Si hay errores, devolver None en lugar del DataFrame
            return None, resultados

    except Exception as e:
        return None, {"error": str(e)}

# -------------------------------------------------
# PRUEBA LOCAL
# -------------------------------------------------
if __name__ == "__main__":
    ruta_archivo = "data/argos_samples/ejemplo_argos.xlsx"
    if not os.path.exists(ruta_archivo):
        print(f"⚠️ No se encontró el archivo de ejemplo en: {ruta_archivo}")
    else:
        import pandas as pd
        df = pd.read_excel(ruta_archivo)
        resumen = resumen_validacion(df)
        print("✅ Validación completada:")
        print(resumen)
