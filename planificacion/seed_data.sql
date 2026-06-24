-- Seed data for planificacion app
-- Requires ficha, competencia, docentes, and aulas/bhorario seeds.
BEGIN;

INSERT INTO planificacion_plantrimestral (id, estado, aprobado_por_id, fecha_aprobacion, motivo_rechazo, ficha_id, trimestre, fecha_inicio, fecha_fin, created_at, updated_at)
VALUES
(1, 'BORRADOR', NULL, NULL, '', 1, 1, '2026-01-15', '2026-04-15', '2026-06-01 13:55:00', '2026-06-01 13:55:00'),
(2, 'APROBADO', 2, '2026-02-01 12:00:00', '', 2, 2, '2026-02-01', '2026-05-01', '2026-06-01 14:00:00', '2026-06-01 14:00:00'),
(3, 'EN_EJECUCION', 2, '2026-03-01 12:00:00', '', 3, 1, '2026-03-01', '2026-06-01', '2026-06-01 14:05:00', '2026-06-01 14:05:00'),
(4, 'RECHAZADO', NULL, NULL, 'Faltan horas de docente.', 4, 3, '2026-04-01', '2026-07-01', '2026-06-01 14:10:00', '2026-06-01 14:10:00'),
(5, 'CERRADO', 2, '2026-05-01 12:00:00', '', 5, 1, '2026-05-01', '2026-08-01', '2026-06-01 14:15:00', '2026-06-01 14:15:00');

INSERT INTO planificacion_itemplan (id, plan_id, competencia_id, docente_id, horas_asignadas, orden, completado)
VALUES
(1, 1, 1, 1, 20, 1, FALSE),
(2, 2, 2, 2, 18, 2, TRUE),
(3, 3, 3, 3, 22, 3, FALSE),
(4, 4, 4, 4, 20, 4, FALSE),
(5, 5, 5, 5, 25, 5, TRUE);

INSERT INTO planificacion_bloquecompetencia (id, bloque_id, item_plan_id, horas_ejecutadas, observaciones, created_at)
VALUES
(1, 1, 1, 0.0, 'Bloque inicial asignado.', '2026-06-01 14:20:00'),
(2, 2, 2, 10.0, 'Avance parcial.', '2026-06-01 14:25:00'),
(3, 3, 3, 5.0, 'Inicio reciente.', '2026-06-01 14:30:00'),
(4, 4, 4, 0.0, 'Pendiente de inicio.', '2026-06-01 14:35:00'),
(5, 5, 5, 18.0, 'Avance significativo.', '2026-06-01 14:40:00');

COMMIT;
