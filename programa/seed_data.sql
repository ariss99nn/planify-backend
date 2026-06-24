-- Seed data for programa app
-- Requires users seeded first only if you want user-related cross references later.
BEGIN;

INSERT INTO programa_programa (id, nombre, descripcion, nivel, horas_lectivas, horas_practicas, estado, trimestres_totales, tipo_formacion, trimestres_cadena, created_at, updated_at)
VALUES
(1, 'Programación Básica', 'Programa técnico en fundamentos de programación.', 'TECNICO', 300, 120, 'ACTIVO', 6, 'POR_OFERTA', 0, '2026-06-01 09:00:00', '2026-06-01 09:00:00'),
(2, 'Gestión de Redes', 'Programa técnico para administración de redes.', 'TECNICO', 280, 100, 'ACTIVO', 6, 'POR_OFERTA', 0, '2026-06-01 09:05:00', '2026-06-01 09:05:00'),
(3, 'Desarrollo Web', 'Programa tecnología con foco en aplicaciones web.', 'TECNOLOGIA', 320, 140, 'ACTIVO', 8, 'POR_OFERTA', 0, '2026-06-01 09:10:00', '2026-06-01 09:10:00'),
(4, 'Seguridad Informática', 'Programa tecnología en ciberseguridad.', 'TECNOLOGIA', 330, 150, 'ACTIVO', 8, 'POR_OFERTA', 0, '2026-06-01 09:15:00', '2026-06-01 09:15:00'),
(5, 'Curso Corto de Python', 'Curso corto de programación en Python.', 'CURSO_CORTO', 60, 20, 'ACTIVO', 1, 'POR_OFERTA', 0, '2026-06-01 09:20:00', '2026-06-01 09:20:00');

INSERT INTO programa_versionprograma (id, programa_id, numero, descripcion, vigente, fecha_inicio, fecha_fin, created_at, updated_at)
VALUES
(1, 1, 1, 'Versión inicial del programa de programación básica.', TRUE, '2026-01-01', '2026-12-31', '2026-06-01 09:30:00', '2026-06-01 09:30:00'),
(2, 2, 1, 'Versión inicial del programa de gestión de redes.', TRUE, '2026-01-01', '2026-12-31', '2026-06-01 09:35:00', '2026-06-01 09:35:00'),
(3, 3, 1, 'Versión inicial del programa de desarrollo web.', TRUE, '2026-01-01', '2026-12-31', '2026-06-01 09:40:00', '2026-06-01 09:40:00'),
(4, 4, 1, 'Versión inicial del programa de seguridad informática.', TRUE, '2026-01-01', '2026-12-31', '2026-06-01 09:45:00', '2026-06-01 09:45:00'),
(5, 5, 1, 'Versión inicial del curso corto de Python.', TRUE, '2026-01-01', '2026-12-31', '2026-06-01 09:50:00', '2026-06-01 09:50:00');

INSERT INTO programa_modulo (id, version_id, nombre, descripcion, orden, horas_lectivas, horas_practicas, estado, created_at, updated_at)
VALUES
(1, 1, 'Módulo de Lógica', 'Fundamentos de lógica y algoritmos.', 1, 100, 40, 'ACTIVO', '2026-06-01 09:55:00', '2026-06-01 09:55:00'),
(2, 2, 'Módulo de Redes Básicas', 'Conceptos iniciales de redes.', 1, 90, 30, 'ACTIVO', '2026-06-01 10:00:00', '2026-06-01 10:00:00'),
(3, 3, 'Módulo de Frontend', 'Desarrollo de interfaces web.', 1, 110, 50, 'ACTIVO', '2026-06-01 10:05:00', '2026-06-01 10:05:00'),
(4, 4, 'Módulo de Ciberseguridad', 'Fundamentos de seguridad informática.', 1, 120, 40, 'ACTIVO', '2026-06-01 10:10:00', '2026-06-01 10:10:00'),
(5, 5, 'Módulo de Python Básico', 'Introducción al lenguaje Python.', 1, 50, 15, 'ACTIVO', '2026-06-01 10:15:00', '2026-06-01 10:15:00');

COMMIT;
