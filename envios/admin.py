from django.contrib import admin
from .models import Envio, EventoSeguimiento

class EventoSeguimientoInline(admin.TabularInline):
    model = EventoSeguimiento
    extra = 0
    ordering = ('-fecha_hora',)

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = ('numero_seguimiento', 'pedido', 'transportista', 'estado', 'entrega_estimada', 'despachado_en')
    list_filter = ('estado', 'transportista')
    search_fields = ('numero_seguimiento', 'pedido__numero_pedido')
    inlines = [EventoSeguimientoInline]
