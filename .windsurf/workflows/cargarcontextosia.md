---
description: Carga automática del contexto completo del proyecto SIA (archivos clave, dependencias y documentación).
auto_execution_mode: 3
---

/context clear

# Documentación y metadatos del proyecto
/context add AI_MEMORY.md
/context add README.md
/context add CHANGELOG.md
/context add requirements.txt

# Scripts raíz útiles para entorno y pruebas
/context add verificar_entorno.py
/context add prueba_conexion.txt

# Aplicación principal (frontend / lógica de vistas SIA)
/context add src/app/app.py
/context add src/app/Home.py
/context add src/app/Cargue.py
/context add src/app/Tablero.py
/context add src/app/Consulta.py
/context add src/app/Umbrales.py
/context add src/app/Admin.py
/context add src/app/Auditoria.py
/context add src/app/Malla.py

# Capa de base de datos
/context add src/database/db_init.py
/context add src/database/db_setup.py
/context add src/database/analisis_datos.py
/context add src/database/migracion_agregar_codigo_alfanumerico.py
/context add src/database/queries.py
/context add src/database/schema.sql
/context add src/database/upsert.py

# Módulos de negocio, carga y reportes
/context add src/modules/argos_loader.py
/context add src/modules/load_data.py
/context add src/modules/mallas_catalogo.py
/context add src/modules/mallas_loader.py
/context add src/modules/reports.py
/context add src/modules/student_view.py
/context add src/modules/validators.py

# Utilidades y helpers
/context add src/utils/cargue_historial.py
/context add src/utils/helpers.py