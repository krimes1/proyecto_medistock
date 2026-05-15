"""Vistas de envíos y tracking de pedidos."""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Envio, EventoSeguimiento


def tracking_publico(request):
    """Vista pública para consultar estado de un envío por número de seguimiento o número de pedido."""
    numero = request.GET.get('numero', '').strip()
    envio = None
    pedido = None
    eventos = []

    if numero:
        # Primero buscar por número de seguimiento en Envio
        try:
            envio = Envio.objects.select_related('pedido__usuario').get(
                numero_seguimiento__iexact=numero
            )
            pedido = envio.pedido
            eventos = envio.eventos.all().order_by('-fecha_hora')
        except Envio.DoesNotExist:
            envio = None

        # Si no se encontró envío, buscar por número de pedido
        if not envio:
            from pedidos.models import Pedido
            try:
                pedido = Pedido.objects.get(numero_pedido__iexact=numero)
                # Intentar obtener el envío asociado al pedido
                try:
                    envio = pedido.envio
                    eventos = envio.eventos.all().order_by('-fecha_hora')
                except Envio.DoesNotExist:
                    envio = None
            except Pedido.DoesNotExist:
                pedido = None

    contexto = {
        'numero': numero,
        'envio': envio,
        'pedido': pedido,
        'eventos': eventos,
    }
    return render(request, 'envios/tracking.html', contexto)


@login_required
def mi_envio(request, pedido_id):
    """Vista del envío asociado a un pedido del usuario."""
    from pedidos.models import Pedido
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)

    try:
        envio = pedido.envio
        eventos = envio.eventos.all().order_by('-fecha_hora')
    except Envio.DoesNotExist:
        envio = None
        eventos = []

    contexto = {
        'pedido': pedido,
        'envio': envio,
        'eventos': eventos,
    }
    return render(request, 'envios/mi_envio.html', contexto)
