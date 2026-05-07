"""Serializers para la API REST de MediStock."""
from rest_framework import serializers
from productos.models import Producto, Categoria, Marca
from inventario.models import ItemStock, Bodega


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion']


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ['id', 'nombre', 'slug']


class StockBodegaSerializer(serializers.ModelSerializer):
    bodega_nombre = serializers.CharField(source='bodega.nombre', read_only=True)
    bodega_codigo = serializers.CharField(source='bodega.codigo', read_only=True)
    bodega_ciudad = serializers.CharField(source='bodega.ciudad', read_only=True)

    class Meta:
        model = ItemStock
        fields = [
            'bodega_codigo', 'bodega_nombre', 'bodega_ciudad',
            'numero_lote', 'fecha_vencimiento', 'cantidad',
            'stock_bajo', 'esta_vencido',
        ]


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer reducido para listados."""
    categoria = serializers.CharField(source='categoria.nombre', read_only=True)
    marca = serializers.CharField(source='marca.nombre', read_only=True, default=None)
    stock_total = serializers.IntegerField(read_only=True)
    en_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'sku', 'nombre', 'slug', 'descripcion_corta',
            'tipo_producto', 'categoria', 'marca', 'precio',
            'stock_total', 'en_stock', 'activo',
        ]


class ProductoDetalleSerializer(serializers.ModelSerializer):
    """Serializer completo con información de stock por bodega."""
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    stock_total = serializers.IntegerField(read_only=True)
    en_stock = serializers.BooleanField(read_only=True)
    stock_por_bodega = StockBodegaSerializer(
        source='items_stock', many=True, read_only=True
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'sku', 'nombre', 'slug', 'descripcion', 'descripcion_corta',
            'tipo_producto', 'categoria', 'marca', 'precio',
            'requiere_receta', 'stock_total', 'en_stock',
            'stock_por_bodega', 'creado_en', 'actualizado_en',
        ]
