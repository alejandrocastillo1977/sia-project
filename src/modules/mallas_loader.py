from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import json

from modules.mallas_catalogo import MALLAS_DIR, INDEX_PATH, _leer_index, MallaMeta


@dataclass
class ResultadoValidacionMalla:
    es_valida: bool
    errores: List[str]
    resumen: Dict[str, Any]


def _validar_estructura_malla(data: Dict[str, Any]) -> ResultadoValidacionMalla:
    errores: List[str] = []

    programa = data.get("programa")
    creditos_totales = data.get("creditos_totales")
    plan = data.get("plan")

    if not isinstance(programa, str) or not programa.strip():
        errores.append("Campo 'programa' debe ser una cadena no vacía.")

    if not isinstance(creditos_totales, int) or creditos_totales <= 0:
        errores.append("Campo 'creditos_totales' debe ser un entero positivo.")

    if not isinstance(plan, list) or not plan:
        errores.append("Campo 'plan' debe ser una lista no vacía de cuatrimestres.")
        return ResultadoValidacionMalla(False, errores, {})

    total_creditos_cursos = 0
    total_cursos = 0
    cuatrimestres: List[int] = []

    for idx, bloque in enumerate(plan, start=1):
        if not isinstance(bloque, dict):
            errores.append(f"El elemento {idx} de 'plan' debe ser un objeto.")
            continue

        cuat = bloque.get("cuatrimestre")
        cursos = bloque.get("cursos")

        if not isinstance(cuat, int) or cuat <= 0:
            errores.append(f"Cuatrimestre #{idx} tiene 'cuatrimestre' inválido.")
        else:
            cuatrimestres.append(cuat)

        if not isinstance(cursos, list) or not cursos:
            errores.append(f"Cuatrimestre {cuat or idx} debe tener una lista 'cursos' no vacía.")
            continue

        for curso in cursos:
            if not isinstance(curso, dict):
                errores.append(f"Curso en cuatrimestre {cuat or idx} debe ser un objeto.")
                continue

            codigo = curso.get("codigo")
            nombre = curso.get("nombre")
            creditos = curso.get("creditos")

            if not (isinstance(codigo, str) or isinstance(codigo, list)):
                errores.append(
                    f"Curso en cuatrimestre {cuat or idx} tiene 'codigo' inválido (str o lista de str)."
                )

            if isinstance(codigo, list) and not all(isinstance(c, str) for c in codigo):
                errores.append(
                    f"Curso en cuatrimestre {cuat or idx} tiene 'codigo' como lista pero no todos son cadenas."
                )

            if not isinstance(nombre, str) or not nombre.strip():
                errores.append(f"Curso en cuatrimestre {cuat or idx} tiene 'nombre' inválido.")

            if not isinstance(creditos, int) or creditos <= 0:
                errores.append(f"Curso '{nombre}' en cuatrimestre {cuat or idx} tiene 'creditos' inválidos.")
            else:
                total_creditos_cursos += creditos
                total_cursos += 1

    resumen = {
        "programa": programa,
        "creditos_totales_declarados": creditos_totales,
        "creditos_suma_cursos": total_creditos_cursos,
        "total_cursos": total_cursos,
        "cuatrimestres": sorted(set(cuatrimestres)),
    }

    if total_creditos_cursos != creditos_totales:
        errores.append(
            f"La suma de créditos de cursos ({total_creditos_cursos}) "
            f"no coincide con 'creditos_totales' ({creditos_totales})."
        )

    return ResultadoValidacionMalla(es_valida=len(errores) == 0, errores=errores, resumen=resumen)


def simular_malla_desde_bytes(contenido: bytes) -> ResultadoValidacionMalla:
    """
    Simula la carga de una malla a partir de un archivo JSON (bytes),
    sin escribir nada en disco.
    """
    try:
        data = json.loads(contenido.decode("utf-8"))
    except Exception as e:
        return ResultadoValidacionMalla(
            es_valida=False,
            errores=[f"JSON inválido: {e}"],
            resumen={},
        )

    if not isinstance(data, dict):
        return ResultadoValidacionMalla(
            es_valida=False,
            errores=["La raíz del JSON debe ser un objeto (dict)."],
            resumen={},
        )

    return _validar_estructura_malla(data)


def registrar_malla(
    id_malla: str,
    nombre_visible: str,
    contenido: bytes,
) -> Tuple[bool, str]:
    """
    Registra una nueva malla:
    - Valida JSON y estructura.
    - Si es válida, guarda el JSON en data/mallas_cargadas/<id_malla>.json
      y actualiza index.json.
    Retorna (ok, mensaje).
    """
    id_malla = id_malla.strip()
    nombre_visible = nombre_visible.strip()

    if not id_malla:
        return False, "El identificador de la malla no puede estar vacío."

    if not nombre_visible:
        return False, "El nombre visible de la malla no puede estar vacío."

    # No permitir colisión con la malla embebida
    if id_malla == "embebida_isov_virtual":
        return False, "El identificador 'embebida_isov_virtual' está reservado por el sistema."

    # Validar estructura primero
    resultado = simular_malla_desde_bytes(contenido)
    if not resultado.es_valida:
        return False, "La malla no es válida. Revisa los errores reportados en la simulación."

    # Asegurar carpeta
    MALLAS_DIR.mkdir(parents=True, exist_ok=True)

    # Guardar JSON
    ruta_json = MALLAS_DIR / f"{id_malla}.json"
    ruta_json.write_bytes(contenido)

    # Actualizar índice
    existentes = _leer_index()
    # Si ya existe id, lo reemplazamos
    otros = [m for m in existentes if m.id != id_malla]
    nuevos = otros + [MallaMeta(id=id_malla, nombre=nombre_visible, archivo=f"{id_malla}.json")]

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps([m.__dict__ for m in nuevos], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return True, f"Malla '{nombre_visible}' registrada con id '{id_malla}'."