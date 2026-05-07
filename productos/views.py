"""Vistas de productos: catálogo, detalle y filtro por categoría."""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto, Categoria


def lista_productos(request):
    """Catálogo de productos con búsqueda y filtros."""
    productos = Producto.objects.filter(activo=True).select_related('categoria', 'marca')
    categorias = Categoria.objects.filter(activa=True, padre__isnull=True).order_by('orden')

    # Filtro por categoría
    categoria_slug = request.GET.get('categoria')
    categoria_actual = None
    if categoria_slug:
        categoria_actual = get_object_or_404(Categoria, slug=categoria_slug)
        productos = productos.filter(categoria=categoria_actual)

    # Filtro por tipo
    tipo = request.GET.get('tipo')
    if tipo:
        productos = productos.filter(tipo_producto=tipo)

    # Búsqueda
    query = request.GET.get('q', '').strip()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(sku__icontains=query) | Q(descripcion__icontains=query)
        )

    # Ordenamiento
    orden = request.GET.get('orden', 'nombre')
    opciones_orden = {
        'nombre': 'nombre',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'reciente': '-creado_en',
    }
    productos = productos.order_by(opciones_orden.get(orden, 'nombre'))

    contexto = {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria_actual,
        'query': query,
        'orden_actual': orden,
        'tipo_actual': tipo,
    }
    return render(request, 'productos/lista.html', contexto)


def detalle_producto(request, slug):
    """Detalle completo de un producto con información de stock."""
    producto = get_object_or_404(
        Producto.objects.select_related('categoria', 'marca'),
        slug=slug, activo=True
    )
    stock_items = producto.items_stock.select_related('bodega').filter(cantidad__gt=0)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria, activo=True
    ).exclude(pk=producto.pk)[:4]

    contexto = {
        'producto': producto,
        'stock_items': stock_items,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'productos/detalle.html', contexto)


def detalle_categoria(request, slug):
    """Productos filtrados por categoría."""
    categoria = get_object_or_404(Categoria, slug=slug, activa=True)
    productos = Producto.objects.filter(
        categoria=categoria, activo=True
    ).select_related('marca')

    contexto = {
        'categoria': categoria,
        'productos': productos,
    }
    return render(request, 'productos/categoria.html', contexto)
