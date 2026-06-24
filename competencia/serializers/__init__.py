from competencia.serializers.asignatura.asignatura_create_serializer import AsignaturaCreateSerializer
from competencia.serializers.asignatura.asignatura_detail_serializer import AsignaturaDetailSerializer
from competencia.serializers.asignatura.asignatura_list_serializer import AsignaturaListSerializer
from competencia.serializers.asignatura.asignatura_update_serializer import AsignaturaUpdateSerializer

from competencia.serializers.competencia.competencia_create_serializer import CompetenciaCreateSerializer
from competencia.serializers.competencia.competencia_detail_serializer import CompetenciaDetailSerializer
from competencia.serializers.competencia.competencia_list_serializer import CompetenciaListSerializer
from competencia.serializers.competencia.competencia_update_serializer import CompetenciaUpdateSerializer
from competencia.serializers.competencia.competencia_transversal_create_serializer import CompetenciaTransversalCreateSerializer
from competencia.serializers.competencia.competencia_transversal_update_serializer import CompetenciaTransversalUpdateSerializer

from competencia.serializers.resultado_aprendizaje.rap_create_serializer import RAPCreateSerializer
from competencia.serializers.resultado_aprendizaje.rap_detail_serializer import RAPDetailSerializer
from competencia.serializers.resultado_aprendizaje.rap_list_serializer import RAPListSerializer
from competencia.serializers.resultado_aprendizaje.rap_update_serializer import RAPUpdateSerializer

__all__ = [
    'AsignaturaCreateSerializer',
    'AsignaturaDetailSerializer',
    'AsignaturaListSerializer',
    'AsignaturaUpdateSerializer',
    'CompetenciaCreateSerializer',
    'CompetenciaDetailSerializer',
    'CompetenciaListSerializer',
    'CompetenciaUpdateSerializer',
    'CompetenciaTransversalCreateSerializer',
    'CompetenciaTransversalUpdateSerializer',
    'RAPCreateSerializer',
    'RAPDetailSerializer',
    'RAPListSerializer',
    'RAPUpdateSerializer',
]