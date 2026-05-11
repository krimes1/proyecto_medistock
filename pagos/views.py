"""Vistas de pagos: integración simulada con WebPay Plus.

Flujo:
1. iniciar_pago → Crea transacción WebPay y redirige al formulario
2. formulario_webpay → Formulario simulado de pago (como Transbank)
3. retorno_webpay → Callback de WebPay, confirma transacción
4. pago_exitoso / pago_fallido → Resultados
5. ver_boleta → Muestra la boleta electrónica generada
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from pedidos.models import Pedido
from .models import Pago
from .services import WebPayPlusSimulado, generar_boleta
from pedidos.emails import enviar_boleta_compra


@login_required
def iniciar_pago(request, pedido_id):
    """Inicia el proceso de pago creando la transacción WebPay."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)

    # Verificar que no tenga pago ya
    if hasattr(pedido, 'pago') and pedido.pago.estado == 'completado':
        messages.info(request, 'Este pedido ya fue pagado.')
        return redirect('pedidos:confirmacion', pedido_id=pedido.pk)

    if request.method == 'POST':
        metodo = request.POST.get('metodo', 'webpay_credito')

        # Crear registro de pago
        pago, _ = Pago.objects.get_or_create(
            pedido=pedido,
            defaults={
                'metodo': metodo,
                'monto': pedido.total,
                'estado': 'procesando',
            }
        )
        if pago.estado == 'pendiente':
            pago.metodo = metodo
            pago.estado = 'procesando'
            pago.save()

        # Crear transacción en WebPay (simulado)
        resultado = WebPayPlusSimulado.crear_transaccion(
            numero_pedido=pedido.numero_pedido,
            monto=int(pedido.total),
            url_retorno=f'/pagos/webpay/retorno/',
        )

        # Guardar token
        pago.id_transaccion = resultado['token']
        pago.save()

        # Redirigir al formulario de WebPay
        return redirect(f"{resultado['url']}&pedido={pedido.pk}")

    contexto = {
        'pedido': pedido,
        'items': pedido.items.select_related('producto').all(),
    }
    return render(request, 'pagos/seleccion_metodo.html', contexto)


@login_required
def formulario_webpay(request):
    """Formulario simulado de WebPay Plus (simula la interfaz de Transbank)."""
    token = request.GET.get('token', '')
    pedido_id = request.GET.get('pedido', '')

    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)

    contexto = {
        'token': token,
        'pedido': pedido,
        'monto': int(pedido.total),
    }
    return render(request, 'pagos/formulario_webpay.html', contexto)


@login_required
def retorno_webpay(request):
    """Callback de WebPay: confirma la transacción y procesa el resultado."""
    token = request.POST.get('token', request.GET.get('token', ''))
    pedido_id = request.POST.get('pedido_id', request.GET.get('pedido_id', ''))

    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    pago = get_object_or_404(Pago, pedido=pedido)

    # Confirmar transacción (simulado)
    resultado = WebPayPlusSimulado.confirmar_transaccion(token)

    if resultado['response_code'] == 0:
        # Pago exitoso
        pago.estado = 'completado'
        pago.codigo_autorizacion = resultado['authorization_code']
        pago.ultimos_cuatro = resultado['card_detail']['card_number'][-4:]
        pago.completado_en = timezone.now()
        pago.save()

        # Registrar pago exitoso sin cambiar el estado del pedido,
        # para que el Ejecutivo lo apruebe manualmente.
        # pedido.estado = 'aprobado' 
        # pedido.aprobado_en = timezone.now()
        # pedido.save()

        # Generar boleta electrónica
        boleta = generar_boleta(pago)
        
        # Enviar correo al usuario con la boleta
        enviar_boleta_compra(pedido, pago, boleta)

        messages.success(request, '¡Pago procesado exitosamente!')
        return redirect('pagos:pago_exitoso', pedido_id=pedido.pk)
    else:
        # Pago fallido
        pago.estado = 'fallido'
        pago.save()

        messages.error(request, 'El pago no pudo ser procesado.')
        return redirect('pagos:pago_fallido', pedido_id=pedido.pk)


@login_required
def pago_exitoso(request, pedido_id):
    """Vista de confirmación de pago exitoso."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    pago = pedido.pago
    boleta = getattr(pago, 'boleta', None)

    contexto = {
        'pedido': pedido,
        'pago': pago,
        'boleta': boleta,
    }
    return render(request, 'pagos/pago_exitoso.html', contexto)


@login_required
def pago_fallido(request, pedido_id):
    """Vista de pago fallido con opción de reintentar."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    return render(request, 'pagos/pago_fallido.html', {'pedido': pedido})


@login_required
def ver_boleta(request, pedido_id):
    """Muestra la boleta electrónica del pedido."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    pago = get_object_or_404(Pago, pedido=pedido, estado='completado')
    boleta = get_object_or_404(pago.boleta.__class__, pago=pago)

    contexto = {
        'pedido': pedido,
        'pago': pago,
        'boleta': boleta,
        'items': pedido.items.select_related('producto').all(),
    }
    return render(request, 'pagos/boleta.html', contexto)
