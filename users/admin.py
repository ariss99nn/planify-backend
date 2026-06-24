from django.contrib import admin
from users.models.user import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombre', 'apellido', 'rol', 'email_verificado', 'is_active', 'fecha_creacion')
    list_filter = ('rol', 'email_verificado', 'is_active', 'fecha_creacion')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'email', 'imagen')
        }),
        ('Rol y Permisos', {
            'fields': ('rol',)
        }),
        ('Estado', {
            'fields': ('is_active', 'email_verificado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
        ('Seguridad', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    def get_readonly_fields(self, request, obj=None):
        """La contraseña es read-only para que se use change_password"""
        return self.readonly_fields + ('password',)
