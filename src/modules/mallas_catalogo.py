from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import json

from modules.load_data import obtener_malla_isov_virtual

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MALLAS_DIR = BASE_DIR / "data" / "mallas_cargadas"
INDEX_PATH = MALLAS_DIR / "index.json"


@dataclass
class MallaMeta:
    id: str
    nombre: str
    archivo: str


def _leer_index() -> List[MallaMeta]:
    """
    Lee el índice de mallas desde data/mallas_cargadas/index.json.
    Si no existe, retorna lista vacía.
    """
    if not INDEX_PATH.exists():
        return []

    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    mallas: List[MallaMeta] = []
    for item in data:
        try:
            mallas.append(
                MallaMeta(
                    id=str(item["id"]),
                    nombre=str(item["nombre"]),
                    archivo=str(item["archivo"]),
                )
            )
        except KeyError:
            continue
    return mallas


def listar_mallas_disponibles() -> List[MallaMeta]:
    """
    Devuelve la lista de mallas registradas en el índice.
    No incluye la malla embebida: esa se maneja aparte.
    """
    return _leer_index()


def cargar_malla_desde_json(id_malla: str) -> Optional[Dict[str, Any]]:
    """
    Carga el JSON de una malla registrada en el índice.
    Retorna None si no se encuentra.
    """
    for meta in _leer_index():
        if meta.id == id_malla:
            ruta = MALLAS_DIR / meta.archivo
            if not ruta.exists():
                return None
            try:
                return json.loads(ruta.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None


def obtener_malla_por_id(id_malla: str) -> Optional[Dict[str, Any]]:
    """
    Punto de entrada principal:
    - 'embebida_isov_virtual' -> malla embebida en código.
    - cualquier otro id -> buscar en index.json y cargar JSON.
    """
    if id_malla == "embebida_isov_virtual":
        return obtener_malla_isov_virtual()

    return cargar_malla_desde_json(id_malla)