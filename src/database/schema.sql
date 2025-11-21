-- ========================================
-- SIA Database Schema (v0.3)
-- Fecha: 2025-11-08
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

-- Tabla: Programa (catálogo de programas académicos)
CREATE TABLE IF NOT EXISTS Programa (
    codigo_programa TEXT PRIMARY KEY,
    descripcion_programa TEXT,
    rectoria TEXT,
    descripcion_rectoria TEXT,
    sede TEXT,
    descripcion_sede TEXT,
    facultad TEXT,
    descripcion_facultad TEXT,
    nivel TEXT,
    descripcion_nivel TEXT
);

-- Tabla: Curso (catálogo actual)
CREATE TABLE IF NOT EXISTS Curso (
    id_curso TEXT PRIMARY KEY,       -- NRC
    nombre TEXT NOT NULL,
    creditos INTEGER,
    codigo_alfanumerico TEXT,        -- ALFA + NUMERI (forma visible)
    codigo_programa TEXT,            -- Programa al que pertenece la oferta (PROGRAMA de ARGOS)
    FOREIGN KEY (codigo_programa) REFERENCES Programa(codigo_programa)
);

-- Tabla: PeriodoAcademico
CREATE TABLE IF NOT EXISTS PeriodoAcademico (
    id_periodo TEXT PRIMARY KEY,
    anio INTEGER,
    periodo INTEGER
);

-- Tabla: Inscripcion (relación estudiante-curso-periodo)
-- v0.3: agrega snapshot del curso (alfa, numeri, codigo_alfanumerico, nombre_curso)
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

    FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso),
    FOREIGN KEY (id_periodo) REFERENCES PeriodoAcademico(id_periodo)
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_insc_est ON Inscripcion(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_insc_per ON Inscripcion(id_periodo);
CREATE UNIQUE INDEX IF NOT EXISTS uq_insc_clave
    ON Inscripcion(id_estudiante, id_curso, id_periodo);

-- Tabla: MallaCurricular (una malla oficial por programa)
CREATE TABLE IF NOT EXISTS MallaCurricular (
    id_malla INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_programa TEXT NOT NULL,
    nombre_malla TEXT NOT NULL,
    creditos_totales INTEGER,
    FOREIGN KEY (codigo_programa) REFERENCES Programa(codigo_programa),
    UNIQUE (codigo_programa)
);

-- Tabla: MallaCurso (cursos que componen una malla)
CREATE TABLE IF NOT EXISTS MallaCurso (
    id_malla INTEGER NOT NULL,
    codigo_curso TEXT NOT NULL,   -- Código alfanumérico oficial (ALFA + NUMERI)
    nombre_oficial TEXT,
    creditos INTEGER,
    cuatrimestre INTEGER,
    FOREIGN KEY (id_malla) REFERENCES MallaCurricular(id_malla) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_malla_curso
    ON MallaCurso(id_malla, codigo_curso);

-- Tabla: Auditoria
CREATE TABLE IF NOT EXISTS Auditoria (
    id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    accion TEXT,
    fecha_evento TEXT DEFAULT CURRENT_TIMESTAMP
);