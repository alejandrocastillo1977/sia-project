from typing import Any

from modules.load_data import (
    obtener_malla_isov_virtual,
    validar_y_normalizar_malla,
    mapear_malla_con_historico,
)
from database import queries


def listar_programas_soportados() -> list[dict]:
    """
    Devuelve la lista de programas para los cuales existe lógica de malla soportada.

    Primera versión:
    - Debe incluir al menos el programa de Ingeniería de Software (ISOF),
      identificando:
      - codigo_programa: str (por ejemplo, "ISOF")
      - nombre_programa: str (por ejemplo, "Ingeniería de Software – UNIMINUTO Virtual")
    """
    # Usamos la malla embebida y normalizada de ISOF como única fuente de verdad
    malla_isof = validar_y_normalizar_malla(obtener_malla_isov_virtual())
    return [
        {
            "codigo_programa": malla_isof["codigo_programa"],
            "nombre_programa": malla_isof.get("programa")
            or malla_isof.get("nombre_malla")
            or malla_isof["codigo_programa"],
        }
    ]


def obtener_malla_para_programa(
    codigo_programa: str,
) -> dict[str, Any]:
    """
    Devuelve la malla curricular normalizada para el programa indicado.

    Primera versión:
    - Para codigo_programa == "ISOF", debe reutilizar la malla embebida y
      la lógica de normalización existente en load_data.py
      (por ejemplo, obtener_malla_isov_virtual + validar_y_normalizar_malla).

    Estructura esperada (resumen):
    - codigo_programa: str
    - nombre_malla: str
    - programa: str
    - creditos_totales: int
    - plan: list[dict] con:
      - cuatrimestre: int
      - cursos: list[dict] con:
        - codigo: str | list[str]
        - nombre: str
        - creditos: int
    """
    codigo = (codigo_programa or "").strip().upper()
    if codigo == "ISOF":
        # Normalizamos siempre la malla embebida de ISOF para garantizar estructura consistente
        return validar_y_normalizar_malla(obtener_malla_isov_virtual())

    raise NotImplementedError(
        f"No hay lógica de malla soportada aún para el programa '{codigo_programa}'"
    )


def _resumen_creditos_malla(malla_cruzada: list[dict]) -> dict[str, int]:
    resumen = {"APROBADO": 0, "PERDIDO": 0, "TRANSFERENCIA": 0, "PENDIENTE": 0}
    for bloque in malla_cruzada or []:
        for curso in bloque.get("cursos", []) or []:
            estado = str(curso.get("estado", "")).upper()
            creditos_raw = curso.get("creditos")
            try:
                creditos = int(creditos_raw) if creditos_raw is not None else 0
            except (TypeError, ValueError):
                creditos = 0
            if estado in resumen:
                resumen[estado] += creditos
    return resumen


def calcular_avance_estudiantes_programa(
    historial_programa: list[dict],
    malla_programa: dict[str, Any],
) -> list[dict]:
    """
    Calcula el avance en créditos de todos los estudiantes de un programa.

    Entradas:
    - historial_programa: lista de dicts devuelta por
      queries.obtener_historial_estudiantes_por_programa(codigo_programa).
    - malla_programa: estructura de malla devuelta por obtener_malla_para_programa.

    Lógica (cuando se implemente):
    - Agrupar por id_estudiante.
    - Para cada estudiante, cruzar malla + historial usando mapear_malla_con_historico
      de load_data.py.
    - Calcular créditos aprobados (APROBADO + TRANSFERENCIA), perdidos y pendientes.
    - Calcular el porcentaje de avance: (cred_aprob_transf * 100.0 / cred_totales_malla).

    Cada dict de salida debe incluir:
    - id_estudiante: str
    - nombre: str
    - programa: str
    - codigo_programa: str
    - cred_aprob_transf: int
    - cred_perdidos: int
    - cred_pendientes: int
    - cred_totales_malla: int
    - porc_aproba_malla: float
    """
    if not historial_programa:
        return []

    # Agrupar historial por estudiante
    historial_por_estudiante: dict[str, list[dict]] = {}
    for reg in historial_programa:
        id_est = str(reg.get("id_estudiante", "") or "").strip()
        if not id_est:
            continue
        historial_por_estudiante.setdefault(id_est, []).append(reg)

    creditos_totales_raw = malla_programa.get("creditos_totales")
    try:
        creditos_totales_base = int(creditos_totales_raw)
    except (TypeError, ValueError):
        creditos_totales_base = 0

    resultados: list[dict] = []

    for id_estudiante, hist_est in historial_por_estudiante.items():
        # Cruce de malla con histórico individual
        malla_cruzada = mapear_malla_con_historico(hist_est, malla_programa)
        resumen = _resumen_creditos_malla(malla_cruzada)

        cred_aprob_transf = resumen["APROBADO"] + resumen["TRANSFERENCIA"]
        cred_perdidos = resumen["PERDIDO"]
        cred_pendientes = resumen["PENDIENTE"]

        cred_totales_malla = creditos_totales_base
        if not cred_totales_malla or cred_totales_malla <= 0:
            cred_totales_malla = (
                resumen["APROBADO"]
                + resumen["TRANSFERENCIA"]
                + resumen["PERDIDO"]
                + resumen["PENDIENTE"]
            )

        if cred_totales_malla and cred_totales_malla > 0:
            porc_aproba_malla = (cred_aprob_transf * 100.0) / float(cred_totales_malla)
        else:
            porc_aproba_malla = 0.0

        # Tomamos datos básicos del primer registro del historial de este estudiante
        base = hist_est[0]
        nombre = base.get("nombre", "")
        programa = base.get("programa", "")
        codigo_programa = base.get("codigo_programa") or malla_programa.get(
            "codigo_programa", ""
        )

        resultados.append(
            {
                "id_estudiante": id_estudiante,
                "nombre": str(nombre),
                "programa": str(programa),
                "codigo_programa": str(codigo_programa or ""),
                "cred_aprob_transf": int(cred_aprob_transf),
                "cred_perdidos": int(cred_perdidos),
                "cred_pendientes": int(cred_pendientes),
                "cred_totales_malla": int(cred_totales_malla or 0),
                "porc_aproba_malla": float(porc_aproba_malla),
            }
        )

    return resultados


def filtrar_porcentaje_minimo(
    lista_avance: list[dict],
    porcentaje_min: float,
) -> list[dict]:
    """
    Filtra la lista de avance dejando solo los estudiantes cuyo porcentaje
    de avance en créditos es mayor o igual a porcentaje_min.

    - lista_avance: salida de calcular_avance_estudiantes_programa.
    - porcentaje_min: valor numérico entre 0 y 100.
    """
    try:
        umbral = float(porcentaje_min)
    except (TypeError, ValueError):
        umbral = 0.0

    filtrados: list[dict] = []
    for reg in lista_avance or []:
        valor = reg.get("porc_aproba_malla")
        try:
            porc = float(valor)
        except (TypeError, ValueError):
            porc = 0.0
        if porc >= umbral:
            filtrados.append(reg)

    return filtrados


def generar_reporte_avance_creditos(
    codigo_programa: str,
    porcentaje_min: float,
) -> dict[str, Any]:
    """
    Servicio de alto nivel que orquesta todo el flujo del reporte de avance.

    Flujo (cuando se implemente):
    - malla = obtener_malla_para_programa(codigo_programa)
    - historial = queries.obtener_historial_estudiantes_por_programa(codigo_programa)
    - todos = calcular_avance_estudiantes_programa(historial, malla)
    - filtrados = filtrar_porcentaje_minimo(todos, porcentaje_min)

    Debe devolver un dict con:
    - codigo_programa: str
    - nombre_programa: str
    - porcentaje_minimo: float
    - total_estudiantes_programa: int
    - total_con_avance_mayor_igual: int
    - promedio_porcentaje_filtrados: float | None
    - estudiantes_todos: list[dict]
    - estudiantes_filtrados: list[dict]
    """
    # Normalizar código de programa
    cod = (codigo_programa or "").strip().upper()

    # Obtener malla y nombre legible del programa
    malla = obtener_malla_para_programa(cod)
    nombre_programa = (
        malla.get("programa")
        or malla.get("nombre_malla")
        or malla.get("codigo_programa")
        or cod
    )
    nombre_programa = str(nombre_programa)

    # Obtener historial masivo de inscripciones del programa
    historial = queries.obtener_historial_estudiantes_por_programa(cod)

    # Calcular avance de todos los estudiantes
    estudiantes_todos = calcular_avance_estudiantes_programa(historial, malla)

    # Normalizar porcentaje mínimo
    try:
        porcentaje_minimo = float(porcentaje_min)
    except (TypeError, ValueError):
        porcentaje_minimo = 0.0

    estudiantes_filtrados = filtrar_porcentaje_minimo(
        estudiantes_todos, porcentaje_minimo
    )

    total_estudiantes_programa = len(estudiantes_todos)
    total_con_avance_mayor_igual = len(estudiantes_filtrados)

    # Calcular promedio de porcentaje de los filtrados
    promedio_porcentaje_filtrados: float | None
    if estudiantes_filtrados:
        suma = 0.0
        count = 0
        for est in estudiantes_filtrados:
            valor = est.get("porc_aproba_malla")
            try:
                porc = float(valor)
            except (TypeError, ValueError):
                porc = 0.0
            suma += porc
            count += 1
        promedio_porcentaje_filtrados = suma / count if count > 0 else None
    else:
        promedio_porcentaje_filtrados = None

    return {
        "codigo_programa": str(cod),
        "nombre_programa": nombre_programa,
        "porcentaje_minimo": float(porcentaje_minimo),
        "total_estudiantes_programa": int(total_estudiantes_programa),
        "total_con_avance_mayor_igual": int(total_con_avance_mayor_igual),
        "promedio_porcentaje_filtrados": (
            None
            if promedio_porcentaje_filtrados is None
            else float(promedio_porcentaje_filtrados)
        ),
        "estudiantes_todos": estudiantes_todos,
        "estudiantes_filtrados": estudiantes_filtrados,
    }
