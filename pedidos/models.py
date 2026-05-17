from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .emails import enviar_notificacion_estado


class Pedido(models.Model):
    """Pedido de compra."""
    OPCIONES_ESTADO = [
        ('pendiente', 'Por Aprobación del Ejecutivo'),
        ('aprobado', 'Aprobado por Ejecutivo'),
        ('preparando', 'En Preparacion'),
        ('despachado', 'Despachado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    OPCIONES_PRIORIDAD = [
        ('normal', 'Normal'),
        ('urgente', 'Urgente'),
        ('critico', 'Critico - Urgencia Medica'),
    ]
    OPCIONES_DESPACHO = [
        ('express', 'Despacho Express'),
        ('normal', 'Despacho Normal'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos', verbose_name='Cliente')
    numero_pedido = models.CharField(max_length=20, unique=True, verbose_name='Nro de Pedido')
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='pendiente', verbose_name='Estado')
    prioridad = models.CharField(max_length=20, choices=OPCIONES_PRIORIDAD, default='normal', verbose_name='Prioridad')
    tipo_despacho = models.CharField(max_length=20, choices=OPCIONES_DESPACHO, default='normal', verbose_name='Tipo de Despacho')
    bodega = models.ForeignKey('inventario.Bodega', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Bodega de Origen')
    direccion_envio = models.TextField(verbose_name='Direccion de Envio')
    ciudad_envio = models.CharField(max_length=100, verbose_name='Ciudad')
    region_envio = models.CharField(max_length=100, verbose_name='Region')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Descuento')
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Costo de Envio')
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='IVA')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='ventas', null=True, blank=True, verbose_name='Vendedor (Referido)')
    numero_seguimiento = models.CharField(max_length=100, blank=True, verbose_name='Nro de Seguimiento')
    notas = models.TextField(blank=True, verbose_name='Notas')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creacion')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Ultima Actualizacion')
    aprobado_en = models.DateTimeField(null=True, blank=True, verbose_name='Aprobado el')
    despachado_en = models.DateTimeField(null=True, blank=True, verbose_name='Despachado el')
    entregado_en = models.DateTimeField(null=True, blank=True, verbose_name='Entregado el')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Pedido {self.numero_pedido} - {self.get_estado_display()}"

    def get_estado_display(self):
        estado_dict = dict(self.OPCIONES_ESTADO)
        base_display = estado_dict.get(self.estado, self.estado)
        if self.estado == 'aprobado':
            bodega_nombre = self.bodega.nombre if self.bodega else "Bodega Central"
            return f"Esperando aprobación de logística - {bodega_nombre}"
        if self.estado == 'cancelado':
            bodega_nombre = self.bodega.nombre if self.bodega else "Bodega Central"
            return f"Cancelado por - {bodega_nombre}"
        return base_display

    def clean(self):
        super().clean()
        if self.pk:
            old_estado = Pedido.objects.get(pk=self.pk).estado
            if self.estado in ['preparando', 'despachado', 'entregado']:
                if old_estado == 'pendiente' and self.estado != 'aprobado':
                    raise ValidationError({'estado': 'El pedido no puede estar listo o en proceso sin las aprobaciones necesarias.'})

    def save(self, *args, **kwargs):
        self.clean()
        is_new = self.pk is None
        old_estado = None
        if not is_new:
            old_estado = Pedido.objects.get(pk=self.pk).estado

        if not self.numero_pedido:
            import uuid
            self.numero_pedido = f"MS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

        if not is_new and old_estado != self.estado:
            # Avoid sending state change if it's approved and we just bought it, 
            # because the purchase boleta email covers it. But as per requirement:
            # "también cada vez que cambie el estado de su pedido o sea aprobado por alguien"
            # It's better to just send it. 
            # Or if old_estado == 'pendiente' and self.estado == 'aprobado': we could skip,
            # but we will send it as requested.
            enviar_notificacion_estado(self, old_estado)


class ItemPedido(models.Model):
    """Item dentro de un pedido."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items', verbose_name='Pedido')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, verbose_name='Producto')
    cantidad = models.PositiveIntegerField(verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Unitario')
    numero_lote = models.CharField(max_length=50, blank=True, verbose_name='Nro de Lote')

    class Meta:
        verbose_name = 'Item del Pedido'
        verbose_name_plural = 'Items del Pedido'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} @ ${self.precio_unitario}"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
