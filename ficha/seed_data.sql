-- Seed data for ficha app
-- Requires programa and users seeds before running.
BEGIN;

INSERT INTO ficha_ficha (id, codigo_ficha, version_id, jornada, numero_estudiantes_estimado, etapa, horas_semanales_objetivo, trimestre, estado, cadena_formacion, jefe_grupo_id, fecha_inicio, fecha_finalizacion, created_at, updated_at)
VALUES
(1, 'F001', 1, 'MANANA', 30, 'LECTIVA', 20, 1, 'ACTIVA', FALSE, 1, '2026-01-15', '2026-07-15', '2026-06-01 12:30:00', '2026-06-01 12:30:00'),
(2, 'F002', 2, 'TARDE', 28, 'PRODUCTIVA', 22, 2, 'ACTIVA', TRUE, 1, '2026-02-01', '2026-08-01', '2026-06-01 12:35:00', '2026-06-01 12:35:00'),
(3, 'F003', 3, 'NOCHE', 25, 'LECTIVA', 18, 1, 'ACTIVA', FALSE, 1, '2026-03-01', '2026-09-01', '2026-06-01 12:40:00', '2026-06-01 12:40:00'),
(4, 'F004', 4, 'MIXTA', 20, 'PRODUCTIVA', 24, 3, 'ACTIVA', FALSE, 1, '2026-04-01', '2026-10-01', '2026-06-01 12:45:00', '2026-06-01 12:45:00'),
(5, 'F005', 5, 'MANANA', 32, 'LECTIVA', 20, 1, 'ACTIVA', TRUE, 1, '2026-05-01', '2026-11-01', '2026-06-01 12:50:00', '2026-06-01 12:50:00');

INSERT INTO ficha_fichaestudiante (id, ficha_id, estudiante_id, activo, es_cadena, fecha_ingreso, fecha_retiro, motivo_retiro)
VALUES
(1, 1, 8, TRUE, FALSE, '2026-01-16', NULL, ''),
(2, 2, 9, TRUE, TRUE, '2026-02-02', NULL, ''),
(3, 3, 10, TRUE, FALSE, '2026-03-02', NULL, ''),
(4, 4, 8, TRUE, FALSE, '2026-04-02', NULL, ''),
(5, 5, 9, TRUE, TRUE, '2026-05-02', NULL, 'Reingreso en trámite');

INSERT INTO ficha_historialetapa (id, ficha_id, etapa_anterior, etapa_nueva, trimestre, fecha, cambiado_por_id)
VALUES
(1, 1, 'LECTIVA', 'PRODUCTIVA', 2, '2026-02-15 09:00:00', 2),
(2, 2, 'PRODUCTIVA', 'LECTIVA', 3, '2026-03-15 09:00:00', 2),
(3, 3, 'LECTIVA', 'PRODUCTIVA', 1, '2026-04-15 09:00:00', 2),
(4, 4, 'PRODUCTIVA', 'LECTIVA', 3, '2026-05-15 09:00:00', 2),
(5, 5, 'LECTIVA', 'PRODUCTIVA', 1, '2026-06-15 09:00:00', 2);

INSERT INTO ficha_reasignacionficha (id, estudiante_id, ficha_origen_id, ficha_destino_id, motivo, realizado_por_id, fecha)
VALUES
(1, 8, 1, 2, 'Cambio de etapa productiva.', 2, '2026-06-01 13:00:00'),
(2, 9, 2, 3, 'Ajuste de cupo en fichas.', 2, '2026-06-01 13:05:00'),
(3, 10, 3, 4, 'Optó por cambio de programa.', 2, '2026-06-01 13:10:00'),
(4, 8, 4, 5, 'Reubicación por horario.', 2, '2026-06-01 13:15:00'),
(5, 9, 5, 1, 'Retorno a ciclo anterior.', 2, '2026-06-01 13:20:00');

COMMIT;
