-- Seed data for competencia app
-- Requires programa.seed_data.sql to be applied first.
BEGIN;

INSERT INTO competencia_asignatura (id, modulo_id, nombre, descripcion, tipo, horas_lectivas, horas_practicas, orden, estado, created_at, updated_at)
VALUES
(1, 1, 'Algoritmos I', 'Introducción a los algoritmos.', 'TEORICA', 40, 20, 1, 'ACTIVA', '2026-06-01 10:20:00', '2026-06-01 10:20:00'),
(2, 2, 'Topologías de Red', 'Estudio de topologías de red.', 'TEORICA', 35, 15, 1, 'ACTIVA', '2026-06-01 10:25:00', '2026-06-01 10:25:00'),
(3, 3, 'HTML y CSS', 'Diseño de interfaces web.', 'PRACTICA', 50, 25, 1, 'ACTIVA', '2026-06-01 10:30:00', '2026-06-01 10:30:00'),
(4, 4, 'Fundamentos de Seguridad', 'Bases de ciberseguridad.', 'TEORICO_PRACTICA', 45, 20, 1, 'ACTIVA', '2026-06-01 10:35:00', '2026-06-01 10:35:00'),
(5, 5, 'Python Básico', 'Sintaxis y estructuras de Python.', 'TEORICA', 30, 10, 1, 'ACTIVA', '2026-06-01 10:40:00', '2026-06-01 10:40:00');

INSERT INTO competencia_competencia (id, asignatura_id, tipo, es_induccion, induccion_activa, codigo, nombre, descripcion, horas_trimestre_transversal, created_at, updated_at)
VALUES
(1, 1, 'PRINCIPAL', FALSE, FALSE, 'COMP-001', 'Competencia Lógica', 'Competencia en lógica de programación.', 8, '2026-06-01 10:45:00', '2026-06-01 10:45:00'),
(2, 2, 'PRINCIPAL', FALSE, FALSE, 'COMP-002', 'Competencia Redes', 'Competencia en redes de datos.', 8, '2026-06-01 10:50:00', '2026-06-01 10:50:00'),
(3, 3, 'TRANSVERSAL', FALSE, FALSE, 'COMP-003', 'Competencia Web', 'Competencia en desarrollo web.', 8, '2026-06-01 10:55:00', '2026-06-01 10:55:00'),
(4, 4, 'PRINCIPAL', FALSE, FALSE, 'COMP-004', 'Competencia Seguridad', 'Competencia en ciberseguridad.', 8, '2026-06-01 11:00:00', '2026-06-01 11:00:00'),
(5, 5, 'PRINCIPAL', FALSE, FALSE, 'COMP-005', 'Competencia Python', 'Competencia básica en Python.', 8, '2026-06-01 11:05:00', '2026-06-01 11:05:00');

INSERT INTO competencia_resultadoaprendizaje (id, competencia_id, codigo, descripcion, criterios_evaluacion, created_at, updated_at)
VALUES
(1, 1, 'RA-001', 'Resolver problemas básicos con algoritmos.', 'Ejecutar y documentar soluciones.', '2026-06-01 11:10:00', '2026-06-01 11:10:00'),
(2, 2, 'RA-002', 'Configurar topologías de red simples.', 'Configurar dispositivos y comprobar conectividad.', '2026-06-01 11:15:00', '2026-06-01 11:15:00'),
(3, 3, 'RA-003', 'Desarrollar páginas web estáticas.', 'Construir interfaces HTML y CSS.', '2026-06-01 11:20:00', '2026-06-01 11:20:00'),
(4, 4, 'RA-004', 'Analizar riesgos de seguridad informática.', 'Identificar vulnerabilidades y proponer controles.', '2026-06-01 11:25:00', '2026-06-01 11:25:00'),
(5, 5, 'RA-005', 'Programar scripts simples en Python.', 'Escribir y ejecutar scripts de Python con estructuras de control.', '2026-06-01 11:30:00', '2026-06-01 11:30:00');

COMMIT;
