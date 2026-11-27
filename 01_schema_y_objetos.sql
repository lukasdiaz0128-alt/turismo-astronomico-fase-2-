-- ============================================================================
-- SISTEMA DE GESTIÓN Y ANALÍTICA PARA RED DE TURISMO ASTRONÓMICO (FASE 2)
-- Motor: MySQL 8.0 | Normalización: 3FN (21 Tablas) + 6 Vistas + 6 Procedimientos
-- ============================================================================

DROP DATABASE IF EXISTS turismo_astronomico;
CREATE DATABASE turismo_astronomico CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE turismo_astronomico;

-- ----------------------------------------------------------------------------
-- 1. INFRAESTRUCTURA Y EQUIPAMIENTO (4 Tablas)
-- ----------------------------------------------------------------------------
CREATE TABLE Centro_astronomico (
    codigo_centro VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    ubicacion VARCHAR(150) NOT NULL,
    capacidad_maxima INT NOT NULL CHECK (capacidad_maxima > 0),
    activo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE Zonas_observacion (
    codigo_zona VARCHAR(10) PRIMARY KEY,
    codigo_centro VARCHAR(10) NOT NULL,
    nombre_zona VARCHAR(100) NOT NULL,
    indice_oscuridad DECIMAL(4,2) NOT NULL CHECK (indice_oscuridad > 0 AND indice_oscuridad <= 25.00),
    altitud_msnm INT NOT NULL CHECK (altitud_msnm >= 0),
    capacidad_zona INT NOT NULL CHECK (capacidad_zona > 0),
    CONSTRAINT fk_zona_centro FOREIGN KEY (codigo_centro) REFERENCES Centro_astronomico(codigo_centro)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Equipamiento (
    codigo_equipo VARCHAR(10) PRIMARY KEY,
    codigo_centro VARCHAR(10) NOT NULL,
    nombre_equipo VARCHAR(120) NOT NULL,
    tipo_equipo VARCHAR(60) NOT NULL,
    estado_operativo ENUM('Operativo', 'En Mantenimiento', 'Fuera de Servicio') NOT NULL DEFAULT 'Operativo',
    fecha_adquisicion DATE NOT NULL,
    CONSTRAINT fk_equipo_centro FOREIGN KEY (codigo_centro) REFERENCES Centro_astronomico(codigo_centro)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Calibraciones (
    codigo_calibracion VARCHAR(12) PRIMARY KEY,
    codigo_equipo VARCHAR(10) NOT NULL,
    fecha_calibracion DATE NOT NULL,
    resultado ENUM('Aprobada', 'Con Observaciones', 'Rechazada') NOT NULL,
    observaciones_tecnicas TEXT,
    CONSTRAINT fk_calibracion_equipo FOREIGN KEY (codigo_equipo) REFERENCES Equipamiento(codigo_equipo)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. PERSONAL, ESPECIALIZACIÓN Y SEGURIDAD (7 Tablas)
-- ----------------------------------------------------------------------------
CREATE TABLE Roles (
    codigo_rol VARCHAR(10) PRIMARY KEY,
    nombre_rol VARCHAR(40) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE Personal (
    codigo_personal VARCHAR(10) PRIMARY KEY,
    codigo_centro VARCHAR(10) NOT NULL,
    codigo_rol VARCHAR(10) NOT NULL,
    rut VARCHAR(15) NOT NULL UNIQUE,
    nombre_completo VARCHAR(120) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    telefono VARCHAR(25) NOT NULL,
    fecha_contratacion DATE NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_personal_centro FOREIGN KEY (codigo_centro) REFERENCES Centro_astronomico(codigo_centro)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_personal_rol FOREIGN KEY (codigo_rol) REFERENCES Roles(codigo_rol)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Cuentas_usuarios (
    nombre_usuario VARCHAR(50) PRIMARY KEY,
    codigo_personal VARCHAR(10) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    CONSTRAINT fk_cuenta_personal FOREIGN KEY (codigo_personal) REFERENCES Personal(codigo_personal)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Investigadores (
    codigo_personal VARCHAR(10) PRIMARY KEY,
    especialidad_cientifica VARCHAR(100) NOT NULL,
    grado_academico VARCHAR(60) NOT NULL,
    numero_publicaciones INT NOT NULL DEFAULT 0 CHECK (numero_publicaciones >= 0),
    CONSTRAINT fk_inv_personal FOREIGN KEY (codigo_personal) REFERENCES Personal(codigo_personal)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Tecnicos (
    codigo_personal VARCHAR(10) PRIMARY KEY,
    area_tecnica VARCHAR(80) NOT NULL,
    certificacion_instrumental VARCHAR(100) NOT NULL,
    CONSTRAINT fk_tec_personal FOREIGN KEY (codigo_personal) REFERENCES Personal(codigo_personal)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Guias_cientificos (
    codigo_personal VARCHAR(10) PRIMARY KEY,
    idiomas VARCHAR(120) NOT NULL,
    anos_experiencia_divulgacion INT NOT NULL DEFAULT 0 CHECK (anos_experiencia_divulgacion >= 0),
    CONSTRAINT fk_guia_personal FOREIGN KEY (codigo_personal) REFERENCES Personal(codigo_personal)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Administrativos (
    codigo_personal VARCHAR(10) PRIMARY KEY,
    cargo_administrativo VARCHAR(80) NOT NULL,
    departamento VARCHAR(80) NOT NULL,
    CONSTRAINT fk_adm_personal FOREIGN KEY (codigo_personal) REFERENCES Personal(codigo_personal)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. CATÁLOGO DE FENÓMENOS ASTRONÓMICOS Y ESPECIALIZACIÓN (4 Tablas)
-- ----------------------------------------------------------------------------
CREATE TABLE Fenomenos (
    codigo_fenomeno VARCHAR(10) PRIMARY KEY,
    nombre_fenomeno VARCHAR(120) NOT NULL,
    descripcion TEXT,
    visibilidad_estimada VARCHAR(60) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE Fenomenos_solares (
    codigo_fenomeno VARCHAR(10) PRIMARY KEY,
    tipo_actividad_solar VARCHAR(80) NOT NULL,
    nivel_radiacion VARCHAR(40) NOT NULL,
    CONSTRAINT fk_fsolar_fenomeno FOREIGN KEY (codigo_fenomeno) REFERENCES Fenomenos(codigo_fenomeno)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Fenomenos_lunares (
    codigo_fenomeno VARCHAR(10) PRIMARY KEY,
    fase_lunar VARCHAR(60) NOT NULL,
    porcentaje_iluminacion DECIMAL(5,2) NOT NULL CHECK (porcentaje_iluminacion >= 0 AND porcentaje_iluminacion <= 100),
    CONSTRAINT fk_flunar_fenomeno FOREIGN KEY (codigo_fenomeno) REFERENCES Fenomenos(codigo_fenomeno)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Fenomenos_espacios_profundos (
    codigo_fenomeno VARCHAR(10) PRIMARY KEY,
    tipo_objeto VARCHAR(80) NOT NULL,
    magnitud_aparente DECIMAL(5,2) NOT NULL,
    constelacion VARCHAR(80) NOT NULL,
    CONSTRAINT fk_fesp_fenomeno FOREIGN KEY (codigo_fenomeno) REFERENCES Fenomenos(codigo_fenomeno)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. OPERACIÓN, VISITANTES, RESERVAS Y EVALUACIONES (6 Tablas)
-- ----------------------------------------------------------------------------
CREATE TABLE Actividad (
    codigo_actividad VARCHAR(10) PRIMARY KEY,
    codigo_centro VARCHAR(10) NOT NULL,
    codigo_zona VARCHAR(10) NOT NULL,
    codigo_guia VARCHAR(10) NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    modalidad ENUM('Observación Nocturna', 'Observación Solar', 'Astrofotografía', 'Charla y Telescopio') NOT NULL,
    cupos_disponibles INT NOT NULL CHECK (cupos_disponibles > 0),
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    estado_actividad ENUM('Programada', 'Realizada', 'Cancelada') NOT NULL DEFAULT 'Programada',
    CONSTRAINT fk_act_centro FOREIGN KEY (codigo_centro) REFERENCES Centro_astronomico(codigo_centro)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_act_zona FOREIGN KEY (codigo_zona) REFERENCES Zonas_observacion(codigo_zona)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_act_guia FOREIGN KEY (codigo_guia) REFERENCES Guias_cientificos(codigo_personal)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Actividad_fenomeno (
    codigo_actividad VARCHAR(10) NOT NULL,
    codigo_fenomeno VARCHAR(10) NOT NULL,
    PRIMARY KEY (codigo_actividad, codigo_fenomeno),
    CONSTRAINT fk_af_act FOREIGN KEY (codigo_actividad) REFERENCES Actividad(codigo_actividad)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_af_fen FOREIGN KEY (codigo_fenomeno) REFERENCES Fenomenos(codigo_fenomeno)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Actividad_equipamiento (
    codigo_actividad VARCHAR(10) NOT NULL,
    codigo_equipo VARCHAR(10) NOT NULL,
    PRIMARY KEY (codigo_actividad, codigo_equipo),
    CONSTRAINT fk_ae_act FOREIGN KEY (codigo_actividad) REFERENCES Actividad(codigo_actividad)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_ae_eq FOREIGN KEY (codigo_equipo) REFERENCES Equipamiento(codigo_equipo)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Visitantes (
    codigo_visitante VARCHAR(10) PRIMARY KEY,
    rut_pasaporte VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    correo VARCHAR(120) NOT NULL UNIQUE,
    pais_origen VARCHAR(60) NOT NULL,
    fecha_nacimiento DATE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Telefonos_visitantes (
    codigo_visitante VARCHAR(10) NOT NULL,
    telefono VARCHAR(25) NOT NULL,
    PRIMARY KEY (codigo_visitante, telefono),
    CONSTRAINT fk_tel_visitante FOREIGN KEY (codigo_visitante) REFERENCES Visitantes(codigo_visitante)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Reservas (
    codigo_reserva VARCHAR(12) PRIMARY KEY,
    codigo_actividad VARCHAR(10) NOT NULL,
    codigo_visitante VARCHAR(10) NOT NULL,
    fecha_reserva DATE NOT NULL,
    asistencia_efectiva TINYINT(1) NOT NULL DEFAULT 0 CHECK (asistencia_efectiva IN (0, 1)),
    observaciones VARCHAR(255),
    estado ENUM('Confirmada', 'Completada', 'Cancelada') NOT NULL DEFAULT 'Confirmada',
    UNIQUE KEY uq_reserva_act_vis (codigo_actividad, codigo_visitante),
    CONSTRAINT fk_res_act FOREIGN KEY (codigo_actividad) REFERENCES Actividad(codigo_actividad)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_res_vis FOREIGN KEY (codigo_visitante) REFERENCES Visitantes(codigo_visitante)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE Evaluaciones (
    codigo_actividad VARCHAR(10) NOT NULL,
    numero_correlativo INT NOT NULL,
    puntuacion_general INT NOT NULL CHECK (puntuacion_general BETWEEN 1 AND 5),
    calidad_explicacion INT NOT NULL CHECK (calidad_explicacion BETWEEN 1 AND 5),
    calidad_instrumental INT NOT NULL CHECK (calidad_instrumental BETWEEN 1 AND 5),
    comentario VARCHAR(255),
    fecha_evaluacion DATE NOT NULL,
    PRIMARY KEY (codigo_actividad, numero_correlativo),
    CONSTRAINT fk_eval_act FOREIGN KEY (codigo_actividad) REFERENCES Actividad(codigo_actividad)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 5. VISTAS ANALÍTICAS (R2, R3, R5, R6, R7, R8)
-- ============================================================================

CREATE OR REPLACE VIEW vw_R2_distribucion_fenomenos AS
SELECT c.nombre AS centro_astronomico, z.nombre_zona,
       CASE
           WHEN fs.codigo_fenomeno IS NOT NULL THEN 'Solar'
           WHEN fl.codigo_fenomeno IS NOT NULL THEN 'Lunar'
           WHEN fep.codigo_fenomeno IS NOT NULL THEN 'Espacio Profundo'
       END AS tipo_fenomeno,
       COUNT(*) AS cantidad_observaciones
FROM Actividad a
JOIN Zonas_observacion z ON a.codigo_zona = z.codigo_zona
JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
JOIN Actividad_fenomeno af ON a.codigo_actividad = af.codigo_actividad
LEFT JOIN Fenomenos_solares fs ON af.codigo_fenomeno = fs.codigo_fenomeno
LEFT JOIN Fenomenos_lunares fl ON af.codigo_fenomeno = fl.codigo_fenomeno
LEFT JOIN Fenomenos_espacios_profundos fep ON af.codigo_fenomeno = fep.codigo_fenomeno
WHERE fs.codigo_fenomeno IS NOT NULL OR fl.codigo_fenomeno IS NOT NULL OR fep.codigo_fenomeno IS NOT NULL
GROUP BY c.nombre, z.nombre_zona, tipo_fenomeno;

CREATE OR REPLACE VIEW vw_R3_asistentes_vs_evaluacion AS
SELECT a.codigo_actividad, c.nombre AS centro_astronomico, a.fecha, a.modalidad,
       COUNT(DISTINCT CASE WHEN r.asistencia_efectiva = 1 THEN r.codigo_reserva END) AS total_asistentes,
       ROUND(AVG(e.puntuacion_general), 2) AS evaluacion_promedio
FROM Actividad a
JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
LEFT JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
LEFT JOIN Evaluaciones e ON a.codigo_actividad = e.codigo_actividad
GROUP BY a.codigo_actividad, c.nombre, a.fecha, a.modalidad
ORDER BY total_asistentes DESC;

CREATE OR REPLACE VIEW vw_R5_tasa_asistencia_zonas AS
SELECT c.nombre AS centro_astronomico, z.codigo_zona, z.nombre_zona,
       COUNT(r.codigo_reserva) AS reservas_totales,
       SUM(CASE WHEN r.asistencia_efectiva = 1 THEN 1 ELSE 0 END) AS asistencias_efectivas,
       ROUND((SUM(CASE WHEN r.asistencia_efectiva = 1 THEN 1 ELSE 0 END) / COUNT(r.codigo_reserva)) * 100, 2) AS tasa_asistencia_pct
FROM Zonas_observacion z
JOIN Centro_astronomico c ON z.codigo_centro = c.codigo_centro
JOIN Actividad a ON z.codigo_zona = a.codigo_zona
JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
WHERE r.estado <> 'Cancelada'
GROUP BY c.nombre, z.codigo_zona, z.nombre_zona
ORDER BY tasa_asistencia_pct DESC;

CREATE OR REPLACE VIEW vw_R6_ranking_fenomenos_zona AS
SELECT c.nombre AS centro_astronomico, z.nombre_zona, f.nombre_fenomeno,
       COUNT(*) AS total_registros,
       RANK() OVER (PARTITION BY c.codigo_centro, z.codigo_zona ORDER BY COUNT(*) DESC) AS ranking_zona
FROM Actividad a
JOIN Centro_astronomico c ON a.codigo_centro = c.codigo_centro
JOIN Zonas_observacion z ON a.codigo_zona = z.codigo_zona
JOIN Actividad_fenomeno af ON a.codigo_actividad = af.codigo_actividad
JOIN Fenomenos f ON af.codigo_fenomeno = f.codigo_fenomeno
GROUP BY c.codigo_centro, c.nombre, z.codigo_zona, z.nombre_zona, f.codigo_fenomeno, f.nombre_fenomeno;

CREATE OR REPLACE VIEW vw_R7_diversidad_fenomenos_centro AS
SELECT c.nombre AS centro_astronomico,
       COUNT(DISTINCT f.codigo_fenomeno) AS fenomenos_distintos,
       ROUND(SUM(CASE WHEN fs.codigo_fenomeno IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_solar,
       ROUND(SUM(CASE WHEN fl.codigo_fenomeno IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_lunar,
       ROUND(SUM(CASE WHEN fep.codigo_fenomeno IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_espacio_profundo
FROM Centro_astronomico c
JOIN Actividad a ON c.codigo_centro = a.codigo_centro
JOIN Actividad_fenomeno af ON a.codigo_actividad = af.codigo_actividad
JOIN Fenomenos f ON af.codigo_fenomeno = f.codigo_fenomeno
LEFT JOIN Fenomenos_solares fs ON f.codigo_fenomeno = fs.codigo_fenomeno
LEFT JOIN Fenomenos_lunares fl ON f.codigo_fenomeno = fl.codigo_fenomeno
LEFT JOIN Fenomenos_espacios_profundos fep ON f.codigo_fenomeno = fep.codigo_fenomeno
GROUP BY c.codigo_centro, c.nombre;

CREATE OR REPLACE VIEW vw_R8_top_visitantes_valor AS
SELECT v.codigo_visitante, v.nombre, v.apellido, v.pais_origen,
       COUNT(r.codigo_reserva) AS actividades_asistidas,
       SUM(a.precio) AS valor_total_generado
FROM Visitantes v
JOIN Reservas r ON v.codigo_visitante = r.codigo_visitante
JOIN Actividad a ON r.codigo_actividad = a.codigo_actividad
WHERE r.asistencia_efectiva = 1
GROUP BY v.codigo_visitante, v.nombre, v.apellido, v.pais_origen
ORDER BY actividades_asistidas DESC, valor_total_generado DESC;

-- ============================================================================
-- 6. PROCEDIMIENTOS ALMACENADOS PARAMETRIZADOS (R1, R4, R9, R10, R11, R12)
-- ============================================================================
DELIMITER //

CREATE PROCEDURE sp_R1_zonas_mas_visitadas(IN p_fecha_inicio DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT c.nombre AS centro_astronomico, z.codigo_zona, z.nombre_zona,
           COUNT(r.codigo_reserva) AS total_visitantes_efectivos
    FROM Zonas_observacion z
    JOIN Centro_astronomico c ON z.codigo_centro = c.codigo_centro
    JOIN Actividad a ON z.codigo_zona = a.codigo_zona
    JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
    WHERE r.asistencia_efectiva = 1
      AND a.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    GROUP BY c.nombre, z.codigo_zona, z.nombre_zona
    ORDER BY total_visitantes_efectivos DESC;
END //

CREATE PROCEDURE sp_R4_centros_actividad_visitantes(IN p_fecha_inicio DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT c.codigo_centro, c.nombre AS centro_astronomico,
           COUNT(DISTINCT a.codigo_actividad) AS total_actividades,
           COUNT(CASE WHEN r.asistencia_efectiva = 1 THEN r.codigo_reserva END) AS total_visitantes
    FROM Centro_astronomico c
    LEFT JOIN Actividad a ON c.codigo_centro = a.codigo_centro AND a.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    LEFT JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
    GROUP BY c.codigo_centro, c.nombre
    ORDER BY total_actividades DESC, total_visitantes DESC;
END //

CREATE PROCEDURE sp_R9_actividades_sobre_promedio_centro(IN p_codigo_centro VARCHAR(10), IN p_fecha_inicio DATE, IN p_fecha_fin DATE)
BEGIN
    WITH AsistenciaActividad AS (
        SELECT a.codigo_actividad, a.fecha, a.modalidad,
               COUNT(CASE WHEN r.asistencia_efectiva = 1 THEN r.codigo_reserva END) AS asistentes
        FROM Actividad a
        LEFT JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
        WHERE a.codigo_centro = p_codigo_centro AND a.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
        GROUP BY a.codigo_actividad, a.fecha, a.modalidad
    )
    SELECT * FROM AsistenciaActividad
    WHERE asistentes > (SELECT AVG(asistentes) FROM AsistenciaActividad)
    ORDER BY asistentes DESC;
END //

CREATE PROCEDURE sp_R10_zonas_oscuridad_superior(IN p_codigo_centro VARCHAR(10))
BEGIN
    SELECT z.codigo_zona, z.nombre_zona, z.indice_oscuridad,
           a.codigo_actividad, a.fecha, a.modalidad
    FROM Zonas_observacion z
    LEFT JOIN Actividad a ON z.codigo_zona = a.codigo_zona
    WHERE z.codigo_centro = p_codigo_centro
      AND z.indice_oscuridad > (
          SELECT AVG(indice_oscuridad) FROM Zonas_observacion WHERE codigo_centro = p_codigo_centro
      )
    ORDER BY z.indice_oscuridad DESC, a.fecha DESC;
END //

CREATE PROCEDURE sp_R11_visitantes_destacados(IN p_fecha_inicio DATE, IN p_fecha_fin DATE)
BEGIN
    WITH MetricasVisitante AS (
        SELECT v.codigo_visitante, v.nombre, v.apellido,
               COUNT(DISTINCT r.codigo_reserva) AS total_asistencias,
               AVG(e.puntuacion_general) AS promedio_nota
        FROM Visitantes v
        JOIN Reservas r ON v.codigo_visitante = r.codigo_visitante AND r.asistencia_efectiva = 1
        JOIN Actividad a ON r.codigo_actividad = a.codigo_actividad AND a.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
        LEFT JOIN Evaluaciones e ON a.codigo_actividad = e.codigo_actividad
        GROUP BY v.codigo_visitante, v.nombre, v.apellido
    )
    SELECT codigo_visitante, nombre, apellido, total_asistencias, ROUND(promedio_nota, 2) AS promedio_nota
    FROM MetricasVisitante
    WHERE total_asistencias > (SELECT AVG(total_asistencias) FROM MetricasVisitante)
      AND promedio_nota > (SELECT AVG(promedio_nota) FROM MetricasVisitante);
END //

CREATE PROCEDURE sp_R12_centros_sobre_promedio_general(IN p_fecha_inicio DATE, IN p_fecha_fin DATE)
BEGIN
    WITH PromedioPorCentro AS (
        SELECT c.codigo_centro, c.nombre AS centro_astronomico,
               COUNT(CASE WHEN r.asistencia_efectiva = 1 THEN r.codigo_reserva END) / COUNT(DISTINCT a.codigo_actividad) AS prom_asistentes_sesion
        FROM Centro_astronomico c
        JOIN Actividad a ON c.codigo_centro = a.codigo_centro AND a.fecha BETWEEN p_fecha_inicio AND p_fecha_fin
        LEFT JOIN Reservas r ON a.codigo_actividad = r.codigo_actividad
        GROUP BY c.codigo_centro, c.nombre
    )
    SELECT codigo_centro, centro_astronomico, ROUND(prom_asistentes_sesion, 2) AS promedio_asistentes_actividad
    FROM PromedioPorCentro
    WHERE prom_asistentes_sesion > (SELECT AVG(prom_asistentes_sesion) FROM PromedioPorCentro)
    ORDER BY promedio_asistentes_actividad DESC;
END //

DELIMITER ;
