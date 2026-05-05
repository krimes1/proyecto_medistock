from django.contrib import admin
from .models import Pago, Boleta

class BoletaInline(admin.StackedInline):
    model = Boleta
    extra = 0

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'metodo', 'estado', 'monto', 'id_transaccion', 'creado_en')
    list_filter = ('estado', 'metodo')
    search_fields = ('id_transaccion', 'pedido__numero_pedido')
    inlines = [BoletaInline]
    readonly_fields = ('creado_en',)

@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    list_display = ('numero_boleta', 'pago', 'monto_total', 'emitida_en')
    search_fields = ('numero_boleta',)
    readonly_fields = ('emitida_en',)
