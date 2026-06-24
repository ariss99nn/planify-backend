# reportes/serializers/reporte_generado_serializer.py
from rest_framework import serializers
from reportes.models.reporte_generado_model import ReporteGenerado


class ReporteGeneradoListSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(
        source='get_tipo_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    usuario_nombre = serializers.CharField(
        source='usuario.nombre_completo', read_only=True
    )

    class Meta:
        model = ReporteGenerado
        fields = [
            'id', 'tipo', 'tipo_display',
            'estado', 'estado_display',
            'usuario', 'usuario_nombre',
            'filtros', 'tarea_id',
            'archivo_pdf', 'archivo_excel',
            'error_mensaje',
            'created_at', 'updated_at',
        ]


class ReporteGeneradoCreateSerializer(serializers.Serializer):
    """
    Solicita la generación de un reporte.
    No crea el objeto directamente — lo hace la vista, antes de
    despachar la tarea Celery (ver SolicitarReporteView).
    """
    tipo = serializers.ChoiceField(choices=ReporteGenerado.TipoReporte.choices)
    filtros = serializers.DictField(required=False, default=dict)

    # Tipos que cualquier rol fuera de "gestión" (docente, estudiante,
    # o cualquier rol futuro) puede solicitar. Todo lo demás requiere
    # COORDINADOR/ADMINISTRATIVO.
    #
    # IMPORTANTE — corrección de seguridad: la versión anterior de
    # este validador solo restringía explícitamente al rol DOCENTE
    # ("if request.user.rol == User.Rol.DOCENTE: ..."), y para
    # cualquier otro rol (p. ej. ESTUDIANTE) caía en un "else: return
    # value" que NO aplicaba ninguna restricción. Eso permitía que un
    # estudiante autenticado solicitara reportes de DOCENTES, AULAS,
    # ANALITICA o NOVEDADES sin restricción, porque SolicitarReporteView
    # solo exige IsAuthenticated y delega el control de tipo aquí.
    # Se reemplaza el bloqueo selectivo por una lista de permitidos:
    # todo rol que no esté en ROLES_GESTION queda restringido por
    # defecto, sin importar cuál sea.
    TIPOS_PERMITIDOS_NO_GESTION = {
        ReporteGenerado.TipoReporte.FICHAS,
        ReporteGenerado.TipoReporte.HORARIOS,
    }

    def validate_tipo(self, value):
        from reportes.permissions.reportes_permissions import ROLES_GESTION

        request = self.context.get('request')
        if not request:
            return value

        if request.user.rol in ROLES_GESTION:
            return value

        if value not in self.TIPOS_PERMITIDOS_NO_GESTION:
            raise serializers.ValidationError(
                'No tienes permiso para solicitar este tipo de reporte.'
            )
        return value