-- Seed data for users app
-- Run this first, before other app seed files.
BEGIN;

INSERT INTO users_user (id, password, email, nombre, apellido, email_verificado, rol, is_active, is_staff, is_superuser, last_login, date_joined, fecha_creacion, fecha_modificacion)
VALUES
(1, 'pbkdf2_sha256$260000$sample$samplehash1', 'admin@example.com', 'Admin', 'Principal', TRUE, 'ADMINISTRATIVO', TRUE, TRUE, TRUE, NULL, '2026-06-01 09:00:00', '2026-06-01 09:00:00', '2026-06-01 09:00:00'),
(2, 'pbkdf2_sha256$260000$sample$samplehash2', 'coord@example.com', 'Coordinador', 'Central', TRUE, 'COORDINADOR', TRUE, TRUE, FALSE, NULL, '2026-06-01 09:05:00', '2026-06-01 09:05:00', '2026-06-01 09:05:00'),
(3, 'pbkdf2_sha256$260000$sample$samplehash3', 'docente1@example.com', 'Docente', 'Uno', TRUE, 'DOCENTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:10:00', '2026-06-01 09:10:00', '2026-06-01 09:10:00'),
(4, 'pbkdf2_sha256$260000$sample$samplehash4', 'docente2@example.com', 'Docente', 'Dos', TRUE, 'DOCENTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:15:00', '2026-06-01 09:15:00', '2026-06-01 09:15:00'),
(5, 'pbkdf2_sha256$260000$sample$samplehash5', 'docente3@example.com', 'Docente', 'Tres', TRUE, 'DOCENTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:20:00', '2026-06-01 09:20:00', '2026-06-01 09:20:00'),
(6, 'pbkdf2_sha256$260000$sample$samplehash6', 'docente4@example.com', 'Docente', 'Cuatro', TRUE, 'DOCENTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:25:00', '2026-06-01 09:25:00', '2026-06-01 09:25:00'),
(7, 'pbkdf2_sha256$260000$sample$samplehash7', 'docente5@example.com', 'Docente', 'Cinco', TRUE, 'DOCENTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:30:00', '2026-06-01 09:30:00', '2026-06-01 09:30:00'),
(8, 'pbkdf2_sha256$260000$sample$samplehash8', 'estudiante1@example.com', 'Estudiante', 'Uno', TRUE, 'ESTUDIANTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:35:00', '2026-06-01 09:35:00', '2026-06-01 09:35:00'),
(9, 'pbkdf2_sha256$260000$sample$samplehash9', 'estudiante2@example.com', 'Estudiante', 'Dos', TRUE, 'ESTUDIANTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:40:00', '2026-06-01 09:40:00', '2026-06-01 09:40:00'),
(10, 'pbkdf2_sha256$260000$sample$samplehash10', 'estudiante3@example.com', 'Estudiante', 'Tres', TRUE, 'ESTUDIANTE', TRUE, FALSE, FALSE, NULL, '2026-06-01 09:45:00', '2026-06-01 09:45:00', '2026-06-01 09:45:00');

INSERT INTO users_emailchangerequest (id, user_id, new_email, code, created_at, expires_at, is_used)
VALUES
(1, 1, 'admin.new@example.com', '111111', '2026-06-01 10:00:00', '2026-06-08 10:00:00', FALSE),
(2, 2, 'coord.new@example.com', '222222', '2026-06-01 10:05:00', '2026-06-08 10:05:00', FALSE),
(3, 3, 'docente1.new@example.com', '333333', '2026-06-01 10:10:00', '2026-06-08 10:10:00', FALSE),
(4, 4, 'docente2.new@example.com', '444444', '2026-06-01 10:15:00', '2026-06-08 10:15:00', FALSE),
(5, 5, 'docente3.new@example.com', '555555', '2026-06-01 10:20:00', '2026-06-08 10:20:00', FALSE);

INSERT INTO users_emailverification (id, user_id, code, created_at, expires_at, is_used, is_verified, verified_at)
VALUES
(1, 6, 'AV0001', '2026-06-01 10:30:00', '2026-06-08 10:30:00', FALSE, FALSE, NULL),
(2, 7, 'AV0002', '2026-06-01 10:35:00', '2026-06-08 10:35:00', FALSE, FALSE, NULL),
(3, 8, 'AV0003', '2026-06-01 10:40:00', '2026-06-08 10:40:00', FALSE, FALSE, NULL),
(4, 9, 'AV0004', '2026-06-01 10:45:00', '2026-06-08 10:45:00', FALSE, FALSE, NULL),
(5, 10, 'AV0005', '2026-06-01 10:50:00', '2026-06-08 10:50:00', FALSE, FALSE, NULL);

INSERT INTO users_passwordreset (id, user_id, token, code, created_at, expires_at, is_used)
VALUES
(1, 1, '11111111-1111-1111-1111-111111111111', 'PR0001', '2026-06-01 11:00:00', '2026-06-08 11:00:00', FALSE),
(2, 2, '22222222-2222-2222-2222-222222222222', 'PR0002', '2026-06-01 11:05:00', '2026-06-08 11:05:00', FALSE),
(3, 3, '33333333-3333-3333-3333-333333333333', 'PR0003', '2026-06-01 11:10:00', '2026-06-08 11:10:00', FALSE),
(4, 4, '44444444-4444-4444-4444-444444444444', 'PR0004', '2026-06-01 11:15:00', '2026-06-08 11:15:00', FALSE),
(5, 5, '55555555-5555-5555-5555-555555555555', 'PR0005', '2026-06-01 11:20:00', '2026-06-08 11:20:00', FALSE);

COMMIT;
