from datetime import date
from django.test import TestCase, RequestFactory
from ficha.tests.factories import make_ficha, make_ficha_estudiante
from ficha.models.ficha_model import Ficha
from ficha.models.ficha_estudiante_model import FichaEstudiante
from ficha.models.ficha_historial_etapa_model import HistorialEtapa
from ficha.serializers import (
    FichaCreateSerializer,
    FichaUpdateSerializer,
    FichaEtapaUpdateSerializer,
    FichaEstudianteCreateSerializer,
    FichaEstudianteUpdateSerializer,
    ReasignacionCreateSerializer,
)
from programa.tests.factories import make_version
from users.tests.factories import (
    make_coordinador, make_docente, make_estudiante, make_user,
)
from users.models.user import User


class FichaCreateSerializerTest(TestCase):

    def test_create_valido(self):
        version = make_version()
        data = {
            'codigo_ficha': 'TEST-001',
            'version': version.pk,
            'jornada': Ficha.Jornada.MANANA,
            'numero_estudiantes_estimado': 25,
            'etapa': Ficha.Etapa.LECTIVA,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
        }
        s = FichaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        ficha = s.save()
        self.assertEqual(ficha.codigo_ficha, 'TEST-001')

    def test_fecha_fin_anterior_invalida(self):
        version = make_version()
        data = {
            'codigo_ficha': 'TEST-002',
            'version': version.pk,
            'jornada': Ficha.Jornada.TARDE,
            'numero_estudiantes_estimado': 20,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-06-01',
            'fecha_finalizacion': '2024-01-01',
        }
        s = FichaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('fecha_finalizacion', s.errors)

    def test_numero_estudiantes_cero_invalido(self):
        version = make_version()
        data = {
            'codigo_ficha': 'TEST-003',
            'version': version.pk,
            'jornada': Ficha.Jornada.NOCHE,
            'numero_estudiantes_estimado': 0,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
        }
        s = FichaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('numero_estudiantes_estimado', s.errors)

    def test_jefe_grupo_rol_incorrecto_invalido(self):
        version = make_version()
        admin = make_user(rol=User.Rol.ADMIN, email='admin_jefe@test.com')
        data = {
            'codigo_ficha': 'TEST-004',
            'version': version.pk,
            'jornada': Ficha.Jornada.MANANA,
            'numero_estudiantes_estimado': 20,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
            'jefe_grupo': admin.pk,
        }
        s = FichaCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('jefe_grupo', s.errors)

    def test_jefe_grupo_docente_valido(self):
        version = make_version()
        docente = make_docente(email='jefe_valid@test.com')
        data = {
            'codigo_ficha': 'TEST-005',
            'version': version.pk,
            'jornada': Ficha.Jornada.MANANA,
            'numero_estudiantes_estimado': 20,
            'horas_semanales_objetivo': 40,
            'trimestre': 1,
            'fecha_inicio': '2024-01-01',
            'jefe_grupo': docente.pk,
        }
        s = FichaCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)


class FichaEtapaUpdateSerializerTest(TestCase):

    def test_cambio_etapa_crea_historial(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)
        coord = make_coordinador(email='coord_etapa@test.com')
        request = RequestFactory().patch('/')
        request.user = coord
        s = FichaEtapaUpdateSerializer(
            ficha,
            data={'etapa': Ficha.Etapa.PRODUCTIVA},
            context={'request': request},
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        self.assertEqual(
            HistorialEtapa.objects.filter(ficha=ficha).count(), 1
        )

    def test_historial_registra_cambiado_por(self):
        ficha = make_ficha(etapa=Ficha.Etapa.LECTIVA)
        coord = make_coordinador(email='coord_cambio@test.com')
        request = RequestFactory().patch('/')
        request.user = coord
        s = FichaEtapaUpdateSerializer(
            ficha,
            data={'etapa': Ficha.Etapa.PRODUCTIVA},
            context={'request': request},
        )
        s.is_valid()
        s.save()
        historial = HistorialEtapa.objects.get(ficha=ficha)
        self.assertEqual(historial.cambiado_por, coord)

    def test_etapa_invalida(self):
        ficha = make_ficha()
        s = FichaEtapaUpdateSerializer(
            ficha, data={'etapa': 'INVALIDA'}
        )
        self.assertFalse(s.is_valid())


class FichaEstudianteSerializerTest(TestCase):

    def test_create_valido(self):
        ficha = make_ficha()
        estudiante = make_estudiante(email='est_cr@test.com')
        data = {
            'ficha': ficha.pk,
            'estudiante': estudiante.pk,
            'es_cadena': False,
        }
        s = FichaEstudianteCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        fe = s.save()
        self.assertEqual(fe.estudiante, estudiante)

    def test_segunda_ficha_no_cadena_invalida(self):
        estudiante = make_estudiante(email='est_doble@test.com')
        ficha1 = make_ficha()
        ficha2 = make_ficha()
        make_ficha_estudiante(ficha=ficha1, estudiante=estudiante, es_cadena=False)
        data = {
            'ficha': ficha2.pk,
            'estudiante': estudiante.pk,
            'es_cadena': False,
        }
        s = FichaEstudianteCreateSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_segunda_ficha_cadena_valida(self):
        estudiante = make_estudiante(email='est_cadena@test.com')
        ficha1 = make_ficha()
        ficha2 = make_ficha()
        make_ficha_estudiante(ficha=ficha1, estudiante=estudiante, es_cadena=True)
        data = {
            'ficha': ficha2.pk,
            'estudiante': estudiante.pk,
            'es_cadena': True,
        }
        s = FichaEstudianteCreateSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)

    def test_rol_incorrecto_invalido(self):
        ficha = make_ficha()
        docente = make_docente(email='doc_est@test.com')
        data = {
            'ficha': ficha.pk,
            'estudiante': docente.pk,
            'es_cadena': False,
        }
        s = FichaEstudianteCreateSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn('estudiante', s.errors)

    def test_update_desactivar_requiere_fecha_y_motivo(self):
        estudiante = make_estudiante(email='est_upd@test.com')
        fe = make_ficha_estudiante(estudiante=estudiante, activo=True)
        s = FichaEstudianteUpdateSerializer(
            fe, data={'activo': False}, partial=True
        )
        self.assertFalse(s.is_valid())

    def test_update_desactivar_valido(self):
        estudiante = make_estudiante(email='est_ok@test.com')
        fe = make_ficha_estudiante(estudiante=estudiante, activo=True)
        s = FichaEstudianteUpdateSerializer(
            fe,
            data={
                'activo': False,
                'fecha_retiro': '2024-06-01',
                'motivo_retiro': FichaEstudiante.MotivoRetiro.DESERCION,
            },
            partial=True,
        )
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        fe.refresh_from_db()
        self.assertFalse(fe.activo)
        self.assertEqual(
            fe.motivo_retiro, FichaEstudiante.MotivoRetiro.DESERCION
        )


class ReasignacionCreateSerializerTest(TestCase):

    def setUp(self):
        self.coord = make_coordinador(email='coord_reas@test.com')
        self.estudiante = make_estudiante(email='est_reas@test.com')
        self.ficha_origen = make_ficha()
        self.ficha_destino = make_ficha()
        self.fe_origen = make_ficha_estudiante(
            ficha=self.ficha_origen, estudiante=self.estudiante, activo=True
        )

    def _make_request(self):
        request = RequestFactory().post('/')
        request.user = self.coord
        return request

    def test_reasignacion_valida(self):
        data = {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Cambio de jornada',
        }
        s = ReasignacionCreateSerializer(
            data=data, context={'request': self._make_request()}
        )
        self.assertTrue(s.is_valid(), s.errors)
        reasignacion = s.save()
        self.assertIsNotNone(reasignacion.pk)

    def test_reasignacion_desactiva_origen(self):
        data = {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Cambio de jornada',
        }
        s = ReasignacionCreateSerializer(
            data=data, context={'request': self._make_request()}
        )
        s.is_valid()
        s.save()
        self.fe_origen.refresh_from_db()
        self.assertFalse(self.fe_origen.activo)
        self.assertEqual(
            self.fe_origen.motivo_retiro,
            FichaEstudiante.MotivoRetiro.REASIGNADO,
        )

    def test_reasignacion_crea_en_destino(self):
        from ficha.models.ficha_estudiante_model import FichaEstudiante
        data = {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Cambio de horario',
        }
        s = ReasignacionCreateSerializer(
            data=data, context={'request': self._make_request()}
        )
        s.is_valid()
        s.save()
        self.assertTrue(
            FichaEstudiante.objects.filter(
                ficha=self.ficha_destino,
                estudiante=self.estudiante,
                activo=True,
            ).exists()
        )

    def test_reasignacion_atomica_falla_limpia(self):
        """Si el destino ya tiene al estudiante activo, nada cambia."""
        make_ficha_estudiante(
            ficha=self.ficha_destino,
            estudiante=self.estudiante,
            activo=True,
        )
        data = {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'Intento duplicado',
        }
        s = ReasignacionCreateSerializer(
            data=data, context={'request': self._make_request()}
        )
        self.assertFalse(s.is_valid())
        self.fe_origen.refresh_from_db()
        self.assertTrue(self.fe_origen.activo)

    def test_origen_igual_destino_invalido(self):
        data = {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_origen.pk,
            'motivo': 'Misma ficha',
        }
        s = ReasignacionCreateSerializer(
            data=data, context={'request': self._make_request()}
        )
        self.assertFalse(s.is_valid())

    def test_estudiante_no_activo_en_origen_invalido(self):
        self.fe_origen.activo = False
        self.fe_origen.fecha_retiro = date(2024, 6, 1)
        self.fe_origen.motivo_retiro = FichaEstudiante.MotivoRetiro.DESERCION
        self.fe_origen.save()
        data = {
            'estudiante': self.estudiante.pk,
            'ficha_origen': self.ficha_origen.pk,
            'ficha_destino': self.ficha_destino.pk,
            'motivo': 'No está activo',
        }
        s = ReasignacionCreateSerializer(
            data=data, context={'request': self._make_request()}
        )
        self.assertFalse(s.is_valid())