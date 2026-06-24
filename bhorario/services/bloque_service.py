# bhorario/services/bloque_service.py
import logging
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from bhorario.models.bloque_horario_model import BloqueHorario

logger = logging.getLogger(__name__)


class ColisionError(Exception):
    """Error semántico de colisión de horario."""
    pass


class BloqueHorarioService:

    @staticmethod
    @transaction.atomic
    def crear_bloque(datos: dict) -> BloqueHorario:
        """
        Creación atómica con tres capas de protección:
        1. select_for_update() — lock real sobre filas candidatas a conflicto
        2. clean() del modelo   — validación de negocio bajo el lock
        3. EXCLUDE constraint   — garantía absoluta en PostgreSQL
        """
        dia      = datos.get('dia_semana')
        h_inicio = datos.get('hora_inicio')
        h_fin    = datos.get('hora_fin')
        docente  = datos.get('docente')
        aula     = datos.get('aula')
        ficha    = datos.get('ficha')

        # Capa 1 — lock preventivo
        _lock_qs = BloqueHorario.objects.select_for_update().filter(
            dia_semana=dia,
            hora_inicio__lt=h_fin,
            hora_fin__gt=h_inicio,
        )
        filtro_recursos = Q()
        if docente:
            filtro_recursos |= Q(docente=docente)
        if aula:
            filtro_recursos |= Q(aula=aula)
        if ficha:
            filtro_recursos |= Q(ficha=ficha)
        if filtro_recursos:
            list(_lock_qs.filter(filtro_recursos).values_list('pk', flat=True))

        # Capa 2 — validación de negocio
        bloque = BloqueHorario(**datos)
        try:
            bloque.full_clean()
        except ValidationError as e:
            raise ColisionError(str(e)) from e

        bloque.save(skip_clean=True)
        logger.info(
            "Bloque creado: %s — Docente: %s | Aula: %s | Ficha: %s",
            bloque, docente, aula, ficha,
        )
        return bloque

    @staticmethod
    @transaction.atomic
    def actualizar_bloque(bloque: BloqueHorario, datos: dict) -> BloqueHorario:
        """Actualización atómica con lock preventivo y validación de negocio."""
        dia      = datos.get('dia_semana',  bloque.dia_semana)
        h_inicio = datos.get('hora_inicio', bloque.hora_inicio)
        h_fin    = datos.get('hora_fin',    bloque.hora_fin)
        docente  = datos.get('docente',     bloque.docente)
        aula     = datos.get('aula',        bloque.aula)
        ficha    = datos.get('ficha',       bloque.ficha)

        _lock_qs = BloqueHorario.objects.select_for_update().filter(
            dia_semana=dia,
            hora_inicio__lt=h_fin,
            hora_fin__gt=h_inicio,
        ).exclude(pk=bloque.pk)

        filtro_recursos = Q()
        if docente:
            filtro_recursos |= Q(docente=docente)
        if aula:
            filtro_recursos |= Q(aula=aula)
        if ficha:
            filtro_recursos |= Q(ficha=ficha)
        if filtro_recursos:
            list(_lock_qs.filter(filtro_recursos).values_list('pk', flat=True))

        for campo, valor in datos.items():
            setattr(bloque, campo, valor)

        try:
            bloque.full_clean()
        except ValidationError as e:
            raise ColisionError(str(e)) from e

        bloque.save(skip_clean=True)
        logger.info("Bloque actualizado: %s", bloque)
        return bloque

    @staticmethod
    def verificar_disponibilidad(
        dia: str,
        hora_inicio,
        hora_fin,
        docente=None,
        aula=None,
        ficha=None,
        excluir_pk=None,
        fecha_referencia=None,  # NUEVO: para filtrar restricciones temporales
    ) -> dict:
        """
        Verifica disponibilidad sin crear nada.

        CORRECCIONES aplicadas:
        - Bug #1: ahora consulta el modelo Disponibilidad para respetar
          las restricciones horarias declaradas por el docente.
        - Bug #6: las restricciones TEMPORALES se filtran por fecha_referencia,
          evitando que una restricción fuera de rango bloquee slots válidos.
        """
        from django.db.models import Q
        from django.utils import timezone

        qs = BloqueHorario.objects.filter(
            dia_semana=dia,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        )
        if excluir_pk:
            qs = qs.exclude(pk=excluir_pk)

        resultado = {
            'docente_disponible': True,
            'aula_disponible':    True,
            'ficha_disponible':   True,
            'conflictos':         [],
        }

        if docente:
            # Check 1: bloque ya existente en BD
            if qs.filter(docente=docente).exists():
                resultado['docente_disponible'] = False
                resultado['conflictos'].append(
                    f'Docente {docente} ya tiene un bloque el {dia} {hora_inicio}-{hora_fin}'
                )

            # Check 2: restricción de Disponibilidad declarada — Bug #1 + #6 RESUELTOS
            if resultado['docente_disponible']:
                from docentes.models.docente_disponibilidad_model import Disponibilidad
                hoy = fecha_referencia or timezone.now().date()

                restringido = Disponibilidad.objects.filter(
                    docente=docente,
                    dia_semana=dia,
                    hora_inicio__lt=hora_fin,
                    hora_fin__gt=hora_inicio,
                    disponible=False,
                ).filter(
                    # Bug #6: respetar el rango de fechas de restricciones TEMPORALES
                    Q(tipo_restriccion='PERMANENTE') |
                    Q(
                        tipo_restriccion='TEMPORAL',
                        fecha_inicio_restriccion__lte=hoy,
                        fecha_fin_restriccion__gte=hoy,
                    )
                ).exists()

                if restringido:
                    resultado['docente_disponible'] = False
                    resultado['conflictos'].append(
                        f'Docente {docente} tiene restricción de disponibilidad '
                        f'el {dia} {hora_inicio}-{hora_fin}'
                    )

        if aula and qs.filter(aula=aula).exists():
            resultado['aula_disponible'] = False
            resultado['conflictos'].append(
                f'Aula {aula} no disponible el {dia} {hora_inicio}-{hora_fin}'
            )

        if ficha and qs.filter(ficha=ficha).exists():
            resultado['ficha_disponible'] = False
            resultado['conflictos'].append(
                f'Ficha {ficha} no disponible el {dia} {hora_inicio}-{hora_fin}'
            )

        resultado['disponible'] = all([
            resultado['docente_disponible'],
            resultado['aula_disponible'],
            resultado['ficha_disponible'],
        ])

        return resultado