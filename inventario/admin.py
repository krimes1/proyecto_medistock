from django.contrib import admin
from .models import Bodega, ItemStock

@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'ciudad', 'region', 'activa')
    list_filter = ('region', 'activa')
    search_fields = ('nombre', 'codigo', 'ciudad')

@admin.register(ItemStock)
class ItemStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'bodega', 'numero_lote', 'cantidad', 'stock_minimo', 'fecha_vencimiento', 'stock_bajo', 'esta_vencido')
    list_filter = ('bodega', 'producto__categoria', 'fecha_vencimiento')
    search_fields = ('producto__nombre', 'numero_lote')
    readonly_fields = ('creado_en', 'actualizado_en')

    def stock_bajo(self, obj):
        return obj.stock_bajo
    stock_bajo.boolean = True
    stock_bajo.short_description = 'Stock Bajo'

    def esta_vencido(self, obj):
        return obj.esta_vencido
    esta_vencido.boolean = True
    esta_vencido.short_description = 'Vencido'
