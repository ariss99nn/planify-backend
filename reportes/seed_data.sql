-- Seed data for reportes app
-- Requires users and contenttypes to exist.
BEGIN;

INSERT INTO reportes_novedad (id, tipo, prioridad, titulo, descripcion, content_type_id, object_id, generada_por_sistema, generada_por_id, atendida, atendida_por_id, fecha_atencion, nota_atencion, fecha_generacion, fecha_expiracion)
VALUES
(1, 'FICHA_SIN_PLAN', 1, 'Ficha sin plan aprobado', 'La ficha no cuenta con plan aprobado a tiempo.', (SELECT id FROM django_content_type WHERE app_label='auth' LIMIT 1), 1, TRUE, NULL, FALSE, NULL, NULL, '', '2026-06-01 16:05:00', NULL),
(2, 'DOCENTE_SOBRECARGADO', 2, 'Docente sobrecargado', 'El docente supera el límite de horas asignadas.', (SELECT id FROM django_content_type WHERE app_label='auth' LIMIT 1), 2, TRUE, NULL, FALSE, NULL, NULL, '', '2026-06-01 16:10:00', NULL),
(3, 'AULA_CONFLICTO', 2, 'Aula con conflicto', 'Asignación simultánea detectada en el aula.', (SELECT id FROM django_content_type WHERE app_label='auth' LIMIT 1), 3, TRUE, NULL, FALSE, NULL, NULL, '', '2026-06-01 16:15:00', NULL),
(4, 'AVANCE_BAJO', 3, 'Avance curricular bajo', 'El avance de la ficha está por debajo del esperado.', (SELECT id FROM django_content_type WHERE app_label='auth' LIMIT 1), 4, TRUE, NULL, FALSE, NULL, NULL, '', '2026-06-01 16:20:00', NULL),
(5, 'OTRA', 3, 'Revisión administrativa pendiente', 'Se requiere revisión manual de la novedad.', (SELECT id FROM django_content_type WHERE app_label='auth' LIMIT 1), 5, TRUE, NULL, FALSE, NULL, NULL, '', '2026-06-01 16:25:00', NULL);

INSERT INTO reportes_reportegenerado (id, tipo, estado, filtros, usuario_id, tarea_id, archivo_pdf, archivo_excel, error_mensaje, created_at, updated_at)
VALUES
(1, 'FICHAS', 'PENDIENTE', '{}', 1, 'task-report-1', 'reportes/pdf/reporte_1.pdf', 'reportes/excel/reporte_1.xlsx', '', '2026-06-01 16:30:00', '2026-06-01 16:30:00'),
(2, 'DOCENTES', 'PROCESANDO', '{}', 2, 'task-report-2', 'reportes/pdf/reporte_2.pdf', 'reportes/excel/reporte_2.xlsx', '', '2026-06-01 16:35:00', '2026-06-01 16:35:00'),
(3, 'HORARIOS', 'LISTO', '{}', 3, 'task-report-3', 'reportes/pdf/reporte_3.pdf', 'reportes/excel/reporte_3.xlsx', '', '2026-06-01 16:40:00', '2026-06-01 16:40:00'),
(4, 'COMPETENCIAS', 'ERROR', '{}', 4, 'task-report-4', NULL, NULL, 'Error al generar el archivo.', '2026-06-01 16:45:00', '2026-06-01 16:45:00'),
(5, 'AULAS', 'LISTO', '{}', 5, 'task-report-5', 'reportes/pdf/reporte_5.pdf', 'reportes/excel/reporte_5.xlsx', '', '2026-06-01 16:50:00', '2026-06-01 16:50:00');

COMMIT;
