from django.contrib import admin
from .models import AlianzaClinica


@admin.register(AlianzaClinica)
class AlianzaClinicaAdmin(admin.ModelAdmin):
    list_display = ('nombre_clinica', 'tipo_alianza', 'estado', 'descuento_acordado', 'creada_en')
    list_filter = ('estado', 'tipo_alianza')
    search_fields = ('nombre_clinica', 'contacto_nombre', 'contacto_email')
