"""Vistas de dashboards segmentados por rol.

- Ejecutivo de Cuentas: stock multi-bodega, aprobar compras
- Operador Logístico: órdenes por urgencia, despachar
- Analista de Finanzas: confirmar pagos, auditar
- Administrador: reportes de venta, alianzas
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from cuentas.decorators import rol_requerido
from pedidos.models import Pedido
from pedidos.emails import enviar_boleta_compra
from pagos.models import Pago
from pagos.services import generar_boleta
from productos.models import Producto
from inventario.models import ItemStock, Bodega
from envios.models import Envio
from envios.services import TrackingAPISimulado


# ============================================================
# EJECUTIVO DE CUENTAS
# ============================================================
@rol_requerido('ejecutivo', 'administrador')
def dashboard_ejecutivo(request):
    """Dashboard del Ejecutivo: stock multi-bodega y pedidos pendientes."""
    bodegas = Bodega.objects.filter(activa=True).annotate(
        total_items=Sum('items_stock__cantidad'),
        productos_bajo_stock=Count(
            'items_stock',
            filter=Q(items_stock__cantidad__lte=10, items_stock__cantidad__gt=0)
        ),
    )
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').select_related('usuario').order_by('-creado_en')
    total_pendientes = pedidos_pendientes.count()

    contexto = {
        'bodegas': bodegas,
        'pedidos_pendientes': pedidos_pendientes[:10],
        'total_pendientes': total_pendientes,
    }
    return render(request, 'dashboards/ejecutivo.html', contexto)


@rol_requerido('ejecutivo', 'administrador')
def stock_bodega(request, bodega_id):
    """Detalle de stock de una bodega específica."""
    bodega = get_object_or_404(Bodega, pk=bodega_id)
    items = ItemStock.objects.filter(bodega=bodega).select_related('producto__categoria').order_by('producto__nombre')

    contexto = {
        'bodega': bodega,
        'items': items,
    }
    return render(request, 'dashboards/stock_bodega.html', contexto)


@rol_requerido('ejecutivo', 'administrador')
def aprobar_pedido(request, pedido_id):
    """Aprueba un pedido pendiente (cambia estado a aprobado)."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, estado='pendiente')
    pedido.estado = 'aprobado'
    pedido.aprobado_en = timezone.now()
    pedido.save()
    messages.success(request, f'Pedido {pedido.numero_pedido} aprobado.')
    return redirect('dashboards:ejecutivo')


# ============================================================
# OPERADOR LOGÍSTICO
# ============================================================
@rol_requerido('logistica', 'administrador')
def dashboard_logistica(request):
    """Dashboard Logístico: pedidos priorizados por urgencia médica."""
    # Prioridad: critico > urgente > normal
    orden_prioridad = ['critico', 'urgente', 'normal']
    pedidos = Pedido.objects.filter(
        estado__in=['aprobado', 'preparando']
    ).select_related('usuario', 'bodega').order_by('-prioridad', 'creado_en')

    # Separar por prioridad
    criticos = pedidos.filter(prioridad='critico')
    urgentes = pedidos.filter(prioridad='urgente')
    normales = pedidos.filter(prioridad='normal')

    contexto = {
        'criticos': criticos,
        'urgentes': urgentes,
        'normales': normales,
        'total_pedidos': pedidos.count(),
    }
    return render(request, 'dashboards/logistica.html', contexto)


@rol_requerido('logistica', 'administrador')
def preparar_pedido(request, pedido_id):
    """Marca un pedido como en preparación."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, estado='aprobado')
    pedido.estado = 'preparando'
    pedido.save()
    messages.success(request, f'Pedido {pedido.numero_pedido} en preparación.')
    return redirect('dashboards:logistica')


@rol_requerido('logistica', 'administrador')
def despachar_pedido(request, pedido_id):
    """Despacha un pedido: genera tracking y crea envío."""
    pedido = get_object_or_404(Pedido, pk=pedido_id, estado='preparando')

    # Crear envío usando API de tracking simulada
    datos_envio = TrackingAPISimulado.crear_envio(pedido)

    envio = Envio.objects.create(
        pedido=pedido,
        transportista=datos_envio['transportista'],
        numero_seguimiento=datos_envio['numero_seguimiento'],
        estado='etiqueta_creada',
        entrega_estimada=datos_envio['entrega_estimada'],
        peso_kg=datos_envio['peso_estimado'],
        despachado_en=timezone.now(),
    )

    # Generar eventos de demo
    TrackingAPISimulado.generar_eventos_demo(envio)

    # Actualizar pedido
    pedido.estado = 'despachado'
    pedido.numero_seguimiento = datos_envio['numero_seguimiento']
    pedido.despachado_en = timezone.now()
    pedido.save()

    messages.success(
        request,
        f'Pedido {pedido.numero_pedido} despachado. Tracking: {datos_envio["numero_seguimiento"]}'
    )
    return redirect('dashboards:logistica')


# ============================================================
# ANALISTA DE FINANZAS
# ============================================================
@rol_requerido('analista', 'administrador')
def dashboard_analista(request):
    """Dashboard Analista: pagos pendientes de confirmación y auditoría."""
    pagos_completados = Pago.objects.filter(estado='completado').order_by('-completado_en')
    pagos_pendientes = Pago.objects.filter(estado='pendiente').order_by('-creado_en')
    pagos_fallidos = Pago.objects.filter(estado='fallido').order_by('-creado_en')

    total_ingresos = pagos_completados.aggregate(total=Sum('monto'))['total'] or 0
    total_transacciones = pagos_completados.count()

    contexto = {
        'pagos_completados': pagos_completados[:20],
        'pagos_pendientes': pagos_pendientes,
        'pagos_fallidos': pagos_fallidos,
        'total_ingresos': total_ingresos,
        'total_transacciones': total_transacciones,
    }
    return render(request, 'dashboards/analista.html', contexto)


@rol_requerido('analista', 'administrador')
def confirmar_transferencia(request, pago_id):
    """Confirma un pago por transferencia bancaria."""
    pago = get_object_or_404(Pago, pk=pago_id, metodo='transferencia', estado='pendiente')
    pago.estado = 'completado'
    pago.confirmado_por = request.user
    pago.completado_en = timezone.now()
    pago.save()

    # Registrar que el pago fue exitoso sin cambiar el estado del pedido,
    # para que el Ejecutivo lo apruebe manualmente.
    # pago.pedido.estado = 'aprobado'
    # pago.pedido.aprobado_en = timezone.now()
    # pago.pedido.save()

    # Generar boleta electrónica
    boleta = generar_boleta(pago)
    
    # Enviar correo al usuario con la boleta
    enviar_boleta_compra(pago.pedido, pago, boleta)

    messages.success(request, f'Transferencia confirmada y boleta generada para pedido {pago.pedido.numero_pedido}.')
    return redirect('dashboards:analista')


# ============================================================
# ADMINISTRADOR
# ============================================================
@rol_requerido('administrador')
def dashboard_administrador(request):
    """Dashboard Administrador: reportes de venta y métricas generales."""
    # Métricas generales
    total_productos = Producto.objects.filter(activo=True).count()
    total_pedidos = Pedido.objects.count()
    pedidos_hoy = Pedido.objects.filter(creado_en__date=timezone.now().date()).count()
    ingresos_totales = Pago.objects.filter(estado='completado').aggregate(
        total=Sum('monto')
    )['total'] or 0

    # Pedidos por estado
    pedidos_por_estado = Pedido.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado')

    # Últimos pedidos
    ultimos_pedidos = Pedido.objects.select_related('usuario').order_by('-creado_en')[:10]

    # Productos bajo stock
    bajo_stock = ItemStock.objects.filter(
        cantidad__lte=10, cantidad__gt=0
    ).select_related('producto', 'bodega')[:10]

    contexto = {
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
        'pedidos_hoy': pedidos_hoy,
        'ingresos_totales': ingresos_totales,
        'pedidos_por_estado': pedidos_por_estado,
        'ultimos_pedidos': ultimos_pedidos,
        'bajo_stock': bajo_stock,
    }
    return render(request, 'dashboards/administrador.html', contexto)


# ============================================================
# VENDEDOR DE INSUMOS
# ============================================================
@rol_requerido('vendedor', 'administrador')
def dashboard_vendedor(request):
    """Dashboard Vendedor: Monitoreo de referidos, ventas y comisiones."""
    pedidos = Pedido.objects.filter(vendedor=request.user).order_by('-creado_en')
    
    total_ventas = pedidos.filter(estado__in=['aprobado', 'preparando', 'despachado', 'entregado']).aggregate(
        total=Sum('subtotal')
    )['total'] or 0

    # Comisión simulada del 10%
    total_comisiones = (total_ventas * 0.10)

    contexto = {
        'pedidos': pedidos[:20],
        'total_ventas': total_ventas,
        'total_comisiones': total_comisiones,
    }
    return render(request, 'dashboards/vendedor.html', contexto)
