from django.contrib import admin
from .models import Categoria, Marca, Producto, ImagenProducto

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'padre', 'activa', 'orden')
    list_filter = ('activa', 'padre')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activa')
    list_filter = ('activa',)
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'marca', 'precio', 'tipo_producto', 'activo', 'destacado', 'stock_total')
    list_filter = ('tipo_producto', 'categoria', 'marca', 'activo', 'destacado')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre', 'sku', 'descripcion')
    inlines = [ImagenProductoInline]
    readonly_fields = ('creado_en', 'actualizado_en')
