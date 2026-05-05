def cantidad_items_carrito(request):
    """Context processor que agrega el conteo de items del carrito a todos los templates."""
    conteo = 0
    if request.user.is_authenticated:
        from .models import Carrito
        carrito = Carrito.objects.filter(usuario=request.user).first()
        if carrito:
            conteo = carrito.cantidad_items
    else:
        clave_sesion = request.session.session_key
        if clave_sesion:
            from .models import Carrito
            carrito = Carrito.objects.filter(clave_sesion=clave_sesion).first()
            if carrito:
                conteo = carrito.cantidad_items
    return {'cantidad_items_carrito': conteo}
