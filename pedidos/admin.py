from django.contrib import admin
from .models import Pedido, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'usuario', 'estado', 'prioridad', 'tipo_despacho', 'total', 'creado_en')
    list_filter = ('estado', 'prioridad', 'tipo_despacho', 'bodega')
    search_fields = ('numero_pedido', 'usuario__username', 'usuario__email')
    inlines = [ItemPedidoInline]
    readonly_fields = ('creado_en', 'actualizado_en')
    date_hierarchy = 'creado_en'
