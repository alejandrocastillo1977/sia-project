"""
Sistema de Inteligencia Académica (SIA)
--------------------------------------------------
Script de verificación de entorno de desarrollo
Versión: 1.0 - Noviembre 2025
Autor: Coordinador del Programa de Ingeniería de Software – UNIMINUTO
Uso: python verificar_entorno.py
"""

import importlib
import sys
from rich.console import Console
from rich.table import Table

console = Console()

# --------------------------------------------------
# Paquetes esperados y su propósito
# --------------------------------------------------
DEPENDENCIAS = {
    "streamlit": "Interfaz gráfica del sistema (UI)",
    "pandas": "Procesamiento de datos (ARGOS)",
    "numpy": "Cálculo numérico y validaciones",
    "openpyxl": "Lectura/escritura de archivos Excel",
    "sqlalchemy": "Conexión y ORM para SQLite",
    "pydantic": "Validación de datos estructurados",
    "fpdf": "Generación de reportes PDF",
    "xlsxwriter": "Exportación a Excel",
    "pytest": "Pruebas automáticas",
    "black": "Formateo de código",
    "ruff": "Linting y análisis estático",
    "rich": "Visualización en consola (colores, tablas)",
    "dotenv": "Gestión de variables de entorno (.env)",
}

# --------------------------------------------------
# Verificación dinámica
# --------------------------------------------------
def verificar_paquete(nombre):
    try:
        pkg = importlib.import_module(nombre)
        version = getattr(pkg, "__version__", "N/A")
        return "✅", version
    except ImportError:
        return "❌", "No instalado"


def main():
    console.print("\n[bold cyan]🔍 Verificación del entorno de desarrollo SIA[/bold cyan]\n")

    tabla = Table(show_header=True, header_style="bold blue")
    tabla.add_column("Paquete", justify="left")
    tabla.add_column("Versión", justify="center")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Descripción", justify="left", style="dim")

    total_faltantes = 0

    for nombre, descripcion in DEPENDENCIAS.items():
        estado, version = verificar_paquete(nombre)
        if estado == "❌":
            total_faltantes += 1
        tabla.add_row(nombre, version, estado, descripcion)

    console.print(tabla)

    if total_faltantes == 0:
        console.print("\n[bold green]✅ Entorno completamente configurado.[/bold green]")
    else:
        console.print(
            f"\n[bold yellow]⚠️ {total_faltantes} paquete(s) faltantes.[/bold yellow] "
            "Ejecuta: [bold white]pip install -r requirements.txt[/bold white]"
        )

    console.print("\n[italic cyan]Fin de la verificación.[/italic cyan]\n")


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        console.print("[bold red]Python 3.10 o superior es requerido.[/bold red]")
        sys.exit(1)
    main()
