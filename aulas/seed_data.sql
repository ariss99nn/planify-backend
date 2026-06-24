-- Seed data for aulas app
-- Requires no prior app seed, but should run before bhorario and alertas.
BEGIN;

INSERT INTO aulas_bloque (id, nombre, pisos, capacidad_maxima, estado, descripcion, imagen)
VALUES
(1, 'Bloque A', 3, 120, 'ACT', 'Bloque principal del campus.', NULL),
(2, 'Bloque B', 4, 160, 'ACT', 'Bloque de laboratorio.', NULL),
(3, 'Bloque C', 2, 80, 'ACT', 'Bloque de aulas teóricas.', NULL),
(4, 'Bloque D', 1, 40, 'MANT', 'Bloque en mantenimiento.', NULL),
(5, 'Bloque E', 2, 60, 'ACT', 'Bloque de apoyo administrativo.', NULL);

INSERT INTO aulas_equipamiento (id, nombre, descripcion, cantidad, numero_serie, fecha_adquisicion, estado, imagen)
VALUES
(1, 'Proyector', 'Proyector multimedia para presentaciones.', 2, 'EQ-0001', '2024-01-10', 'FUNC', NULL),
(2, 'Computadora', 'Equipo de escritorio con software instalado.', 10, 'EQ-0002', '2024-03-12', 'FUNC', NULL),
(3, 'Pizarra', 'Pizarra blanca con marcadores.', 5, 'EQ-0003', '2023-09-05', 'FUNC', NULL),
(4, 'Cámara', 'Cámara de videoconferencia.', 1, 'EQ-0004', '2024-02-20', 'MANT', NULL),
(5, 'Impresora', 'Impresora láser de red.', 1, 'EQ-0005', '2024-05-18', 'FUNC', NULL);

INSERT INTO aulas_aula (id, codigo_aula, capacidad, tipo_aula, estado, bloque_id, piso, descripcion, imagen)
VALUES
(1, 'A-101', 30, 'TEO', 'ACT', 1, 1, 'Aula teórica principal.', NULL),
(2, 'B-202', 25, 'LAB', 'ACT', 2, 2, 'Laboratorio de redes.', NULL),
(3, 'C-103', 20, 'TEO', 'ACT', 3, 1, 'Aula de matemáticas.', NULL),
(4, 'D-001', 15, 'SIS', 'MANT', 4, 1, 'Aula de sistemas en mantenimiento.', NULL),
(5, 'E-010', 18, 'OTR', 'ACT', 5, 1, 'Aula de apoyo administrativo.', NULL);

INSERT INTO aulas_aula_equipamiento (aula_id, equipamiento_id)
VALUES
(1, 1),
(1, 3),
(2, 2),
(3, 3),
(5, 5);

COMMIT;
