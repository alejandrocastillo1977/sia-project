# 🎓 Sistema de Inteligencia Académica (SIA)

> **Versión estable:** v1.3 – Hito 9  
> **Fecha:** Noviembre 2025  
> **Autor:** Coordinador del Programa de Ingeniería de Software – UNIMINUTO  
> **Repositorio:** [github.com/alejandrocastillo1977/sia-project](https://github.com/alejandrocastillo1977/sia-project)

---

## 📘 Descripción general

El **Sistema de Inteligencia Académica (SIA)** es una herramienta institucional desarrollada en **Python + Streamlit + SQLite** que permite analizar, validar y visualizar el rendimiento académico de los estudiantes con base en los reportes **ARGOS** de UNIMINUTO.

### Objetivos principales

- Validar y transformar los reportes ARGOS institucionales.  
- Centralizar la información académica por estudiante, curso y periodo.  
- Generar **reportes PDF y Excel** con información auditada.  
- Proporcionar visualizaciones analíticas por **umbrales de desempeño**.  
- Mantener trazabilidad completa mediante **auditoría de eventos**.

---

## 🧩 Arquitectura general

```bash
sia-project/
│
├── src/
│   ├── app/                  # Aplicación Streamlit (interfaz principal)
│   │   ├── app.py            # Navegación y módulos principales
│   │   ├── Cargue.py         # Cargue de archivos ARGOS
│   │   ├── Consulta.py       # Consulta por estudiante
│   │   ├── Tablero.py        # Visualización general
│   │   ├── Umbrales.py       # Reportes analíticos por umbral
│   │   ├── Admin.py          # Reinicio y mantenimiento del sistema
│   │   └── Auditoria.py      # Registro y monitoreo de eventos
│   │
│   ├── database/
│   │   ├── schema.sql        # Definición completa de tablas y relaciones
│   │   ├── db_init.py        # Inicialización automática de la base de datos
│   │   ├── upsert.py         # Inserción/actualización (UPSERT)
│   │   ├── queries.py        # Consultas optimizadas y búsquedas
│   │   └── migracion_agregar_codigo_alfanumerico.py
│   │
│   ├── modules/
│   │   ├── argos_loader.py   # Cargue y validación híbrida de archivos ARGOS
│   │   ├── validators.py     # Validaciones estructurales y semánticas
│   │   ├── reports.py        # Exportes a PDF y Excel
│   │   └── load_data.py      # (reservado para futuras integraciones)
│   │
│   └── utils/
│       └── helpers.py        # Utilidades adicionales (placeholder)
│
├── data/                     # Archivos de datos y base SQLite (auto-generada)
├── exports/                  # Reportes generados (PDF, Excel)
├── backups/                  # Copias de seguridad y bundles Git
├── requirements.txt          # Dependencias de entorno
├── verificar_entorno.py      # Script de validación del entorno SIA
├── .gitignore
└── README.md
```

---

## ⚙️ Instalación y configuración

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/alejandrocastillo1977/sia-project.git
cd sia-project
```

### 2️⃣ Crear entorno virtual
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # En Windows PowerShell
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Verificar entorno
```bash
python verificar_entorno.py
```
Debe mostrar:  
✅ “Entorno completamente configurado.”

### 5️⃣ Inicializar base de datos
```bash
python src/database/db_init.py
```
Esto crea `data/sia.db` con la estructura definida en `schema.sql`.

---

## 🚀 Ejecución del sistema

Ejecuta el entorno Streamlit desde la raíz del proyecto:
```bash
streamlit run src/app/app.py
```

Abre en el navegador:
👉 [http://localhost:8501](http://localhost:8501)

---

## 🧠 Flujo general del sistema

### 🔹 Cargue ARGOS
- Carga un archivo `.xlsx` del sistema institucional.  
- El módulo valida encabezados, estructura y datos híbridos (por nombre y posición).  
- Inserta o actualiza los registros en la base de datos SQLite.

### 🔹 Consulta por estudiante
- Permite buscar por ID o nombre.  
- Muestra historial académico, cursos y notas por periodo.  
- Exporta a PDF o Excel con formato institucional.

### 🔹 Tablero y visualizaciones
- Gráficas y métricas de desempeño general.  
- Comparaciones por programa, periodo y umbral.

### 🔹 Módulo de Umbrales
- Analiza notas por rangos (bajo, medio, alto).  
- Permite identificar alertas de rendimiento académico.

### 🔹 Auditoría del sistema
- Registra eventos de cargue, mantenimiento y exporte.  
- Genera respaldo automático (`backups/auditoria_snapshot_YYYYMMDD.csv`).

### 🔹 Mantenimiento (Admin)
- Permite reiniciar la base de datos.  
- Reejecuta el esquema base sin perder el histórico de auditoría.

---

## 🧾 Base de datos

El sistema usa **SQLite** con las siguientes tablas principales:

| Tabla              | Propósito                                                   |
| ------------------ | ----------------------------------------------------------- |
| `Estudiante`       | Datos del estudiante (id, nombre, programa, correo)         |
| `Curso`            | Información del curso (NRC, nombre, código alfanumérico)    |
| `PeriodoAcademico` | Año y periodo (e.g., 202405)                                |
| `Inscripcion`      | Relación estudiante–curso–periodo–nota (control de versión) |
| `Auditoria`        | Registro histórico de acciones y eventos del sistema        |

---

## 🧰 Tecnologías y librerías

| Categoría                | Librerías principales             |
| ------------------------ | --------------------------------- |
| Interfaz gráfica         | `streamlit`                       |
| Procesamiento y análisis | `pandas`, `numpy`                 |
| Validación y estructuras | `pydantic`                        |
| Exportes                 | `xlsxwriter`, `fpdf`              |
| Base de datos            | `sqlite3`, `SQLAlchemy`           |
| Visualización            | `plotly`, `matplotlib`            |
| Formato y calidad        | `black`, `ruff`, `pytest`, `rich` |

---

## 🏷️ Versionado por hitos

| Versión        | Hito                                                                   | Descripción |
| -------------- | ---------------------------------------------------------------------- | ----------- |
| `v1.0-Hito6`   | Implementación base del sistema (cargue ARGOS, validación, auditoría). |             |
| `v1.2-Hito7`   | Módulos de consulta y tablero con conexión a base de datos.            |             |
| `v1.2.3-Hito8` | Visualizaciones por umbral, mantenimiento seguro del sistema.          |             |
| `v1.3-Hito9`   | Exportes PDF/Excel, auditoría mejorada, validación híbrida ARGOS.      |             |

---

## 👨‍💻 Autoría y créditos

Proyecto académico desarrollado por:

**Coordinador del Programa de Ingeniería de Software**  
Corporación Universitaria Minuto de Dios – **UNIMINUTO**  
Sede Virtual y a Distancia (UVD)

**Desarrollador responsable:**  
**Alejandro Castillo**  
📧 coordinador.gestion.favoritos@gmail.com

---

## 📎 Licencia

Este proyecto es de uso académico e institucional, desarrollado para propósitos educativos y de gestión interna.  
No se permite su distribución comercial sin autorización de **UNIMINUTO**.
