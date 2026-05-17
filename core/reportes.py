"""Servicio de generación de reportes PDF para el Administrador de MediStock.

Tipos de reportes disponibles:
  1. Ventas Generales — resumen de pedidos e ingresos por período
  2. Productos Más Vendidos — ranking de productos
  3. Inventario / Stock Crítico — productos bajo stock mínimo
  4. Clientes Principales — clientes con mayor volumen de compras
  5. Alianzas Estratégicas — estado de alianzas con clínicas
  6. Rendimiento de Vendedores — comisiones y referidos
"""
import io
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Count, F, Q
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


# ────────────────────────────────────────
# Estilos compartidos
# ────────────────────────────────────────
AZUL = colors.HexColor('#0A6EBD')
VERDE = colors.HexColor('#12B886')
GRIS = colors.HexColor('#495057')
GRIS_CLARO = colors.HexColor('#F8F9FA')
BLANCO = colors.white

def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle('TituloReporte', parent=ss['Title'], fontSize=22,
                          textColor=AZUL, spaceAfter=6))
    ss.add(ParagraphStyle('Subtitulo', parent=ss['Heading2'], fontSize=13,
                          textColor=GRIS, spaceAfter=12))
    ss.add(ParagraphStyle('SeccionTitulo', parent=ss['Heading3'], fontSize=14,
                          textColor=AZUL, spaceBefore=18, spaceAfter=8))
    ss.add(ParagraphStyle('CeldaDerecha', parent=ss['Normal'], alignment=TA_RIGHT))
    ss.add(ParagraphStyle('CeldaCentro', parent=ss['Normal'], alignment=TA_CENTER))
    ss.add(ParagraphStyle('Pie', parent=ss['Normal'], fontSize=8,
                          textColor=GRIS, alignment=TA_CENTER))
    return ss


def _header(elements, styles, titulo, subtitulo):
    elements.append(Paragraph('MediStock', styles['TituloReporte']))
    elements.append(Paragraph(titulo, styles['Heading1']))
    elements.append(Paragraph(subtitulo, styles['Subtitulo']))
    elements.append(HRFlowable(width='100%', thickness=1, color=AZUL,
                               spaceAfter=12))


def _tabla_estilo():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])


def _pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(GRIS)
    canvas.drawCentredString(
        letter[0] / 2, 0.5 * inch,
        f'MediStock — Reporte generado el {date.today().strftime("%d/%m/%Y")} — Página {doc.page}'
    )
    canvas.restoreState()


def _formato_clp(valor):
    """Formatea un Decimal/int como moneda CLP sin decimales."""
    if valor is None:
        return '$0'
    return f'${int(valor):,}'.replace(',', '.')


# ════════════════════════════════════════
# 1) REPORTE DE VENTAS GENERALES
# ════════════════════════════════════════
def generar_reporte_ventas(fecha_desde=None, fecha_hasta=None):
    from pedidos.models import Pedido
    from pagos.models import Pago

    hoy = timezone.now().date()
    if not fecha_desde:
        fecha_desde = hoy - timedelta(days=30)
    if not fecha_hasta:
        fecha_hasta = hoy

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, 'Reporte de Ventas Generales',
            f'Período: {fecha_desde.strftime("%d/%m/%Y")} — {fecha_hasta.strftime("%d/%m/%Y")}')

    pedidos = Pedido.objects.filter(
        creado_en__date__gte=fecha_desde,
        creado_en__date__lte=fecha_hasta,
    )
    total_pedidos = pedidos.count()
    ingresos = Pago.objects.filter(
        estado='completado',
        completado_en__date__gte=fecha_desde,
        completado_en__date__lte=fecha_hasta,
    ).aggregate(total=Sum('monto'))['total'] or 0

    # KPIs
    elems.append(Paragraph('Resumen Ejecutivo', styles['SeccionTitulo']))
    kpi_data = [
        ['Total Pedidos', 'Ingresos Totales', 'Ticket Promedio'],
        [str(total_pedidos),
         _formato_clp(ingresos),
         _formato_clp(ingresos / total_pedidos if total_pedidos else 0)],
    ]
    kpi = Table(kpi_data, colWidths=[2.2*inch]*3)
    kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elems.append(kpi)
    elems.append(Spacer(1, 16))

    # Pedidos por estado
    elems.append(Paragraph('Pedidos por Estado', styles['SeccionTitulo']))
    por_estado = pedidos.values('estado').annotate(total=Count('id')).order_by('estado')
    data_estado = [['Estado', 'Cantidad']]
    for e in por_estado:
        data_estado.append([e['estado'].replace('_', ' ').title(), str(e['total'])])
    if len(data_estado) > 1:
        t = Table(data_estado, colWidths=[3.5*inch, 2*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    else:
        elems.append(Paragraph('Sin datos para el período seleccionado.', styles['Normal']))

    # Últimos 15 pedidos
    elems.append(Paragraph('Últimos Pedidos del Período', styles['SeccionTitulo']))
    data_pedidos = [['Nº Pedido', 'Cliente', 'Estado', 'Total', 'Fecha']]
    for p in pedidos.select_related('usuario')[:15]:
        data_pedidos.append([
            p.numero_pedido,
            p.usuario.get_full_name() or p.usuario.username,
            p.get_estado_display(),
            _formato_clp(p.total),
            p.creado_en.strftime('%d/%m/%Y'),
        ])
    if len(data_pedidos) > 1:
        t2 = Table(data_pedidos, colWidths=[1.2*inch, 1.8*inch, 1.3*inch, 1*inch, 1*inch])
        t2.setStyle(_tabla_estilo())
        elems.append(t2)

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# ════════════════════════════════════════
# 2) PRODUCTOS MÁS VENDIDOS
# ════════════════════════════════════════
def generar_reporte_productos_vendidos(fecha_desde=None, fecha_hasta=None):
    from pedidos.models import ItemPedido

    hoy = timezone.now().date()
    if not fecha_desde:
        fecha_desde = hoy - timedelta(days=30)
    if not fecha_hasta:
        fecha_hasta = hoy

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, 'Productos Más Vendidos',
            f'Período: {fecha_desde.strftime("%d/%m/%Y")} — {fecha_hasta.strftime("%d/%m/%Y")}')

    items = ItemPedido.objects.filter(
        pedido__creado_en__date__gte=fecha_desde,
        pedido__creado_en__date__lte=fecha_hasta,
        pedido__estado__in=['aprobado', 'preparando', 'despachado', 'entregado'],
    ).values(
        'producto__nombre', 'producto__sku'
    ).annotate(
        total_vendido=Sum('cantidad'),
        ingresos=Sum(F('cantidad') * F('precio_unitario')),
    ).order_by('-total_vendido')[:20]

    data = [['#', 'SKU', 'Producto', 'Uds. Vendidas', 'Ingresos']]
    for i, item in enumerate(items, 1):
        data.append([
            str(i),
            item['producto__sku'],
            item['producto__nombre'][:40],
            str(item['total_vendido']),
            _formato_clp(item['ingresos']),
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[0.4*inch, 0.9*inch, 2.5*inch, 1*inch, 1.2*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    else:
        elems.append(Paragraph('Sin ventas en el período seleccionado.', styles['Normal']))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# ════════════════════════════════════════
# 3) STOCK CRÍTICO / INVENTARIO
# ════════════════════════════════════════
def generar_reporte_inventario():
    from inventario.models import ItemStock

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, 'Reporte de Inventario — Stock Crítico',
            f'Fecha: {date.today().strftime("%d/%m/%Y")}')

    items = ItemStock.objects.filter(
        cantidad__lte=F('stock_minimo')
    ).select_related('producto', 'bodega').order_by('cantidad')

    data = [['Producto', 'Bodega', 'Lote', 'Stock Actual', 'Stock Mín.', 'Vencimiento']]
    for it in items:
        data.append([
            it.producto.nombre[:35],
            it.bodega.codigo,
            it.numero_lote,
            str(it.cantidad),
            str(it.stock_minimo),
            it.fecha_vencimiento.strftime('%d/%m/%Y'),
        ])

    if len(data) > 1:
        elems.append(Paragraph(f'Se encontraron {len(data)-1} productos en nivel crítico.',
                               styles['Normal']))
        elems.append(Spacer(1, 10))
        t = Table(data, colWidths=[1.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    else:
        elems.append(Paragraph(' Todos los productos están sobre el stock mínimo.',
                               styles['Normal']))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# ════════════════════════════════════════
# 4) CLIENTES PRINCIPALES
# ════════════════════════════════════════
def generar_reporte_clientes():
    from pedidos.models import Pedido

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, 'Clientes Principales',
            f'Fecha: {date.today().strftime("%d/%m/%Y")}')

    clientes = Pedido.objects.filter(
        estado__in=['aprobado', 'preparando', 'despachado', 'entregado']
    ).values(
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'usuario__email',
    ).annotate(
        total_pedidos=Count('id'),
        total_gastado=Sum('total'),
    ).order_by('-total_gastado')[:20]

    data = [['#', 'Cliente', 'Email', 'Pedidos', 'Total Gastado']]
    for i, c in enumerate(clientes, 1):
        nombre = f"{c['usuario__first_name']} {c['usuario__last_name']}".strip()
        if not nombre:
            nombre = c['usuario__username']
        data.append([
            str(i), nombre, c['usuario__email'],
            str(c['total_pedidos']), _formato_clp(c['total_gastado']),
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[0.4*inch, 1.8*inch, 2*inch, 0.8*inch, 1.2*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    else:
        elems.append(Paragraph('Sin datos de clientes aún.', styles['Normal']))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# ════════════════════════════════════════
# 5) ALIANZAS ESTRATÉGICAS
# ════════════════════════════════════════
def generar_reporte_alianzas():
    from core.models import AlianzaClinica

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, 'Reporte de Alianzas Estratégicas',
            f'Fecha: {date.today().strftime("%d/%m/%Y")}')

    alianzas = AlianzaClinica.objects.all()

    # Resumen
    total = alianzas.count()
    activas = alianzas.filter(estado='activa').count()
    negociacion = alianzas.filter(estado='en_negociacion').count()
    vol_total = alianzas.filter(estado='activa').aggregate(
        t=Sum('volumen_mensual_estimado'))['t'] or 0

    kpi_data = [
        ['Total Alianzas', 'Activas', 'En Negociación', 'Vol. Mensual Activas'],
        [str(total), str(activas), str(negociacion), _formato_clp(vol_total)],
    ]
    kpi = Table(kpi_data, colWidths=[1.5*inch]*4)
    kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERDE),
        ('TEXTCOLOR', (0, 0), (-1, 0), BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 13),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elems.append(kpi)
    elems.append(Spacer(1, 16))

    # Tabla detalle
    data = [['Clínica', 'Tipo', 'Estado', 'Dcto.', 'Vol. Mensual']]
    for a in alianzas:
        data.append([
            a.nombre_clinica[:30],
            a.get_tipo_alianza_display()[:25],
            a.get_estado_display(),
            f'{a.descuento_acordado}%',
            _formato_clp(a.volumen_mensual_estimado),
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[1.8*inch, 1.5*inch, 1*inch, 0.7*inch, 1.2*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    else:
        elems.append(Paragraph('Sin alianzas registradas.', styles['Normal']))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# ════════════════════════════════════════
# 6) RENDIMIENTO DE VENDEDORES
# ════════════════════════════════════════
def generar_reporte_vendedores():
    from pedidos.models import Pedido
    from cuentas.models import PerfilUsuario

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, 'Rendimiento de Vendedores',
            f'Fecha: {date.today().strftime("%d/%m/%Y")}')

    vendedores = PerfilUsuario.objects.filter(rol='vendedor').select_related('usuario')
    data = [['Vendedor', 'Código', 'Pedidos Referidos', 'Ventas Totales', 'Comisión (10%)']]

    for v in vendedores:
        pedidos = Pedido.objects.filter(
            vendedor=v.usuario,
            estado__in=['aprobado', 'preparando', 'despachado', 'entregado'],
        )
        total_ventas = pedidos.aggregate(t=Sum('subtotal'))['t'] or 0
        comision = total_ventas * Decimal('0.10')
        data.append([
            v.usuario.get_full_name() or v.usuario.username,
            v.codigo_vendedor or 'N/A',
            str(pedidos.count()),
            _formato_clp(total_ventas),
            _formato_clp(comision),
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[1.5*inch, 1.1*inch, 1.1*inch, 1.2*inch, 1.2*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    else:
        elems.append(Paragraph('Sin vendedores registrados.', styles['Normal']))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# ════════════════════════════════════════
# 7) PDF COTIZACIÓN (para el vendedor)
# ════════════════════════════════════════
def generar_pdf_cotizacion(cotizacion):
    """Genera un PDF profesional de cotización para enviar al cliente."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    _header(elems, styles, f'Cotización Nº {cotizacion.numero}',
            f'Fecha: {cotizacion.creada_en.strftime("%d/%m/%Y")}')

    # Datos del cliente
    elems.append(Paragraph('Datos del Cliente', styles['SeccionTitulo']))
    info = [
        ['Cliente:', cotizacion.nombre_cliente],
        ['Email:', cotizacion.email_cliente],
    ]
    if cotizacion.telefono_cliente:
        info.append(['Teléfono:', cotizacion.telefono_cliente])
    if cotizacion.direccion_cliente:
        info.append(['Dirección:', cotizacion.direccion_cliente])
    info.append(['Válida hasta:', cotizacion.valida_hasta.strftime('%d/%m/%Y')])

    t_info = Table(info, colWidths=[1.5*inch, 4.5*inch])
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elems.append(t_info)
    elems.append(Spacer(1, 16))

    # Tabla de productos
    elems.append(Paragraph('Detalle de Productos', styles['SeccionTitulo']))
    data = [['#', 'Producto', 'SKU', 'Cant.', 'P. Unitario', 'Subtotal']]
    for i, item in enumerate(cotizacion.items.select_related('producto'), 1):
        data.append([
            str(i),
            item.producto.nombre[:35],
            item.producto.sku,
            str(item.cantidad),
            _formato_clp(item.precio_unitario),
            _formato_clp(item.subtotal),
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[0.4*inch, 2.2*inch, 0.9*inch, 0.6*inch, 1*inch, 1*inch])
        t.setStyle(_tabla_estilo())
        elems.append(t)
    elems.append(Spacer(1, 16))

    # Totales
    totales = [
        ['Subtotal:', _formato_clp(cotizacion.subtotal)],
        [f'Descuento ({cotizacion.descuento_porcentaje}%):', f'-{_formato_clp(cotizacion.descuento_monto)}'],
        ['TOTAL:', _formato_clp(cotizacion.total)],
    ]
    t_tot = Table(totales, colWidths=[4*inch, 2*inch])
    t_tot.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (-1, -1), (-1, -1), 13),
        ('TEXTCOLOR', (-1, -1), (-1, -1), AZUL),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, AZUL),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elems.append(t_tot)

    # Notas
    if cotizacion.notas:
        elems.append(Spacer(1, 20))
        elems.append(Paragraph('Notas / Condiciones', styles['SeccionTitulo']))
        elems.append(Paragraph(cotizacion.notas, styles['Normal']))

    # Pie con vendedor
    elems.append(Spacer(1, 30))
    vendedor_nombre = cotizacion.vendedor.get_full_name() or cotizacion.vendedor.username
    elems.append(Paragraph(
        f'Cotización generada por: <b>{vendedor_nombre}</b> — MediStock Ejecutivo de Cuentas',
        styles['Pie']
    ))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf


# Alias for F() needed in the stock report
from django.db.models import F as models_F


# ════════════════════════════════════════
# 8) REPORTE DE STOCK — EJECUTIVO
# ════════════════════════════════════════
def generar_reporte_stock_ejecutivo(producto_id=None):
    """Genera un PDF con el estado del stock, opcionalmente filtrado por producto."""
    from inventario.models import ItemStock
    from productos.models import Producto

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.8*inch, bottomMargin=0.8*inch)
    styles = _styles()
    elems = []

    if producto_id:
        producto = Producto.objects.filter(pk=producto_id).first()
        titulo = f'Reporte de Stock — {producto.nombre}' if producto else 'Reporte de Stock'
    else:
        producto = None
        titulo = 'Reporte General de Stock'

    _header(elems, styles, titulo,
            f'Fecha: {date.today().strftime("%d/%m/%Y")}')

    # Filtrar items de stock
    items_qs = ItemStock.objects.select_related('producto', 'bodega').order_by(
        'bodega__nombre', 'producto__nombre'
    )
    if producto:
        items_qs = items_qs.filter(producto=producto)

    # KPIs
    total_items = items_qs.count()
    total_unidades = items_qs.aggregate(t=Sum('cantidad'))['t'] or 0
    bajo_stock = items_qs.filter(cantidad__lte=models_F('stock_minimo'), cantidad__gt=0).count()
    agotados = items_qs.filter(cantidad=0).count()

    elems.append(Paragraph('Resumen General', styles['SeccionTitulo']))
    kpi_data = [
        ['Registros', 'Unidades Totales', 'Bajo Stock', 'Agotados'],
        [str(total_items), f'{total_unidades:,}'.replace(',', '.'),
         str(bajo_stock), str(agotados)],
    ]
    kpi = Table(kpi_data, colWidths=[1.5*inch]*4)
    kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('TEXTCOLOR', (0, 0), (-1, 0), BLANCO),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 13),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elems.append(kpi)
    elems.append(Spacer(1, 16))

    # Tabla detallada
    elems.append(Paragraph('Detalle de Stock por Producto y Bodega', styles['SeccionTitulo']))
    data = [['Producto', 'SKU', 'Bodega', 'Lote', 'Cantidad', 'Min.', 'Vencimiento', 'Estado']]
    for it in items_qs:
        if it.esta_vencido:
            estado = 'VENCIDO'
        elif it.cantidad == 0:
            estado = 'AGOTADO'
        elif it.stock_bajo:
            estado = 'BAJO'
        else:
            estado = 'OK'
        data.append([
            it.producto.nombre[:25],
            it.producto.sku,
            it.bodega.codigo,
            it.numero_lote,
            str(it.cantidad),
            str(it.stock_minimo),
            it.fecha_vencimiento.strftime('%d/%m/%Y'),
            estado,
        ])

    if len(data) > 1:
        t = Table(data, colWidths=[
            1.5*inch, 0.7*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.5*inch, 0.8*inch, 0.6*inch
        ])
        style = _tabla_estilo()
        for i, row in enumerate(data[1:], 1):
            if row[-1] == 'VENCIDO':
                style.add('TEXTCOLOR', (-1, i), (-1, i), colors.HexColor('#E74C3C'))
                style.add('FONTNAME', (-1, i), (-1, i), 'Helvetica-Bold')
            elif row[-1] == 'AGOTADO':
                style.add('TEXTCOLOR', (-1, i), (-1, i), colors.HexColor('#E74C3C'))
            elif row[-1] == 'BAJO':
                style.add('TEXTCOLOR', (-1, i), (-1, i), colors.HexColor('#F39C12'))
                style.add('FONTNAME', (-1, i), (-1, i), 'Helvetica-Bold')
            else:
                style.add('TEXTCOLOR', (-1, i), (-1, i), colors.HexColor('#2ECC71'))
        t.setStyle(style)
        elems.append(t)
    else:
        elems.append(Paragraph('No se encontraron registros de stock.', styles['Normal']))

    doc.build(elems, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    buf.seek(0)
    return buf
