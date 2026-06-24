-- Seed data for notificaciones app
-- Requires alertas and users seeds first.
BEGIN;

INSERT INTO notificaciones_notificacion (id, alerta_id, destinatario_id, canal, estado, intentos, error_detalle, tarea_id, fecha_creacion, fecha_envio)
VALUES
(1, 1, 8, 'APP', 'PENDIENTE', 0, '', NULL, '2026-06-01 15:10:00', NULL),
(2, 2, 9, 'EMAIL', 'PENDIENTE', 0, '', NULL, '2026-06-01 15:15:00', NULL),
(3, 3, 10, 'SMS', 'ENVIADA', 1, '', 'task-3', '2026-06-01 15:20:00', '2026-06-01 15:25:00'),
(4, 4, 8, 'APP', 'PENDIENTE', 0, '', NULL, '2026-06-01 15:30:00', NULL),
(5, 5, 9, 'EMAIL', 'PENDIENTE', 0, '', NULL, '2026-06-01 15:35:00', NULL);

COMMIT;
