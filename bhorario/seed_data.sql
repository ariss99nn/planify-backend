-- Seed data for bhorario app
-- Requires aulas, docentes, ficha, competencia seeds.
BEGIN;

INSERT INTO bhorario_bloquehorario (id, dia_semana, hora_inicio, hora_fin, jornada, es_recurrente, fecha_especifica, orden_dia, aula_id, docente_id, ficha_id, competencia_id, created_at, updated_at)
VALUES
(1, 'LUNES', '08:00:00', '10:00:00', 'MANANA', TRUE, NULL, 0, 1, 1, 1, 1, '2026-06-01 13:30:00', '2026-06-01 13:30:00'),
(2, 'MARTES', '10:00:00', '12:00:00', 'MANANA', TRUE, NULL, 1, 2, 2, 2, 2, '2026-06-01 13:35:00', '2026-06-01 13:35:00'),
(3, 'MIERCOLES', '14:00:00', '16:00:00', 'TARDE', TRUE, NULL, 2, 3, 3, 3, 3, '2026-06-01 13:40:00', '2026-06-01 13:40:00'),
(4, 'JUEVES', '16:00:00', '18:00:00', 'TARDE', TRUE, NULL, 3, 4, 4, 4, 4, '2026-06-01 13:45:00', '2026-06-01 13:45:00'),
(5, 'VIERNES', '08:00:00', '10:00:00', 'MANANA', TRUE, NULL, 4, 5, 5, 5, 5, '2026-06-01 13:50:00', '2026-06-01 13:50:00');

COMMIT;
