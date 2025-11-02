-- ========================================
-- SIA Database Schema (v0.1)
-- Fecha: 2025-11-01
-- Autor: Coordinador del Proyecto SIA
-- ========================================

-- Tabla: Estudiante
CREATE TABLE IF NOT EXISTS Estudiante (
    id_estudiante TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    programa TEXT,
    correo_institucional TEXT,
    fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Curso
CREATE TABLE IF NOT EXISTS Curso (
    id_curso TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    creditos INTEGER
);

-- Tabla: PeriodoAcademico
CREATE TABLE IF NOT EXISTS PeriodoAcademico (
    id_periodo TEXT PRIMARY KEY,
    anio INTEGER,
    periodo INTEGER
);

-- Tabla: Inscripcion (relación estudiante-curso-periodo)
CREATE TABLE IF NOT EXISTS Inscripcion (
    id_inscripcion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante TEXT,
    id_curso TEXT,
    id_periodo TEXT,
    nota REAL,
    version_periodo INTEGER DEFAULT 1,
    FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante),
    FOREIGN KEY (id_curso) REFERENCES Curso(id_curso),
    FOREIGN KEY (id_periodo) REFERENCES PeriodoAcademico(id_periodo)
);

-- Tabla: Auditoria
CREATE TABLE IF NOT EXISTS Auditoria (
    id_evento INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT,
    accion TEXT,
    fecha_evento TEXT DEFAULT CURRENT_TIMESTAMP
);
