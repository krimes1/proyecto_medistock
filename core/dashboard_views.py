"""Vistas de dashboards segmentados por rol.

- Ejecutivo de Cuentas: stock multi-bodega, aprobar compras, gestión de stock
- Operador Logístico: órdenes por urgencia, despachar
- Analista de Finanzas: confirmar pagos, auditar
- Administrador: reportes de venta, alianzas
"""
import json
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.views.decorators.http import require_POST
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
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if pedido.estado == 'aprobado':
        messages.info(request, f'El pedido {pedido.numero_pedido} ya se encuentra aprobado.')
    elif pedido.estado == 'pendiente':
        pedido.estado = 'aprobado'
        pedido.aprobado_en = timezone.now()
        pedido.save()
        messages.success(request, f'Pedido {pedido.numero_pedido} aprobado exitosamente.')
    else:
        messages.warning(request, f'El pedido {pedido.numero_pedido} está en estado "{pedido.get_estado_display()}" y no puede ser aprobado.')
    
    return redirect('dashboards:ejecutivo')


@rol_requerido('ejecutivo', 'administrador')
def pedidos_aprobados(request):
    """Vista de lista de pedidos ya aprobados por el ejecutivo."""
    # Obtenemos los pedidos que ya fueron aprobados, es decir, que no están pendientes
    pedidos = Pedido.objects.exclude(estado='pendiente').exclude(estado='cancelado').select_related('usuario').order_by('-aprobado_en', '-creado_en')
    
    contexto = {
        'pedidos': pedidos,
        'total_pedidos': pedidos.count(),
    }
    return render(request, 'dashboards/ejecutivo_pedidos_aprobados.html', contexto)


@rol_requerido('ejecutivo', 'administrador')
def revisar_stock(request):
    """Vista de revisión de stock: lista de todos los productos con stock editable."""
    busqueda = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    estado_stock = request.GET.get('estado', '')

    productos = Producto.objects.filter(activo=True).select_related('categoria', 'marca')

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(sku__icontains=busqueda) |
            Q(marca__nombre__icontains=busqueda)
        )

    if categoria:
        productos = productos.filter(categoria__slug=categoria)

    productos = productos.order_by('nombre')

    # Enriquecer con datos de stock
    productos_stock = []
    for prod in productos:
        items = ItemStock.objects.filter(producto=prod).select_related('bodega')
        stock_total = sum(i.cantidad for i in items)
        stock_minimo = min((i.stock_minimo for i in items), default=10)

        if estado_stock == 'critico' and stock_total > stock_minimo:
            continue
        if estado_stock == 'ok' and stock_total <= stock_minimo:
            continue
        if estado_stock == 'agotado' and stock_total > 0:
            continue

        productos_stock.append({
            'producto': prod,
            'items': items,
            'stock_total': stock_total,
            'stock_minimo': stock_minimo,
            'estado': 'agotado' if stock_total == 0 else ('critico' if stock_total <= stock_minimo else 'ok'),
        })

    from productos.models import Categoria
    categorias = Categoria.objects.filter(activa=True).order_by('nombre')

    contexto = {
        'productos_stock': productos_stock,
        'total_productos': len(productos_stock),
        'busqueda': busqueda,
        'categoria_filtro': categoria,
        'estado_filtro': estado_stock,
        'categorias': categorias,
    }
    return render(request, 'dashboards/revisar_stock.html', contexto)


@rol_requerido('ejecutivo', 'administrador')
@require_POST
def actualizar_stock(request, item_id):
    """Actualiza la cantidad de stock de un ItemStock via AJAX."""
    item = get_object_or_404(ItemStock, pk=item_id)
    try:
        data = json.loads(request.body)
        nueva_cantidad = int(data.get('cantidad', 0))
        if nueva_cantidad < 0:
            return JsonResponse({'error': 'La cantidad no puede ser negativa.'}, status=400)
        item.cantidad = nueva_cantidad
        item.save()
        # Recalcular stock total del producto
        stock_total = ItemStock.objects.filter(producto=item.producto).aggregate(
            total=Sum('cantidad')
        )['total'] or 0
        return JsonResponse({
            'ok': True,
            'nueva_cantidad': item.cantidad,
            'stock_total': stock_total,
            'estado': 'agotado' if stock_total == 0 else ('critico' if stock_total <= item.stock_minimo else 'ok'),
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Cantidad inválida.'}, status=400)


@rol_requerido('ejecutivo', 'administrador')
def descargar_reporte_stock(request):
    """Genera y descarga un reporte PDF de stock (de un producto o de todos)."""
    producto_id = request.GET.get('producto_id', '')
    from core.reportes import generar_reporte_stock_ejecutivo
    buf = generar_reporte_stock_ejecutivo(producto_id=producto_id if producto_id else None)
    fecha_str = timezone.now().strftime('%Y%m%d')
    filename = f'medistock_stock_{fecha_str}.pdf'
    response = HttpResponse(buf.read(), content_type='application/pdf')
    if request.GET.get('preview') == 'true':
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@rol_requerido('ejecutivo', 'administrador')
def enviar_reporte_stock(request):
    """Genera un reporte PDF de stock y lo envía al correo indicado."""
    email_destino = request.GET.get('email', '').strip()
    producto_id = request.GET.get('producto_id', '')

    if not email_destino:
        messages.error(request, 'Debes indicar un correo de destino.')
        return redirect('dashboards:revisar_stock')

    from core.reportes import generar_reporte_stock_ejecutivo
    buf = generar_reporte_stock_ejecutivo(producto_id=producto_id if producto_id else None)
    fecha_str = timezone.now().strftime('%Y%m%d')
    filename = f'medistock_stock_{fecha_str}.pdf'

    email = EmailMessage(
        subject='[MediStock] Reporte de Stock',
        body=f'Estimado/a,\n\n'
             f'Adjunto encontrará el reporte de stock generado el {timezone.now().strftime("%d/%m/%Y %H:%M")}.\n\n'
             f'Generado por: {request.user.get_full_name() or request.user.username}\n\n'
             f'Atentamente,\nSistema MediStock',
        from_email='MediStock <medistock.soporte@gmail.com>',
        to=[email_destino],
    )
    email.attach(filename, buf.read(), 'application/pdf')
    email.send(fail_silently=False)

    messages.success(request, f'El reporte de stock fue enviado a {email_destino}.')
    return redirect('dashboards:revisar_stock')


# ============================================================
# OPERADOR LOGÍSTICO
# ============================================================
@rol_requerido('logistica', 'administrador')
def dashboard_logistica(request):
    """Dashboard Logístico: pedidos priorizados por urgencia médica, filtrados por bodega asignada."""
    # Prioridad: critico > urgente > normal
    pedidos = Pedido.objects.filter(
        estado__in=['pendiente', 'aprobado', 'preparando']
    ).select_related('usuario', 'bodega').order_by('-prioridad', 'creado_en')

    # Filtrar por bodega asignada al operador (admin ve todo)
    bodega_asignada = None
    if request.user.perfil.rol == 'logistica' and request.user.perfil.bodega:
        bodega_asignada = request.user.perfil.bodega
        pedidos = pedidos.filter(bodega=bodega_asignada)

    # Separar por estado
    pedidos_previos = pedidos.filter(estado='pendiente')
    pedidos_nuevos = pedidos.filter(estado='aprobado')
    pedidos_curso = pedidos.filter(estado='preparando')

    contexto = {
        'previos_criticos': pedidos_previos.filter(prioridad='critico'),
        'previos_urgentes': pedidos_previos.filter(prioridad='urgente'),
        'previos_normales': pedidos_previos.filter(prioridad='normal'),
        'nuevos_criticos': pedidos_nuevos.filter(prioridad='critico'),
        'nuevos_urgentes': pedidos_nuevos.filter(prioridad='urgente'),
        'nuevos_normales': pedidos_nuevos.filter(prioridad='normal'),
        'curso_criticos': pedidos_curso.filter(prioridad='critico'),
        'curso_urgentes': pedidos_curso.filter(prioridad='urgente'),
        'curso_normales': pedidos_curso.filter(prioridad='normal'),
        'total_previos': pedidos_previos.count(),
        'total_nuevos': pedidos_nuevos.count(),
        'total_curso': pedidos_curso.count(),
        'total_pedidos': pedidos.count(),
        'bodega_asignada': bodega_asignada,
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
        estado='en_transito',
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
def revisar_transferencia(request, pago_id):
    """Vista para que el analista revise el comprobante y los detalles del pedido."""
    pago = get_object_or_404(Pago, pk=pago_id, metodo='transferencia', estado='pendiente')
    pedido = pago.pedido
    items = pedido.items.select_related('producto').all()

    contexto = {
        'pago': pago,
        'pedido': pedido,
        'items': items,
    }
    return render(request, 'dashboards/revisar_transferencia.html', contexto)


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
# ADMINISTRADOR — Centro de Reportes y Alianzas
# ============================================================
@rol_requerido('administrador')
def dashboard_administrador(request):
    """Dashboard Administrador: centro de reportes, métricas y alianzas."""
    from core.models import AlianzaClinica

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

    # Alianzas resumen
    alianzas = AlianzaClinica.objects.all()
    alianzas_activas = alianzas.filter(estado='activa').count()
    alianzas_negociacion = alianzas.filter(estado='en_negociacion').count()
    total_alianzas = alianzas.count()

    contexto = {
        'total_productos': total_productos,
        'total_pedidos': total_pedidos,
        'pedidos_hoy': pedidos_hoy,
        'ingresos_totales': ingresos_totales,
        'pedidos_por_estado': pedidos_por_estado,
        'ultimos_pedidos': ultimos_pedidos,
        'bajo_stock': bajo_stock,
        'alianzas_activas': alianzas_activas,
        'alianzas_negociacion': alianzas_negociacion,
        'total_alianzas': total_alianzas,
    }
    return render(request, 'dashboards/administrador.html', contexto)


# ------------ Descarga de Reportes PDF ----------------
REPORTES_MAP = {
    'ventas': ('Reporte de Ventas Generales', True),
    'productos': ('Productos Más Vendidos', True),
    'inventario': ('Stock Crítico', False),
    'clientes': ('Clientes Principales', False),
    'alianzas': ('Alianzas Estratégicas', False),
    'vendedores': ('Rendimiento de Vendedores', False),
}

def _generar_pdf(tipo, fecha_desde=None, fecha_hasta=None):
    from core.reportes import (
        generar_reporte_ventas, generar_reporte_productos_vendidos,
        generar_reporte_inventario, generar_reporte_clientes,
        generar_reporte_alianzas, generar_reporte_vendedores,
    )
    generadores = {
        'ventas': lambda: generar_reporte_ventas(fecha_desde, fecha_hasta),
        'productos': lambda: generar_reporte_productos_vendidos(fecha_desde, fecha_hasta),
        'inventario': generar_reporte_inventario,
        'clientes': generar_reporte_clientes,
        'alianzas': generar_reporte_alianzas,
        'vendedores': generar_reporte_vendedores,
    }
    return generadores[tipo]()


@rol_requerido('administrador')
def descargar_reporte(request, tipo):
    """Genera y descarga un reporte PDF."""
    if tipo not in REPORTES_MAP:
        messages.error(request, 'Tipo de reporte no válido.')
        return redirect('dashboards:administrador')

    titulo, usa_fechas = REPORTES_MAP[tipo]
    fecha_desde = fecha_hasta = None
    if usa_fechas:
        from core.forms import ReporteFiltroForm
        form = ReporteFiltroForm(request.GET)
        if form.is_valid():
            fecha_desde = form.cleaned_data.get('fecha_desde')
            fecha_hasta = form.cleaned_data.get('fecha_hasta')

    buf = _generar_pdf(tipo, fecha_desde, fecha_hasta)
    fecha_str = timezone.now().strftime('%Y%m%d')
    filename = f'medistock_{tipo}_{fecha_str}.pdf'
    response = HttpResponse(buf.read(), content_type='application/pdf')
    if request.GET.get('preview') == 'true':
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@rol_requerido('administrador')
def enviar_reporte(request, tipo):
    """Genera un reporte PDF y lo envía al correo del administrador."""
    if tipo not in REPORTES_MAP:
        messages.error(request, 'Tipo de reporte no válido.')
        return redirect('dashboards:administrador')

    titulo, usa_fechas = REPORTES_MAP[tipo]
    fecha_desde = fecha_hasta = None
    if usa_fechas:
        from core.forms import ReporteFiltroForm
        form = ReporteFiltroForm(request.GET)
        if form.is_valid():
            fecha_desde = form.cleaned_data.get('fecha_desde')
            fecha_hasta = form.cleaned_data.get('fecha_hasta')

    buf = _generar_pdf(tipo, fecha_desde, fecha_hasta)
    fecha_str = timezone.now().strftime('%Y%m%d')
    filename = f'medistock_{tipo}_{fecha_str}.pdf'

    email = EmailMessage(
        subject=f'[MediStock] {titulo}',
        body=f'Estimado/a {request.user.get_full_name() or request.user.username},\n\n'
             f'Adjunto encontrará el reporte "{titulo}" generado el {timezone.now().strftime("%d/%m/%Y %H:%M")}.\n\n'
             f'Atentamente,\nSistema MediStock',
        from_email='MediStock <medistock.soporte@gmail.com>',
        to=[request.user.email],
    )
    email.attach(filename, buf.read(), 'application/pdf')
    email.send(fail_silently=False)

    messages.success(request, f' El reporte "{titulo}" fue enviado a {request.user.email}.')
    return redirect('dashboards:administrador')


# ------------ CRUD Alianzas Estratégicas ----------------
@rol_requerido('administrador')
def lista_alianzas(request):
    """Lista completa de alianzas estratégicas."""
    from core.models import AlianzaClinica
    alianzas = AlianzaClinica.objects.all()
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        alianzas = alianzas.filter(estado=estado_filtro)
    contexto = {
        'alianzas': alianzas,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'dashboards/alianzas_lista.html', contexto)


@rol_requerido('administrador')
def crear_alianza(request):
    """Crear nueva alianza estratégica."""
    from core.forms import AlianzaClinicaForm
    if request.method == 'POST':
        form = AlianzaClinicaForm(request.POST)
        if form.is_valid():
            alianza = form.save(commit=False)
            alianza.creada_por = request.user
            alianza.save()
            messages.success(request, f'Alianza con "{alianza.nombre_clinica}" creada exitosamente.')
            return redirect('dashboards:lista_alianzas')
    else:
        form = AlianzaClinicaForm()
    return render(request, 'dashboards/alianza_form.html', {'form': form, 'es_edicion': False})


@rol_requerido('administrador')
def editar_alianza(request, alianza_id):
    """Editar alianza existente."""
    from core.models import AlianzaClinica
    from core.forms import AlianzaClinicaForm
    alianza = get_object_or_404(AlianzaClinica, pk=alianza_id)
    if request.method == 'POST':
        form = AlianzaClinicaForm(request.POST, instance=alianza)
        if form.is_valid():
            form.save()
            messages.success(request, f'Alianza con "{alianza.nombre_clinica}" actualizada.')
            return redirect('dashboards:lista_alianzas')
    else:
        form = AlianzaClinicaForm(instance=alianza)
    return render(request, 'dashboards/alianza_form.html', {'form': form, 'alianza': alianza, 'es_edicion': True})


@rol_requerido('administrador')
def eliminar_alianza(request, alianza_id):
    """Eliminar alianza estratégica."""
    from core.models import AlianzaClinica
    alianza = get_object_or_404(AlianzaClinica, pk=alianza_id)
    if request.method == 'POST':
        nombre = alianza.nombre_clinica
        alianza.delete()
        messages.success(request, f'Alianza con "{nombre}" eliminada.')
        return redirect('dashboards:lista_alianzas')
    return render(request, 'dashboards/alianza_confirm_delete.html', {'alianza': alianza})



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
