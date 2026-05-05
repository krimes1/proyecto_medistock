from django.shortcuts import render
from productos.models import Producto, Categoria


def inicio(request):
    """Pagina principal de MediStock."""
    productos_destacados = Producto.objects.filter(
        activo=True, destacado=True
    ).select_related('categoria', 'marca')[:8]

    categorias = Categoria.objects.filter(
        activa=True, padre__isnull=True
    ).order_by('orden')[:6]

    contexto = {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
    }
    return render(request, 'core/home.html', contexto)


def nosotros(request):
    return render(request, 'core/nosotros.html')


def contacto(request):
    return render(request, 'core/contacto.html')
