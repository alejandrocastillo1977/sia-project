# 🧾 CHANGELOG – Sistema de Inteligencia Académica (SIA)

> **Repositorio:** [github.com/alejandrocastillo1977/sia-project](https://github.com/alejandrocastillo1977/sia-project)  
> **Autor:** Alejandro Castillo – Coordinador del Programa de Ingeniería de Software (UNIMINUTO)  
> **Última versión:** `v1.3-Hito9-Final`  
> **Fecha de actualización:** Noviembre 2025  

---

## 📜 Resumen histórico de versiones

| Versión | Fecha | Rama / Tag | Descripción |
|----------|--------|-------------|-------------|
| **v1.0-Hito6** | Abril 2025 | `main` | Versión base funcional con cargue ARGOS y auditoría inicial |
| **v1.2-Hito7** | Junio 2025 | `feat/hito-7-consultas-tablero` | Integración de consultas y tablero general |
| **v1.2.3-Hito8-Final** | Septiembre 2025 | `feat/hito-8-visualizaciones-umbrales` | Visualizaciones por umbral y mantenimiento seguro |
| **v1.3-Hito9-Final** | Noviembre 2025 | `feat/hito-9-exportes-reportes` | Exportes PDF/Excel, validación híbrida y auditoría avanzada |

---

## 🏷️ v1.3 – Hito 9 (Final)
**Tag:** `v1.3-Hito9-Final`  
**Rama:** `feat/hito-9-exportes-reportes`  
**Fecha:** 8 de noviembre de 2025  

### ✨ Nuevas funcionalidades
- Exportes institucionales (PDF / Excel) para reportes individuales.  
- Auditoría avanzada con registro de eventos y respaldos automáticos (`backups/auditoria_snapshot_*.csv`).  
- Validación híbrida ARGOS (por nombre y posición de columna).  
- Compatibilidad con encabezados flexibles (`FACULTA` / `FACULTAD`, `DESCRIPION` / `DESCRIPCION`).  
- Integración de migraciones automáticas (`migracion_agregar_codigo_alfanumerico.py`).  
- Refactor completo de `Cargue.py`, `reports.py` y `queries.py`.  

### 🐛 Correcciones
- Solución a errores de integridad por duplicación de NRC entre periodos.  
- Separación correcta del campo `codigo_alfanumerico` (`ALFA + NUMERI`).  
- Manejo de encabezados incompletos o con tildes.  
- Sincronización de auditoría con el módulo de mantenimiento.  

### 🧱 Cambios estructurales
- Nueva tabla `Auditoria` y módulo `Auditoria.py`.  
- Migración automática: `src/database/migracion_agregar_codigo_alfanumerico.py`.  
- Revisión total de `schema.sql` y `upsert.py`.  
- Refactor del flujo de validación ARGOS.  

---

## 🏷️ v1.2.3 – Hito 8 (Visualizaciones y Mantenimiento)
**Tag:** `v1.2.3-Hito8-Final`  
**Rama:** `feat/hito-8-visualizaciones-umbrales`  
**Fecha:** Septiembre 2025  

### ✨ Nuevas funcionalidades
- Módulo de **umbrales** (`Umbrales.py`) con visualizaciones analíticas.  
- Módulo **Admin** (`Admin.py`) para reinicio seguro de base de datos.  
- Nuevas gráficas con `plotly` y `matplotlib`.  
- Validaciones de estructura ARGOS antes del cargue.  

### 🧱 Cambios estructurales
- Creación de entidad `PeriodoAcademico`.  
- Nuevo campo `version` en `Inscripcion`.  
- Auditoría integrada en eventos administrativos.  

---

## 🏷️ v1.2 – Hito 7 (Consultas y Tablero)
**Tag:** `v1.2-Hito7-Final`  
**Rama:** `feat/hito-7-consultas-tablero`  
**Fecha:** Junio 2025  

### ✨ Nuevas funcionalidades
- Módulo de **Consulta** (`Consulta.py`) por ID y nombre.  
- Módulo **Tablero** (`Tablero.py`) con indicadores y KPIs.  
- Exportes parciales por periodo.  

### 🧱 Cambios estructurales
- Refactor del esquema de base de datos y relaciones.  
- Unificación de scripts `app/` y `database/`.  
- Primera interfaz institucional con estilo UNIMINUTO.  

---

## 🏷️ v1.0 – Hito 6 (Versión Base)
**Tag:** `v1.0-Hito6`  
**Fecha:** Abril 2025  

### 🏗️ Componentes iniciales
- Estructura raíz del proyecto `sia-project/`.  
- Módulo base de **Cargue ARGOS**.  
- Script `verificar_entorno.py`.  
- Auditoría inicial de cargues.  
- Configuración de `.gitignore` y `requirements.txt`.  

---

## ⚙️ Dependencias principales

| Categoría | Librerías |
|------------|------------|
| Interfaz | Streamlit |
| Procesamiento | Pandas, NumPy |
| Base de datos | SQLite, SQLAlchemy |
| Exportes | XlsxWriter, FPDF |
| Visualización | Plotly, Matplotlib |
| Auditoría | Rich |
| Validación | Pydantic |
| QA y formato | Black, Ruff, Pytest |

---

## 👨‍💻 Créditos

**Autor y responsable técnico:**  
**Alejandro Castillo**  
Coordinador del Programa de Ingeniería de Software  
Corporación Universitaria Minuto de Dios – UNIMINUTO  
📧 coordinador.gestion.favoritos@gmail.com  

---

## 📎 Licencia

Uso **académico e institucional exclusivo**.  
Cualquier distribución o uso comercial requiere autorización expresa de **UNIMINUTO**.
