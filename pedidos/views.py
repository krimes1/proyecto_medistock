"""Vistas de pedidos: checkout, detalle de pedido, confirmación."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from django.http import JsonResponse
from .models import Pedido, ItemPedido
from cuentas.models import PerfilUsuario
from carrito.views import _obtener_carrito
from inventario.models import Bodega


@login_required
def checkout(request):
    """Proceso de checkout: selección de despacho y dirección."""
    carrito = _obtener_carrito(request)
    items = carrito.items.select_related('producto').all()

    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('productos:lista_productos')

    bodegas = Bodega.objects.filter(activa=True)

    if request.method == 'POST':
        tipo_despacho = request.POST.get('tipo_despacho', 'normal')
        prioridad = request.POST.get('prioridad', 'normal')
        direccion = request.POST.get('direccion', '')
        ciudad = request.POST.get('ciudad', '')
        region = request.POST.get('region', '')
        bodega_id = request.POST.get('bodega', '')
        notas = request.POST.get('notas', '')

        if not direccion or not ciudad or not region:
            messages.error(request, 'Completa todos los campos de envío.')
            return redirect('pedidos:checkout')

        codigo_vendedor_input = request.POST.get('codigo_vendedor', '').strip()
        vendedor_asignado = None
        descuento = Decimal('0')

        if codigo_vendedor_input:
            from cuentas.models import PerfilUsuario
            perfil_vendedor = PerfilUsuario.objects.filter(codigo_vendedor=codigo_vendedor_input, rol='vendedor').first()
            if perfil_vendedor:
                vendedor_asignado = perfil_vendedor.usuario
                # Aplicar 5% de descuento
                descuento = (carrito.total * Decimal('0.05')).quantize(Decimal('1'))

        # Calcular totales
        subtotal = carrito.total
        subtotal_con_descuento = subtotal - descuento
        costo_envio = Decimal('5990') if tipo_despacho == 'express' else Decimal('2990')
        impuesto = (subtotal_con_descuento * Decimal('0.19')).quantize(Decimal('1'))
        total = subtotal_con_descuento + costo_envio + impuesto

        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            tipo_despacho=tipo_despacho,
            prioridad=prioridad,
            direccion_envio=direccion,
            ciudad_envio=ciudad,
            region_envio=region,
            bodega_id=bodega_id if bodega_id else None,
            subtotal=subtotal,
            descuento=descuento,
            costo_envio=costo_envio,
            impuesto=impuesto,
            total=total,
            vendedor=vendedor_asignado,
            notas=notas,
        )

        # Si usó un código, lo quitamos de la sesión para futuras compras
        if vendedor_asignado and 'vendedor_ref' in request.session:
            del request.session['vendedor_ref']

        # Crear items del pedido
        for item in items:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio,
            )

        # Limpiar carrito
        items.delete()

        # Redirigir a pago
        return redirect('pagos:iniciar_pago', pedido_id=pedido.pk)

    from cuentas.forms import REGIONES_CHILE, CIUDADES_CHILE
    codigo_sesion = request.session.get('vendedor_ref', '')
    contexto = {
        'carrito': carrito,
        'items': items,
        'bodegas': bodegas,
        'regiones': REGIONES_CHILE,
        'ciudades': CIUDADES_CHILE,
        'codigo_vendedor_sesion': codigo_sesion,
    }
    return render(request, 'pedidos/checkout.html', contexto)


@login_required
def detalle_pedido(request, pedido_id):
    """Detalle de un pedido específico."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    items = pedido.items.select_related('producto').all()

    contexto = {
        'pedido': pedido,
        'items': items,
    }
    return render(request, 'pedidos/detalle.html', contexto)


@login_required
def confirmacion_pedido(request, pedido_id):
    """Página de confirmación tras pago exitoso."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    return render(request, 'pedidos/confirmacion.html', {'pedido': pedido})


@login_required
def validar_codigo_vendedor(request):
    """API para validar el código de vendedor por AJAX."""
    codigo = request.GET.get('codigo', '').strip()
    if not codigo:
        return JsonResponse({'valido': False, 'mensaje': 'No se ingresó código'})

    perfil = PerfilUsuario.objects.filter(codigo_vendedor=codigo, rol='vendedor').first()
    if perfil:
        return JsonResponse({
            'valido': True,
            'mensaje': '¡5% de descuento por vendedor aplicado exitosamente!',
            'vendedor': perfil.usuario.get_full_name() or perfil.usuario.username
        })
    return JsonResponse({'valido': False, 'mensaje': 'Código de vendedor incorrecto o no existe'})
