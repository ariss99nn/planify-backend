-- Seed data for docentes app
-- Requires users and programa/competencia/aulas seeds.
BEGIN;

INSERT INTO docentes_docente (id, user_id, especialidad, horas_max_semanales, permite_horas_extra, horas_extra_autorizadas, estado, imagen)
VALUES
(1, 3, 'Programación', 40, TRUE, 5, TRUE, NULL),
(2, 4, 'Redes', 40, FALSE, 0, TRUE, NULL),
(3, 5, 'Seguridad', 40, TRUE, 10, TRUE, NULL),
(4, 6, 'Desarrollo Web', 40, FALSE, 0, TRUE, NULL),
(5, 7, 'Bases de Datos', 40, FALSE, 0, TRUE, NULL);

INSERT INTO docentes_disponibilidad (id, docente_id, dia_semana, hora_inicio, hora_fin, disponible, motivo, tipo_restriccion, fecha_inicio_restriccion, fecha_fin_restriccion, created_at, updated_at)
VALUES
(1, 1, 'LUNES', '08:00:00', '12:00:00', TRUE, '', 'PERMANENTE', NULL, NULL, '2026-06-01 11:40:00', '2026-06-01 11:40:00'),
(2, 2, 'MARTES', '10:00:00', '14:00:00', TRUE, '', 'PERMANENTE', NULL, NULL, '2026-06-01 11:45:00', '2026-06-01 11:45:00'),
(3, 3, 'MIERCOLES', '09:00:00', '13:00:00', FALSE, 'Reunión de coordinación', 'TEMPORAL', '2026-06-15', '2026-06-20', '2026-06-01 11:50:00', '2026-06-01 11:50:00'),
(4, 4, 'JUEVES', '14:00:00', '18:00:00', TRUE, '', 'PERMANENTE', NULL, NULL, '2026-06-01 11:55:00', '2026-06-01 11:55:00'),
(5, 5, 'VIERNES', '08:00:00', '10:00:00', TRUE, '', 'PERMANENTE', NULL, NULL, '2026-06-01 12:00:00', '2026-06-01 12:00:00');

INSERT INTO docentes_habilitaciondocente (id, docente_id, nivel, modulo_id, asignatura_id, activo, fecha_desde, fecha_hasta, observaciones, created_at, updated_at)
VALUES
(1, 1, 'MODULO', 1, NULL, TRUE, '2026-01-01', NULL, 'Habilitado en módulo completo.', '2026-06-01 12:05:00', '2026-06-01 12:05:00'),
(2, 2, 'MODULO', 2, NULL, TRUE, '2026-01-01', NULL, 'Habilitado en módulo completo.', '2026-06-01 12:10:00', '2026-06-01 12:10:00'),
(3, 3, 'MODULO', 3, NULL, TRUE, '2026-01-01', NULL, 'Habilitado en módulo completo.', '2026-06-01 12:15:00', '2026-06-01 12:15:00'),
(4, 4, 'ASIGNATURA', NULL, 4, TRUE, '2026-02-01', NULL, 'Habilitación en asignatura específica.', '2026-06-01 12:20:00', '2026-06-01 12:20:00'),
(5, 5, 'ASIGNATURA', NULL, 5, TRUE, '2026-02-01', NULL, 'Habilitación en asignatura específica.', '2026-06-01 12:25:00', '2026-06-01 12:25:00');

COMMIT;
