"""Vistas del carrito de compras."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from productos.models import Producto
from .models import Carrito, ItemCarrito


def _obtener_carrito(request):
    """Obtiene o crea el carrito del usuario actual."""
    if request.user.is_authenticated:
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
        return carrito
    else:
        if not request.session.session_key:
            request.session.create()
        clave = request.session.session_key
        carrito, _ = Carrito.objects.get_or_create(clave_sesion=clave)
        return carrito


def detalle_carrito(request):
    """Muestra el contenido del carrito."""
    carrito = _obtener_carrito(request)
    items = carrito.items.select_related('producto__categoria').all()
    contexto = {
        'carrito': carrito,
        'items': items,
    }
    return render(request, 'carrito/detalle.html', contexto)


@require_POST
def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito."""
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    carrito = _obtener_carrito(request)
    cantidad = int(request.POST.get('cantidad', 1))

    if not producto.en_stock:
        messages.error(request, f'{producto.nombre} no tiene stock disponible.')
        return redirect('productos:detalle_producto', slug=producto.slug)

    item, creado = ItemCarrito.objects.get_or_create(
        carrito=carrito, producto=producto,
        defaults={'cantidad': cantidad}
    )
    if not creado:
        item.cantidad += cantidad
        item.save()

    messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('carrito:detalle_carrito')


@require_POST
def actualizar_item(request, item_id):
    """Actualiza la cantidad de un item del carrito."""
    carrito = _obtener_carrito(request)
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=carrito)
    cantidad = int(request.POST.get('cantidad', 1))

    if cantidad > 0:
        item.cantidad = cantidad
        item.save()
        messages.success(request, 'Cantidad actualizada.')
    else:
        item.delete()
        messages.success(request, 'Producto eliminado del carrito.')

    return redirect('carrito:detalle_carrito')


@require_POST
def eliminar_item(request, item_id):
    """Elimina un item del carrito."""
    carrito = _obtener_carrito(request)
    item = get_object_or_404(ItemCarrito, pk=item_id, carrito=carrito)
    nombre = item.producto.nombre
    item.delete()
    messages.success(request, f'{nombre} eliminado del carrito.')
    return redirect('carrito:detalle_carrito')
