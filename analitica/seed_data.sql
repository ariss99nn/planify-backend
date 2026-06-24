-- Seed data for analitica app
-- Requires programa seeds before running.
BEGIN;

INSERT INTO analitica_analiticasnapshot (id, fecha, fichas_activas, fichas_lectiva, fichas_productiva, estudiantes_activos, deserciones_mes, graduados_mes, reasignaciones_mes, docentes_activos, docentes_sobrecargados, aulas_activas, aulas_mantenimiento, aulas_inactivas, planes_aprobados, planes_pendientes, alertas_pendientes, conflictos_horario_mes, created_at)
VALUES
(1, '2026-01-31', 5, 3, 2, 120, 2, 1, 1, 25, 3, 20, 1, 2, 2, 1, 3, 4, '2026-06-01 16:55:00'),
(2, '2026-02-28', 6, 4, 2, 125, 1, 2, 2, 26, 2, 21, 1, 1, 3, 1, 2, 5, '2026-06-01 17:00:00'),
(3, '2026-03-31', 6, 4, 2, 128, 1, 1, 3, 27, 4, 22, 1, 1, 4, 2, 3, 6, '2026-06-01 17:05:00'),
(4, '2026-04-30', 5, 3, 2, 130, 0, 1, 2, 26, 4, 20, 2, 1, 3, 2, 2, 4, '2026-06-01 17:10:00'),
(5, '2026-05-31', 7, 5, 2, 132, 1, 2, 4, 28, 5, 23, 1, 1, 5, 1, 3, 7, '2026-06-01 17:15:00');

INSERT INTO analitica_snapshotprograma (id, snapshot_id, programa_id, fichas_activas, fichas_lectiva, fichas_productiva, estudiantes_activos, deserciones_mes, graduados_mes, avance_curricular_pct, horas_planificadas, horas_ejecutadas)
VALUES
(1, 1, 1, 1, 1, 0, 25, 0, 0, 35.0, 120, 80),
(2, 2, 2, 1, 1, 0, 24, 0, 1, 40.0, 110, 75),
(3, 3, 3, 2, 1, 0, 26, 0, 1, 30.0, 130, 90),
(4, 4, 4, 1, 0, 1, 27, 0, 0, 25.0, 140, 100),
(5, 5, 5, 2, 1, 1, 30, 1, 0, 50.0, 60, 45);

COMMIT;
