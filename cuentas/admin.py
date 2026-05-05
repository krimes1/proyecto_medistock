from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'usuario'

class UsuarioAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'obtener_rol', 'is_active')
    list_filter = BaseUserAdmin.list_filter + ('perfil__rol',)

    def obtener_rol(self, obj):
        return obj.perfil.get_rol_display() if hasattr(obj, 'perfil') else '-'
    obtener_rol.short_description = 'Rol'

admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
