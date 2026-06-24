# bhorario/views/bloque_horario_disponibilidad_view.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bhorario.services.bloque_service import BloqueHorarioService
from docentes.models.docente_model import Docente
from aulas.models.aula_model import Aula
from ficha.models.ficha_model import Ficha


class DisponibilidadView(APIView):
    """
    POST /api/horarios/disponibilidad/
    Verifica si docente, aula y ficha están disponibles en un intervalo.
    No crea nada — solo consulta.
    """
    permission_classes = [IsAuthenticated]

    # FIX B1: helper que valida y convierte un campo FK a int de forma segura
    @staticmethod
    def _parse_pk(data: dict, campo: str):
        """
        Retorna (int_value, None) si válido,
        o (None, Response_error) si inválido.
        """
        raw = data.get(campo)
        if raw is None:
            return None, None
        try:
            value = int(raw)
            if value <= 0:
                raise ValueError
            return value, None
        except (ValueError, TypeError):
            return None, Response(
                {'detail': f'"{campo}" debe ser un entero positivo.'},
                status=400,
            )

    def post(self, request):
        data = request.data

        # Campos obligatorios
        try:
            hora_inicio = data['hora_inicio']
            hora_fin    = data['hora_fin']
            dia         = data['dia_semana']
        except KeyError as e:
            return Response({'detail': f'Campo requerido: {e}'}, status=400)

        # Validar y parsear FKs — FIX B1
        docente_pk, err = self._parse_pk(data, 'docente')
        if err:
            return err
        aula_pk, err = self._parse_pk(data, 'aula')
        if err:
            return err
        ficha_pk, err = self._parse_pk(data, 'ficha')
        if err:
            return err
        excluir_pk, err = self._parse_pk(data, 'excluir_pk')
        if err:
            return err

        # Resolver instancias
        docente = Docente.objects.filter(pk=docente_pk).first() if docente_pk else None
        aula    = Aula.objects.filter(pk=aula_pk).first()       if aula_pk    else None
        ficha   = Ficha.objects.filter(pk=ficha_pk).first()     if ficha_pk   else None

        resultado = BloqueHorarioService.verificar_disponibilidad(
            dia=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            docente=docente,
            aula=aula,
            ficha=ficha,
            excluir_pk=excluir_pk,
        )

        # 'disponible' ya viene calculado en el service
        return Response(resultado)