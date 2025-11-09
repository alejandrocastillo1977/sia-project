# 🧾 CHANGELOG – Sistema de Inteligencia Académica (SIA)

> **Repositorio:** [github.com/alejandrocastillo1977/sia-project](https://github.com/alejandrocastillo1977/sia-project)  
> **Última versión:** `v1.3-Hito9-Final`  
> **Fecha de actualización:** Noviembre 2025  

---

## 🧩 Estructura de versionado

El proyecto sigue un esquema de hitos numerados (`Hito6`, `Hito7`, `Hito8`, `Hito9`) que reflejan avances funcionales y de arquitectura.  
Cada hito tiene asociado un **tag Git** y una **rama de desarrollo**.

---

## 🏷️ v1.3 – Hito 9 (Final)
**Tag:** `v1.3-Hito9-Final`  
**Rama:** `feat/hito-9-exportes-reportes`  
**Fecha:** 8 de noviembre de 2025  

### ✨ Nuevas funcionalidades
- **Exportes institucionales (PDF / Excel)** para reportes individuales de estudiantes.  
- **Auditoría avanzada**: registro detallado de eventos, creación de snapshots automáticos (`backups/auditoria_snapshot_*.csv`).  
- **Validación híbrida ARGOS**: estructura validada por nombre y posición de columna.  
- Compatibilidad con encabezados flexibles (`FACULTA` / `FACULTAD`, `DESCRIPION` / `DESCRIPCION`).  
- **Integración de migraciones** automáticas: `migracion_agregar_codigo_alfanumerico.py`.  
- Mejora en la generación de reportes institucionales con encabezado UNIMINUTO.  
- Refactor de `queries.py` y `upsert.py` para mantener la integridad de datos en `Curso` e `Inscripcion`.

### 🐛 Correcciones
- Resolución del error de integridad por duplicación de NRC entre periodos.  
- Ajuste del campo `codigo_alfanumerico` para separar correctamente `ALFA + NUMERI`.  
- Corrección en la carga de archivos Excel con encabezados inconsistentes.  
- Armonización del flujo de auditoría con el módulo de mantenimiento.

### 🧱 Cambios estructurales
- Se agregó la nueva tabla `Auditoria`.  
- Se incorporó un script de migración automática en `src/database/migracion_agregar_codigo_alfanumerico.py`.  
- Revisión completa de `schema.sql`.  
- Refactor completo del módulo `Cargue.py` para integrar validación híbrida.  
- Nuevo módulo `Auditoria.py` dentro de `src/app/`.

---

## 🏷️ v1.2.3 – Hito 8 (Visualizaciones y Mantenimiento)
**Tag:** `v1.2.3-Hito8-Final`  
**Rama:** `feat/hito-8-visualizaciones-umbrales`  
**Fecha:** Septiembre 2025  

### ✨ Nuevas funcionalidades
- Incorporación del **módulo de umbrales** (`Umbrales.py`) con visualizaciones analíticas.  
- Módulo de **mantenimiento administrativo** (`Admin.py`), con reinicio seguro de base de datos.  
- Validación previa de la estructura ARGOS y control de versiones en las inscripciones.  
- Nuevas gráficas con `plotly` y exportación de métricas.

### 🧱 Cambios estructurales
- Se añade `PeriodoAcademico` como entidad independiente.  
- Se actualiza `schema.sql` con relaciones y claves foráneas.  
- Nuevo campo `version` en `Inscripcion` para mantener histórico de cambios.

---

## 🏷️ v1.2 – Hito 7 (Consultas y Tablero)
**Tag:** `v1.2-Hito7-Final`  
**Rama:** `feat/hito-7-consultas-tablero`  
**Fecha:** Junio 2025  

### ✨ Nuevas funcionalidades
- Implementación del **módulo de consultas** (`Consulta.py`) con búsqueda por ID y nombre.  
- Creación del **tablero general** (`Tablero.py`) con indicadores de desempeño.  
- Exportación inicial de reportes filtrados.  
- Integración de filtros de periodo y asignatura.  
- Primera conexión funcional a la base de datos consolidada `sia.db`.

### 🧱 Cambios estructurales
- Refactor del esquema de base de datos inicial (introducción de claves primarias).  
- Unificación de scripts en `src/app` y `src/database`.  
- Primer diseño de interfaz institucional UNIMINUTO con estilo Streamlit.

---

## 🏷️ v1.0 – Hito 6 (Versión Base)
**Tag:** `v1.0-Hito6`  
**Fecha:** Abril 2025  

### 🏗️ Componentes iniciales
- Estructura raíz del proyecto `sia-project/`.  
- Primer prototipo funcional del módulo **Cargue ARGOS**.  
- Script `verificar_entorno.py` para validar dependencias y versiones.  
- Implementación básica de auditoría de cargues.  
- Configuración inicial de `.gitignore`, `requirements.txt` y entorno virtual.

---

## ⚙️ Dependencias y herramientas clave

| Categoría | Librerías |
|------------|------------|
| Interfaz | Streamlit |
| Procesamiento | Pandas, NumPy |
| Base de datos | SQLite, SQLAlchemy |
| Exportes | XlsxWriter, FPDF |
| Visualización | Plotly, Matplotlib |
| Auditoría | Rich |
| Validación | Pydantic |
| Formato y QA | Black, Ruff, Pytest |

---

## 🧑‍💻 Mantenimiento y soporte

**Autor / Responsable técnico:**  
Alejandro Castillo  
📧 coordinador.gestion.favoritos@gmail.com  

**Institución:**  
Corporación Universitaria Minuto de Dios – UNIMINUTO  
Facultad de Ingeniería / Programa de Ingeniería de Software  
Sede Virtual y a Distancia (UVD)

---

## 📎 Licencia

Uso **académico e institucional exclusivo**.  
Distribución, modificación o uso comercial requerirá autorización expresa de UNIMINUTO.
