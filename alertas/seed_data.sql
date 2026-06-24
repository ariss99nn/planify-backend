-- Seed data for alertas app
-- Requires aulas and users seeds first.
BEGIN;

INSERT INTO alertas_alerta (id, tipo, descripcion, formato_alerta, estado, bloque_origen_id, destinatario_id, fecha_creacion, fecha_lectura)
VALUES
(1, 'CONFLICTO', 'Conflicto de horario detectado en Aula A-101.', 'EMAIL', 'PENDIENTE', 1, 8, '2026-06-01 14:45:00', NULL),
(2, 'DISPONIBILIDAD', 'Disponibilidad insuficiente de docente.', 'APP', 'PENDIENTE', 2, 9, '2026-06-01 14:50:00', NULL),
(3, 'SISTEMA', 'Error en la generación de horario.', 'SMS', 'ENVIADA', 3, 10, '2026-06-01 14:55:00', '2026-06-01 15:00:00'),
(4, 'CONFLICTO', 'Aula en mantenimiento asignada en horario.', 'APP', 'PENDIENTE', 4, 8, '2026-06-01 15:00:00', NULL),
(5, 'DISPONIBILIDAD', 'Docente con bloqueo temporal.', 'EMAIL', 'PENDIENTE', 5, 9, '2026-06-01 15:05:00', NULL);

COMMIT;
