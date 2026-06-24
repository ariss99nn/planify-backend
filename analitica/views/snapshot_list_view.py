# analitica/views/snapshot_list_view.py
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analitica.models.analitica_snapshot_model import AnaliticaSnapshot
from analitica.models.snapshot_programa_model import SnapshotPrograma
from analitica.permissions.analitica_permissions import CanViewAnalitica
from analitica.serializers.snapshot_serializer import AnaliticaSnapshotSerializer


class SnapshotListView(APIView):
    """
    GET /api/analitica/snapshots/?limite=30&programa=<id>

    Historial paginado de snapshots — solo gestión.

    Parámetros:
      ?limite=<int>    Máximo de snapshots (1–100, default 30).
      ?programa=<int>  Filtra snapshots donde participa el programa y
                       devuelve solo el detalle de ese programa en cada
                       snapshot. Útil para graficar la evolución de un
                       programa en el tiempo. Sin este parámetro se
                       devuelve el breakdown completo de cada snapshot.
    """
    permission_classes = [IsAuthenticated, CanViewAnalitica]

    def get(self, request):
        # ── Validar `limite` ─────────────────────────────────────────────────
        try:
            limite = int(request.query_params.get('limite', 30))
        except ValueError:
            return Response(
                {'limite': 'Debe ser un entero positivo.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (1 <= limite <= 100):
            return Response(
                {'limite': 'Debe estar entre 1 y 100.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Validar `programa` ───────────────────────────────────────────────
        programa_id_raw = request.query_params.get('programa')
        programa_id = None
        if programa_id_raw is not None:
            try:
                programa_id = int(programa_id_raw)
            except ValueError:
                return Response(
                    {'programa': 'Debe ser un entero (pk del programa).'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ── Construir queryset ───────────────────────────────────────────────
        if programa_id:
            # Solo el SnapshotPrograma del programa solicitado en cada snapshot
            # → vista de evolución temporal de un programa concreto.
            prefetch_qs = (
                SnapshotPrograma.objects
                .select_related('programa')
                .filter(programa_id=programa_id)
            )
            qs = (
                AnaliticaSnapshot.objects
                .filter(programas__programa_id=programa_id)
                .prefetch_related(Prefetch('programas', queryset=prefetch_qs))
                .order_by('-fecha')
                .distinct()
            )
        else:
            # Todos los programas de cada snapshot → vista general de dashboard.
            prefetch_qs = SnapshotPrograma.objects.select_related('programa')
            qs = (
                AnaliticaSnapshot.objects
                .prefetch_related(Prefetch('programas', queryset=prefetch_qs))
                .order_by('-fecha')
            )

        snapshots = list(qs[:limite])
        return Response(AnaliticaSnapshotSerializer(snapshots, many=True).data)