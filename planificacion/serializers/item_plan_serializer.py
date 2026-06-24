# planificacion/serializers/item_plan_serializer.py
from rest_framework import serializers

from planificacion.models.item_plan_model import ItemPlan


class ItemPlanListSerializer(serializers.ModelSerializer):

    competencia_codigo = serializers.CharField(
        source='competencia.codigo', read_only=True
    )
    competencia_nombre = serializers.CharField(
        source='competencia.nombre', read_only=True
    )
    competencia_tipo = serializers.CharField(
        source='competencia.tipo', read_only=True
    )
    docente_nombre = serializers.CharField(
        source='docente.user.nombre', read_only=True, default=None
    )
    # Normalizado a DecimalField para coincidir con el tipo del property
    horas_ejecutadas = serializers.DecimalField(
        max_digits=5, decimal_places=1, read_only=True
    )
    horas_restantes = serializers.DecimalField(
        max_digits=5, decimal_places=1, read_only=True
    )
    porcentaje_avance = serializers.FloatField(read_only=True)

    class Meta:
        model  = ItemPlan
        fields = [
            'id', 'plan',
            'competencia', 'competencia_codigo', 'competencia_nombre', 'competencia_tipo',
            'docente', 'docente_nombre',
            'horas_asignadas', 'horas_ejecutadas', 'horas_restantes', 'porcentaje_avance',
            'orden', 'completado',
        ]


class ItemPlanCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ItemPlan
        fields = ['plan', 'competencia', 'docente', 'horas_asignadas', 'orden']

    def validate(self, data):
        plan        = data.get('plan')
        competencia = data.get('competencia')

        # 1. No agregar ítems a planes ya aprobados
        if plan and plan.estado == plan.EstadoPlan.APROBADO:
            raise serializers.ValidationError(
                'No se pueden agregar ítems a un plan ya aprobado.'
            )

        # 2. Unicidad (plan, competencia)
        if ItemPlan.objects.filter(plan=plan, competencia=competencia).exists():
            raise serializers.ValidationError(
                'Esta competencia ya está en el plan.'
            )

        # 3. Horas no superan el tope de la asignatura
        if competencia and competencia.asignatura_id:
            horas_max = competencia.asignatura.total_horas
            if data.get('horas_asignadas', 0) > horas_max:
                raise serializers.ValidationError({
                    'horas_asignadas': (
                        f'No puede superar {horas_max} horas de la asignatura.'
                    )
                })

        return data


class ItemPlanUpdateSerializer(serializers.ModelSerializer):
    """No permite cambiar plan ni competencia."""

    class Meta:
        model  = ItemPlan
        fields = ['docente', 'horas_asignadas', 'orden', 'completado']

    def validate(self, data):
        if (
            self.instance
            and self.instance.plan.estado == self.instance.plan.EstadoPlan.APROBADO
        ):
            raise serializers.ValidationError(
                'No se puede editar un ítem de un plan aprobado.'
            )
        return data