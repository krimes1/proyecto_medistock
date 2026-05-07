"""Vistas de la API REST de MediStock.

Endpoints disponibles:
  GET /api/v1/productos/                   — Lista de productos con stock
  GET /api/v1/productos/{codigo_producto}/ — Detalle con stock por bodega
  GET /api/v1/categorias/                  — Lista de categorías
"""
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from productos.models import Producto, Categoria
from .serializers import (
    ProductoListSerializer, ProductoDetalleSerializer, CategoriaSerializer,
)


class ProductoListAPI(generics.ListAPIView):
    """Lista de productos activos con stock actualizado en tiempo real.

    Permite búsqueda por nombre/SKU y filtro por categoría.
    Pensado para que ERPs de clínicas consuman información automáticamente.
    """
    queryset = Producto.objects.filter(activo=True).select_related('categoria', 'marca')
    serializer_class = ProductoListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'sku', 'descripcion']
    ordering_fields = ['precio', 'nombre', 'creado_en']
    ordering = ['nombre']


class ProductoDetalleAPI(generics.RetrieveAPIView):
    """Detalle de un producto específico con stock por bodega en tiempo real.

    Endpoint principal: GET /api/v1/productos/{codigo_producto}/
    Donde {codigo_producto} es el SKU del producto (ej: MS-D001).
    """
    queryset = Producto.objects.filter(activo=True).select_related(
        'categoria', 'marca'
    ).prefetch_related('items_stock__bodega')
    serializer_class = ProductoDetalleSerializer
    permission_classes = [AllowAny]
    lookup_field = 'sku'
    lookup_url_kwarg = 'codigo_producto'


class CategoriaListAPI(generics.ListAPIView):
    """Lista de categorías activas."""
    queryset = Categoria.objects.filter(activa=True)
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
