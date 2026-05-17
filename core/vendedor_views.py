"""Vistas de Cotizaciones y Asesoramiento para el Vendedor."""
import uuid
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage as DjangoEmail
from django.utils import timezone
from django.db.models import Sum, F

from cuentas.decorators import rol_requerido
from core.models import Cotizacion, ItemCotizacion, VisitaAsesoramiento
from core.forms import CotizacionForm, VisitaForm
from productos.models import Producto


# ════════════════════════════════════════
# COTIZACIONES
# ════════════════════════════════════════
@rol_requerido('vendedor')
def lista_cotizaciones(request):
    """Lista de cotizaciones del vendedor actual."""
    cotizaciones = Cotizacion.objects.filter(vendedor=request.user)
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro:
        cotizaciones = cotizaciones.filter(estado=estado_filtro)
    contexto = {
        'cotizaciones': cotizaciones,
        'estado_filtro': estado_filtro,
        'total': cotizaciones.count(),
        'borradores': cotizaciones.filter(estado='borrador').count(),
        'enviadas': cotizaciones.filter(estado='enviada').count(),
        'aprobadas': cotizaciones.filter(estado='aprobada').count(),
    }
    return render(request, 'vendedor/cotizaciones_lista.html', contexto)


@rol_requerido('vendedor')
def crear_cotizacion(request):
    """Paso 1: Crear cotización con datos del cliente."""
    if request.method == 'POST':
        form = CotizacionForm(request.POST)
        if form.is_valid():
            cot = form.save(commit=False)
            cot.vendedor = request.user
            cot.numero = f"COT-{uuid.uuid4().hex[:8].upper()}"
            cot.save()
            messages.success(request, f'Cotización {cot.numero} creada. Ahora agrega productos.')
            return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)
    else:
        form = CotizacionForm(initial={
            'valida_hasta': (timezone.now() + timedelta(days=15)).date(),
        })
    return render(request, 'vendedor/cotizacion_form.html', {'form': form, 'es_edicion': False})


@rol_requerido('vendedor')
def detalle_cotizacion(request, cot_id):
    """Detalle de cotización con sus items y acciones."""
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    items = cot.items.select_related('producto')
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    contexto = {
        'cotizacion': cot,
        'items': items,
        'productos': productos,
    }
    return render(request, 'vendedor/cotizacion_detalle.html', contexto)


@rol_requerido('vendedor')
def editar_cotizacion(request, cot_id):
    """Editar datos del cliente de una cotización."""
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    if cot.estado not in ('borrador', 'enviada'):
        messages.error(request, 'Solo puedes editar cotizaciones en borrador o enviadas.')
        return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)
    if request.method == 'POST':
        form = CotizacionForm(request.POST, instance=cot)
        if form.is_valid():
            form.save()
            cot.calcular_totales()
            messages.success(request, 'Cotización actualizada.')
            return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)
    else:
        form = CotizacionForm(instance=cot)
    return render(request, 'vendedor/cotizacion_form.html', {'form': form, 'cotizacion': cot, 'es_edicion': True})


@rol_requerido('vendedor')
def agregar_item_cotizacion(request, cot_id):
    """Agregar un producto a la cotización."""
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))
        producto = get_object_or_404(Producto, pk=producto_id)
        # Si ya existe, sumar cantidad
        item_existente = cot.items.filter(producto=producto).first()
        if item_existente:
            item_existente.cantidad += cantidad
            item_existente.save()
        else:
            ItemCotizacion.objects.create(
                cotizacion=cot,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
            )
        cot.calcular_totales()
        messages.success(request, f'{producto.nombre} agregado a la cotización.')
    return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)


@rol_requerido('vendedor')
def eliminar_item_cotizacion(request, cot_id, item_id):
    """Eliminar un producto de la cotización."""
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    item = get_object_or_404(ItemCotizacion, pk=item_id, cotizacion=cot)
    item.delete()
    cot.calcular_totales()
    messages.success(request, 'Producto eliminado de la cotización.')
    return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)


@rol_requerido('vendedor')
def cambiar_estado_cotizacion(request, cot_id, nuevo_estado):
    """Cambiar el estado de una cotización."""
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    estados_validos = ['borrador', 'enviada', 'aprobada', 'rechazada', 'vencida']
    if nuevo_estado not in estados_validos:
        messages.error(request, 'Estado no válido.')
        return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)
    cot.estado = nuevo_estado
    cot.save()
    messages.success(request, f'Estado cambiado a "{cot.get_estado_display()}".')
    return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)


@rol_requerido('vendedor')
def descargar_cotizacion_pdf(request, cot_id):
    """Genera y descarga la cotización como PDF."""
    from core.reportes import generar_pdf_cotizacion
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    buf = generar_pdf_cotizacion(cot)
    fecha_str = timezone.now().strftime('%Y%m%d')
    filename = f'cotizacion_{cot.numero}_{fecha_str}.pdf'
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@rol_requerido('vendedor')
def enviar_cotizacion_email(request, cot_id):
    """Envía la cotización por correo al cliente y la marca como 'enviada'."""
    from core.reportes import generar_pdf_cotizacion
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)
    buf = generar_pdf_cotizacion(cot)
    fecha_str = timezone.now().strftime('%Y%m%d')
    filename = f'cotizacion_{cot.numero}_{fecha_str}.pdf'

    email = DjangoEmail(
        subject=f'[MediStock] Cotización {cot.numero}',
        body=f'Estimado/a,\n\n'
             f'Adjunto encontrará la cotización Nº {cot.numero} generada por {request.user.get_full_name()}.\n'
             f'Esta cotización es válida hasta el {cot.valida_hasta.strftime("%d/%m/%Y")}.\n\n'
             f'Para cualquier consulta, no dude en contactarnos.\n\n'
             f'Atentamente,\n{request.user.get_full_name()}\nMediStock — Ejecutivo de Cuentas',
        from_email='MediStock <medistock.soporte@gmail.com>',
        to=[cot.email_cliente],
        reply_to=[request.user.email],
    )
    email.attach(filename, buf.read(), 'application/pdf')
    email.send(fail_silently=False)

    if cot.estado == 'borrador':
        cot.estado = 'enviada'
        cot.save()

    messages.success(request, f' Cotización enviada a {cot.email_cliente}.')
    return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)


@rol_requerido('vendedor')
def convertir_cotizacion_pedido(request, cot_id):
    """Convierte una cotización aprobada en un Pedido real."""
    from pedidos.models import Pedido, ItemPedido
    cot = get_object_or_404(Cotizacion, pk=cot_id, vendedor=request.user)

    if cot.estado != 'aprobada':
        messages.error(request, 'Solo puedes convertir cotizaciones aprobadas.')
        return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)

    if cot.pedido_generado:
        messages.warning(request, f'Esta cotización ya fue convertida al pedido {cot.pedido_generado.numero_pedido}.')
        return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)

    if not cot.items.exists():
        messages.error(request, 'La cotización no tiene productos.')
        return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)

    # Crear pedido
    pedido = Pedido(
        usuario=cot.cliente or request.user,
        estado='pendiente',
        prioridad='normal',
        tipo_despacho='normal',
        direccion_envio=cot.direccion_cliente or 'Por confirmar',
        ciudad_envio='Por confirmar',
        region_envio='Por confirmar',
        subtotal=cot.subtotal,
        descuento=cot.descuento_monto,
        total=cot.total,
        vendedor=request.user,
        notas=f'Generado desde Cotización {cot.numero}',
    )
    pedido.save()

    for item in cot.items.all():
        ItemPedido.objects.create(
            pedido=pedido,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
        )

    cot.estado = 'convertida'
    cot.pedido_generado = pedido
    cot.save()

    messages.success(request, f' Cotización convertida al Pedido {pedido.numero_pedido}.')
    return redirect('dashboards:detalle_cotizacion', cot_id=cot.pk)


# ════════════════════════════════════════
# ASESORAMIENTO
# ════════════════════════════════════════
@rol_requerido('vendedor')
def lista_visitas(request):
    """Lista de visitas de asesoramiento."""
    visitas = VisitaAsesoramiento.objects.filter(vendedor=request.user)
    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        visitas = visitas.filter(tipo=tipo_filtro)
    contexto = {
        'visitas': visitas,
        'tipo_filtro': tipo_filtro,
        'total': visitas.count(),
        'pendientes': visitas.filter(resultado='pendiente').count(),
    }
    return render(request, 'vendedor/visitas_lista.html', contexto)


@rol_requerido('vendedor')
def crear_visita(request):
    """Registrar nueva visita de asesoramiento."""
    if request.method == 'POST':
        form = VisitaForm(request.POST)
        if form.is_valid():
            visita = form.save(commit=False)
            visita.vendedor = request.user
            visita.save()
            messages.success(request, f'Visita a "{visita.nombre_institucion}" registrada.')
            return redirect('dashboards:lista_visitas')
    else:
        form = VisitaForm(initial={'fecha_visita': timezone.now().date()})
    return render(request, 'vendedor/visita_form.html', {'form': form, 'es_edicion': False})


@rol_requerido('vendedor')
def editar_visita(request, visita_id):
    """Editar visita existente."""
    visita = get_object_or_404(VisitaAsesoramiento, pk=visita_id, vendedor=request.user)
    if request.method == 'POST':
        form = VisitaForm(request.POST, instance=visita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Visita actualizada.')
            return redirect('dashboards:lista_visitas')
    else:
        form = VisitaForm(instance=visita)
    return render(request, 'vendedor/visita_form.html', {'form': form, 'visita': visita, 'es_edicion': True})


@rol_requerido('vendedor')
def eliminar_visita(request, visita_id):
    """Eliminar visita de asesoramiento."""
    visita = get_object_or_404(VisitaAsesoramiento, pk=visita_id, vendedor=request.user)
    if request.method == 'POST':
        nombre = visita.nombre_institucion
        visita.delete()
        messages.success(request, f'Visita a "{nombre}" eliminada.')
        return redirect('dashboards:lista_visitas')
    return render(request, 'vendedor/visita_confirm_delete.html', {'visita': visita})
