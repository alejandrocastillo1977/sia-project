-- ========================================
-- SIA Database Schema (v0.4)
-- Fecha: 2025-11-16
-- Autor: Coordinador del Proyecto SIA
-- ========================================

PRAGMA foreign_keys = ON;

-- Tabla: Estudiante
CREATE TABLE IF NOT EXISTS Estudiante (
    id_estudiante TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    programa TEXT,
    correo_institucional TEXT,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Curso (catálogo actual)
CREATE TABLE IF NOT EXISTS Curso (
    id_curso TEXT PRIMARY KEY,       -- NRC
    nombre TEXT NOT NULL,
    creditos INTEGER,
    codigo_alfanumerico TEXT         -- ALFA + NUMERI (forma visible)
);

-- Tabla: PeriodoAcademico
CREATE TABLE IF NOT EXISTS PeriodoAcademico (
    id_periodo TEXT PRIMARY KEY,
    anio INTEGER,
    periodo INTEGER
);

-- Tabla: Inscripcion (relación estudiante-curso-periodo)
-- v0.3: snapshot del curso
-- v0.4: agrega snapshot de programa (programa, descripcion_programa)
CREATE TABLE IF NOT EXISTS Inscripcion (
    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante TEXT NOT NULL,
    id_curso TEXT NOT NULL,
    id_periodo TEXT NOT NULL,
    nota REAL,
    version_periodo INTEGER DEFAULT 1,

    -- Snapshot del curso al momento del cargue (inmutable por defecto)
    alfa TEXT,
    numeri TEXT,
    codigo_alfanumerico TEXT,
    nombre_curso TEXT,

    -- Snapshot del programa al momento del cargue
    programa TEXT,              -- código corto, ej. ISUT / ISOF
    descripcion_programa TEXT,  -- nombre largo, ej. INGENIERIA DE SISTEMAS

    FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso),
    FOREIGN KEY (id_periodo) REFERENCES PeriodoAcademico(id_periodo)
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_insc_est ON Inscripcion(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_insc_per ON Inscripcion(id_periodo);
CREATE UNIQUE INDEX IF NOT EXISTS uq_insc_clave
    ON Inscripcion(id_estudiante, id_curso, id_periodo);

-- Tabla: Auditoria
CREATE TABLE IF NOT EXISTS Auditoria (
    id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    accion TEXT,
    fecha_evento TEXT DEFAULT CURRENT_TIMESTAMP
);