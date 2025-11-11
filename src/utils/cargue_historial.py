"""Utilidades para gestionar el historial de cargues ARGOS.

Este módulo centraliza la lectura y escritura del registro de cargues
recientes con el fin de reutilizarlo tanto en la vista principal como en
el módulo de cargue. Los datos se persisten en un archivo JSON sencillo
ubicado en `exports/logs/cargues_recientes.json`.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
"""Directorio base del proyecto (raíz del repositorio)."""

LOG_DIR = PROJECT_ROOT / "exports" / "logs"
"""Directorio donde se almacena el historial de cargues."""

HISTORIAL_PATH = LOG_DIR / "cargues_recientes.json"
"""Ruta completa al archivo JSON del historial de cargues."""

MAX_ENTRADAS = 3
"""Número máximo de cargues a almacenar en el historial."""


def _asegurar_directorio() -> None:
    """Crea la carpeta del historial si aún no existe."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)


def obtener_historial() -> List[Dict[str, str]]:
    """Devuelve la lista de cargues almacenados.

    Returns
    -------
    list of dict
        Entradas con las claves `archivo`, `modo`, `estado` y `fecha`.
    """

    if not HISTORIAL_PATH.exists():
        return []

    try:
        with HISTORIAL_PATH.open("r", encoding="utf-8") as fh:
            datos = json.load(fh)
            if isinstance(datos, list):
                return [
                    entrada
                    for entrada in datos
                    if isinstance(entrada, dict)
                ][:MAX_ENTRADAS]
    except json.JSONDecodeError:
        # Si el archivo está corrupto lo reiniciamos en la siguiente escritura.
        return []

    return []


def registrar_cargue(archivo: str, modo: str, estado: str) -> None:
    """Añade un cargue al historial persistente.

    Parameters
    ----------
    archivo:
        Nombre del archivo cargado.
    modo:
        Descripción del modo utilizado (simulación o real).
    estado:
        Resultado general del proceso ("Éxito", "Error", etc.).
    """

    _asegurar_directorio()

    historial = obtener_historial()

    # Construimos la nueva entrada con sello de tiempo ISO.
    nueva_entrada = {
        "archivo": archivo,
        "modo": modo,
        "estado": estado,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    historial.insert(0, nueva_entrada)
    historial = historial[:MAX_ENTRADAS]

    with HISTORIAL_PATH.open("w", encoding="utf-8") as fh:
        json.dump(historial, fh, ensure_ascii=False, indent=2)


__all__ = [
    "HISTORIAL_PATH",
    "MAX_ENTRADAS",
    "obtener_historial",
    "registrar_cargue",
]
