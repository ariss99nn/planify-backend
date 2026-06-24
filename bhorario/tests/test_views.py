from datetime import time
from django.test import TestCase
from rest_framework.test import APIClient
from bhorario.tests.factories import make_bloque
from bhorario.models.bloque_horario_model import BloqueHorario
from docentes.tests.factories import make_docente
from aulas.tests.factories import make_aula
from users.tests.factories import (
    make_coordinador, make_administrativo,
    make_docente as make_docente_user,
    make_estudiante, get_auth_header,
)


class BloqueHorarioViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_bh@test.com')
        self.admin = make_administrativo(email='admin_bh@test.com')
        self.docente_user = make_docente_user(email='doc_bh@test.com')
        self.docente = make_docente(user=self.docente_user)
        self.estudiante = make_estudiante(email='est_bh@test.com')
        self.aula = make_aula()
        self.bloque = make_bloque(
            aula=self.aula,
            docente=self.docente,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )

    def test_coord_lista_todos(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/horarios/', **headers)
        self.assertEqual(r.status_code, 200)

    def test_docente_ve_sus_bloques(self):
        otro_docente_user = make_docente_user(email='otro_bh@test.com')
        otro_docente = make_docente(user=otro_docente_user)
        otro_bloque = make_bloque(docente=otro_docente, hora_inicio=time(14, 0), hora_fin=time(16, 0))
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get('/api/horarios/', **headers)
        self.assertEqual(r.status_code, 200)
        ids = [b['id'] for b in r.data['results']]
        self.assertIn(self.bloque.pk, ids)
        self.assertNotIn(otro_bloque.pk, ids)

    def test_sin_autenticacion(self):
        r = self.client.get('/api/horarios/')
        self.assertEqual(r.status_code, 401)

    def test_coord_crea_bloque(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/horarios/create/', {
            'dia_semana': BloqueHorario.DiaSemana.MARTES,
            'hora_inicio': '14:00',
            'hora_fin': '16:00',
            'jornada': BloqueHorario.Jornada.TARDE,
            'aula': self.aula.pk,
            'docente': self.docente.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post('/api/horarios/create/', {
            'dia_semana': BloqueHorario.DiaSemana.JUEVES,
            'hora_inicio': '06:00',
            'hora_fin': '08:00',
            'jornada': BloqueHorario.Jornada.MANANA,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_conflicto_docente_rechazado(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/horarios/create/', {
            'dia_semana': BloqueHorario.DiaSemana.LUNES,
            'hora_inicio': '08:30',
            'hora_fin': '10:30',
            'jornada': BloqueHorario.Jornada.MANANA,
            'docente': self.docente.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 400)

    def test_coord_actualiza_bloque(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.patch(
            f'/api/horarios/{self.bloque.pk}/update/',
            {'jornada': BloqueHorario.Jornada.TARDE},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)

    def test_not_found(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.get('/api/horarios/99999/', **headers)
        self.assertEqual(r.status_code, 404)


class AlertaViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.coord = make_coordinador(email='coord_al@test.com')
        self.docente_user = make_docente_user(email='doc_al@test.com')
        self.estudiante = make_estudiante(email='est_al@test.com')

    def test_coord_crea_alerta(self):
        headers = get_auth_header(self.client, self.coord)
        r = self.client.post('/api/alertas/create/', {
            'tipo': 'SISTEMA',
            'descripcion': 'Mantenimiento programado',
            'formato_alerta': 'APP',
            'destinatario': self.docente_user.pk,
        }, format='json', **headers)
        self.assertEqual(r.status_code, 201)

    def test_docente_no_puede_crear_alerta(self):
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.post('/api/alertas/create/', {
            'tipo': 'SISTEMA',
            'descripcion': 'Intento',
            'formato_alerta': 'APP',
        }, format='json', **headers)
        self.assertEqual(r.status_code, 403)

    def test_docente_ve_sus_alertas(self):
        from alertas.models.alerta_model import Alerta
        Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Para docente',
            destinatario=self.docente_user,
        )
        Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Para otro',
            destinatario=self.estudiante,
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.get('/api/alertas/', **headers)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)

    def test_docente_marca_alerta_leida(self):
        from alertas.models.alerta_model import Alerta
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Leer esto',
            destinatario=self.docente_user,
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.patch(
            f'/api/alertas/{alerta.pk}/update/',
            {'estado': Alerta.EstadoAlerta.LEIDA},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 200)
        alerta.refresh_from_db()
        self.assertEqual(alerta.estado, Alerta.EstadoAlerta.LEIDA)
        self.assertIsNotNone(alerta.fecha_lectura)

    def test_docente_no_puede_actualizar_alerta_ajena(self):
        from alertas.models.alerta_model import Alerta
        alerta = Alerta.objects.create(
            tipo=Alerta.TipoAlerta.SISTEMA,
            descripcion='Ajena',
            destinatario=self.estudiante,
        )
        headers = get_auth_header(self.client, self.docente_user)
        r = self.client.patch(
            f'/api/alertas/{alerta.pk}/update/',
            {'estado': Alerta.EstadoAlerta.LEIDA},
            format='json',
            **headers,
        )
        self.assertEqual(r.status_code, 403)