from __future__ import annotations

from typing import Any, Dict, List


MALLA_ISOV_VIRTUAL: Dict[str, Any] = {
    "programa": "Ingeniería de Software – UNIMINUTO Virtual",
    "creditos_totales": 140,
    "plan": [
        {
            "cuatrimestre": 1,
            "cursos": [
                {"codigo": "INFO 1030", "nombre": "Habilidades Digitales para el Aprendizaje", "creditos": 3},
                {"codigo": "LENG 1040", "nombre": "Lectura y Escritura en el Contexto Digital", "creditos": 3},
                {"codigo": "UVFI D022", "nombre": "Precálculo", "creditos": 3},
                {"codigo": "FHUM 1010", "nombre": "Proyecto de Vida", "creditos": 2},
                {"codigo": "ISOF V003", "nombre": "Introducción a la Ingeniería de Software", "creditos": 3},
            ],
        },
        {
            "cuatrimestre": 2,
            "cursos": [
                {"codigo": "UVFI V011", "nombre": "Álgebra Lineal", "creditos": 3},
                {"codigo": "ISOF V013", "nombre": "Desarrollo de Software Orientado a Objetos", "creditos": 3},
                {"codigo": "ISUD D063", "nombre": "Infraestructura de TI", "creditos": 3},
                {"codigo": "FHUM 1020", "nombre": "Cátedra Minuto de Dios", "creditos": 2},
            ],
        },
        {
            "cuatrimestre": 3,
            "cursos": [
                {"codigo": "UVFI V051", "nombre": "Matemáticas Discretas", "creditos": 3},
                {"codigo": "UVFI D031", "nombre": "Cálculo Diferencial", "creditos": 3},
                {"codigo": "ISOF V023", "nombre": "Estructuras de Datos y Análisis de Algoritmos", "creditos": 3},
                {"codigo": "ISOF V033", "nombre": "Análisis y Diseño de Software", "creditos": 3},
                {"codigo": "ISOF V043", "nombre": "Sistemas de Gestión de Bases de Datos", "creditos": 3},
            ],
        },
        {
            "cuatrimestre": 4,
            "cursos": [
                {"codigo": "UVFI D061", "nombre": "Cálculo Integral", "creditos": 3},
                {"codigo": "ISOF V053", "nombre": "Ingeniería de Software Avanzada", "creditos": 3},
                {"codigo": "ISOF V063", "nombre": "Desarrollo de Software Orientado a la Web", "creditos": 3},
                {"codigo": "ISOF V073", "nombre": "Data Warehouse y Minería de Datos", "creditos": 3},
                {"codigo": "ISUD D103", "nombre": "Sistemas Operativos", "creditos": 3},
            ],
        },
        {
            "cuatrimestre": 5,
            "cursos": [
                {"codigo": "UVFI D041", "nombre": "Física Mecánica", "creditos": 3},
                {"codigo": "FHUM 1120", "nombre": "Constitución Política", "creditos": 2},
                {"codigo": "ISOF V083", "nombre": "Diseño de Interfaces", "creditos": 3},
                {"codigo": "ISOF V093", "nombre": "Inteligencia de Negocios", "creditos": 3},
            ],
        },
        {
            "cuatrimestre": 6,
            "cursos": [
                {"codigo": "UVFI V021", "nombre": "Ecuaciones Diferenciales", "creditos": 3},
                {"codigo": "ETIC 190", "nombre": "Ética Profesional", "creditos": 2},
                {
                    "codigo": ["ADMI 1070", "ADMI 2000"],
                    "nombre": "Emprendimiento",
                    "creditos": 3,
                },
                {
                    "codigo": "ISOF V103",
                    "nombre": "Pruebas de Software y Aseguramiento de la Calidad",
                    "creditos": 3,
                },
                {"codigo": "ISOF V113", "nombre": "Infraestructura en la Nube", "creditos": 3},
            ],
        },
        {
            "cuatrimestre": 7,
            "cursos": [
                {"codigo": "UVFI D141", "nombre": "Física Electromagnética", "creditos": 3},
                {"codigo": "ISOF V123", "nombre": "Seguridad en el Desarrollo de Software", "creditos": 3},
                {
                    "codigo": "ISOF V133",
                    "nombre": "Desarrollo de Software en Plataformas Móviles",
                    "creditos": 3,
                },
                {
                    "codigo": "ISOF V143",
                    "nombre": "Ethical Hacking y Seguridad de la Información",
                    "creditos": 3,
                },
                {
                    "codigo": "ISOF V004",
                    "nombre": "Electiva Profesional Complementaria I (CPC)",
                    "creditos": 3,
                },
            ],
        },
        {
            "cuatrimestre": 8,
            "cursos": [
                {"codigo": "UVFI V031", "nombre": "Probabilidad y Estadística", "creditos": 3},
                {"codigo": "PRAC 1010", "nombre": "Práctica en Responsabilidad Social", "creditos": 3},
                {"codigo": "ISOF V153", "nombre": "Computación Bioinspirada", "creditos": 3},
                {
                    "codigo": "ISOF V163",
                    "nombre": "Inteligencia Artificial y Sistemas Inteligentes",
                    "creditos": 3,
                },
                {
                    "codigo": "ISOF V014",
                    "nombre": "Electiva Profesional Complementaria II (CPC)",
                    "creditos": 3,
                },
            ],
        },
        {
            "cuatrimestre": 9,
            "cursos": [
                {"codigo": "UVFI V041", "nombre": "Geometría", "creditos": 3},
                {
                    "codigo": "ISOF V173",
                    "nombre": "Gerencia de Proyectos de Software",
                    "creditos": 3,
                },
                {"codigo": "ISOF V183", "nombre": "Machine Learning", "creditos": 3},
                {
                    "codigo": "ISOF V193",
                    "nombre": "Plataformas de Desarrollo de Software",
                    "creditos": 3,
                },
                {"codigo": "UVFI V061", "nombre": "Fundamentos de Investigación", "creditos": 3},
            ],
        },
        {
            "cuatrimestre": 10,
            "cursos": [
                {
                    "codigo": "ISOF V203",
                    "nombre": "Administración y Gestión de la Configuración de Software",
                    "creditos": 3,
                },
                {"codigo": "UVFI V071", "nombre": "Metodología de la Investigación", "creditos": 3},
                {
                    "codigo": "ISOF V024",
                    "nombre": "Electiva Profesional Complementaria III (CPC)",
                    "creditos": 3,
                },
                {"codigo": "ISOF V034", "nombre": "Práctica Profesional", "creditos": 6},
            ],
        },
    ],
}


def obtener_malla_isov_virtual() -> Dict[str, Any]:
    """Devuelve la malla curricular embebida de Ingeniería de Software – UNIMINUTO Virtual."""

    return MALLA_ISOV_VIRTUAL


def _clasificar_estado_inscripcion(registro: Dict[str, Any]) -> str:
    """Clasifica una inscripción individual como APROBADO, PERDIDO o TRANSFERENCIA.

    Se asume:
    - TRANSFERENCIA si el id_curso/nrc comienza por "TRANSF-".
    - APROBADO si la nota es >= 3.0.
    - PERDIDO si la nota es < 3.0.
    """

    nrc = str(registro.get("nrc", "")).upper().strip()
    nota = registro.get("nota")

    if nrc.startswith("TRANSF-"):
        return "TRANSFERENCIA"

    try:
        nota_val = float(nota) if nota is not None else 0.0
    except (TypeError, ValueError):
        nota_val = 0.0

    if nota_val >= 3.0:
        return "APROBADO"

    return "PERDIDO"


def _estado_global_curso(registros: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Dado el conjunto de inscripciones de un curso, devuelve el estado consolidado.

    La prioridad es:
    TRANSFERENCIA > APROBADO > PERDIDO.
    También devuelve la última nota y el último periodo (por id_periodo).
    """

    if not registros:
        return {"estado": "PENDIENTE", "nota": None, "id_periodo": None}

    prioridad = {"TRANSFERENCIA": 3, "APROBADO": 2, "PERDIDO": 1}

    mejor_estado = "PERDIDO"
    mejor_registro: Dict[str, Any] | None = None

    for reg in registros:
        estado = _clasificar_estado_inscripcion(reg)
        if prioridad.get(estado, 0) > prioridad.get(mejor_estado, 0):
            mejor_estado = estado
            mejor_registro = reg
        elif prioridad.get(estado, 0) == prioridad.get(mejor_estado, 0):
            if mejor_registro is None or str(reg.get("id_periodo", "")) > str(
                mejor_registro.get("id_periodo", "")
            ):
                mejor_registro = reg

    if mejor_registro is None:
        return {"estado": "PENDIENTE", "nota": None, "id_periodo": None}

    return {
        "estado": mejor_estado,
        "nota": mejor_registro.get("nota"),
        "id_periodo": mejor_registro.get("id_periodo"),
    }


def mapear_malla_con_historico(
    historial: List[Dict[str, Any]],
    malla: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Cruza la malla curricular con el histórico del estudiante.

    Parameters
    ----------
    historial:
        Lista de dicts tal como la retorna [database.queries.historial_estudiante](cci:1://file:///d:/sia-project/src/database/queries.py:84:0-108:34).
    malla:
        Estructura de malla. Si es None, se usa la malla embebida de Ingeniería de Software.

    Returns
    -------
    list of dict
        Una lista de cuatrimestres. Cada elemento tiene:
        - cuatrimestre
        - cursos: lista de dicts con `codigo`, `nombre`, `creditos`, `estado`, `nota`, `id_periodo`.
    """

    if malla is None:
        malla = MALLA_ISOV_VIRTUAL

    indice: Dict[str, List[Dict[str, Any]]] = {}
    for reg in historial:
        codigo_hist = str(reg.get("codigo_curso", "")).upper().strip()
        if not codigo_hist:
            continue
        indice.setdefault(codigo_hist, []).append(reg)

    resultado: List[Dict[str, Any]] = []

    for bloque in malla.get("plan", []):
        cuat = int(bloque.get("cuatrimestre", 0))
        cursos_bloque: List[Dict[str, Any]] = []

        for curso in bloque.get("cursos", []):
            cod_raw = curso.get("codigo")
            if isinstance(cod_raw, list):
                codigos_malla = [str(c).upper().strip() for c in cod_raw]
                codigo_mostrar = codigos_malla[0]
            else:
                codigo_mostrar = str(cod_raw).upper().strip()
                codigos_malla = [codigo_mostrar]

            registros_curso: List[Dict[str, Any]] = []
            for alias in codigos_malla:
                registros_curso.extend(indice.get(alias, []))

            estado_info = _estado_global_curso(registros_curso)

            cursos_bloque.append(
                {
                    "codigo": codigo_mostrar,
                    "nombre": curso.get("nombre"),
                    "creditos": curso.get("creditos"),
                    "estado": estado_info["estado"],
                    "nota": estado_info["nota"],
                    "id_periodo": estado_info["id_periodo"],
                }
            )

        resultado.append({"cuatrimestre": cuat, "cursos": cursos_bloque})

    return resultado


__all__ = [
    "MALLA_ISOV_VIRTUAL",
    "obtener_malla_isov_virtual",
    "mapear_malla_con_historico",
]