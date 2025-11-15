# 🧠 AI_MEMORY — Sistema de Inteligencia Académica (SIA)

> **Propósito:** Este archivo proporciona al asistente de IA el contexto completo del proyecto SIA para ofrecer respuestas coherentes, técnicas y contextualizadas.

---

## 🎯 Objetivo del proyecto

El **Sistema de Inteligencia Académica (SIA)** es una aplicación institucional desarrollada en **Python + Streamlit + SQLite**, orientada a la gestión, análisis y auditoría de datos académicos provenientes de reportes **ARGOS** de UNIMINUTO.  
Su propósito es **automatizar la validación, transformación, análisis y visualización** de información académica, asegurando trazabilidad y calidad de datos.

---

## 🧩 Arquitectura del sistema

### 1. Interfaz (UI)
- **Framework:** Streamlit (`src/app/`)
- **Punto de entrada:** `src/app/app.py`
- **Módulos:** `Cargue.py`, `Consulta.py`, `Tablero.py`, `Umbrales.py`, `Admin.py`, `Auditoria.py`
- **Función:** Permitir navegación por pestañas, visualización de datos, reportes y auditoría.

### 2. Capa de datos
- **Ubicación:** `src/database/`
- **Base:** `data/sia.db` (SQLite)
- **Archivos clave:** `schema.sql`, `db_init.py`, `upsert.py`, `queries.py`, `migracion_agregar_codigo_alfanumerico.py`
- **Propósito:** Crear y mantener la estructura de base de datos, ejecutar consultas y operaciones CRUD con SQLAlchemy.

### 3. Lógica y servicios
- **Ubicación:** `src/modules/`
- **Módulos:** `argos_loader.py`, `validators.py`, `reports.py`, `load_data.py`
- **Propósito:** Manejo de validación de archivos, generación de reportes y control de flujo del cargue académico.

### 4. Utilitarios
- **Ubicación:** `src/utils/`
- **Archivos:** `helpers.py`, `cargue_historial.py`
- **Función:** Funciones auxiliares, logs y procesamiento complementario.

### 5. Scripts raíz
- **`verificar_entorno.py`** → verifica versión de Python y dependencias.
- **`requirements.txt`** → define entorno reproducible.
- **`README.md`** → documentación principal del sistema.

---

## ⚙️ Dependencias principales

- `streamlit`, `pandas`, `numpy`, `SQLAlchemy`, `sqlite-utils`  
- `pydantic`, `plotly`, `matplotlib`, `fpdf2`, `xlsxwriter`, `reportlab`  
- `python-dotenv`, `rich`, `pytest`, `black`, `ruff`

---

## 🧪 Ejecución del sistema

### Verificar entorno
```bash
python verificar_entorno.py
```
Debe mostrar: “Entorno completamente configurado.”

### Ejecutar aplicación
```bash
streamlit run src/app/app.py
```
Abrir en el navegador: [http://localhost:8501](http://localhost:8501)

---

## 🧱 Buenas prácticas y estilo de código

- Seguir **PEP8** para formato y espaciado.  
- Documentar funciones y clases con *docstrings triple comillas*.  
- Usar nombres en inglés para funciones y módulos; español para interfaz y textos visibles.  
- Validar rutas con `os.path` o `Path` antes de guardar archivos.  
- Versionar por hitos (`v1.x-HitoN`).

---

## 🧩 Instrucciones para el asistente de IA (Windsurf)

**Rol esperado del agente de IA:**
- Responder en español técnico y claro.
- Mantener precisión sobre arquitectura y dependencias.
- Evitar reescribir código existente sin analizar su impacto.
- Proponer mejoras estructurales (optimización, modularización, logging, documentación).
- Al hacer refactor, preservar compatibilidad con Streamlit y SQLite.
- Priorizar el uso de *pydantic* para validaciones y *SQLAlchemy* para persistencia.

**Archivos clave a indexar permanentemente:**
- `README.md`
- `AI_MEMORY.md`
- `src/app/app.py`
- `src/database/db_init.py`
- `src/modules/argos_loader.py`
- `src/modules/reports.py`
- `src/utils/helpers.py`
- `requirements.txt`

---

## 🧭 Contexto adicional

**Versión actual:** v1.3 – Hito 9  
**Autor:** Jaime Alejandro Augusto Castillo Fontecha  
**Institución:** Corporación Universitaria Minuto de Dios – UNIMINUTO  
**Programa:** Ingeniería de Software (Modalidad Virtual)  
**Última actualización:** Noviembre 2025
