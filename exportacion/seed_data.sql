-- Seed data for exportacion app
-- Requires users seed before running.
BEGIN;

INSERT INTO exportacion_registroexportacion (id, usuario_id, tipo, formato, filtros, registros_exportados, ip_origen, fecha)
VALUES
(1, 1, 'FICHAS', 'EXCEL', '{}', 5, '192.168.1.10', '2026-06-01 15:40:00'),
(2, 2, 'ESTUDIANTES', 'CSV', '{}', 10, '192.168.1.11', '2026-06-01 15:45:00'),
(3, 3, 'DOCENTES', 'JSON', '{}', 5, '192.168.1.12', '2026-06-01 15:50:00'),
(4, 4, 'HORARIOS', 'PDF', '{}', 5, '192.168.1.13', '2026-06-01 15:55:00'),
(5, 5, 'ANALITICA', 'EXCEL', '{}', 7, '192.168.1.14', '2026-06-01 16:00:00');

COMMIT;
