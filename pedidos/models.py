from django.db import models
from django.contrib.auth.models import User


class Pedido(models.Model):
    """Pedido de compra."""
    OPCIONES_ESTADO = [
        ('pendiente', 'Pendiente'),
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
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Costo de Envio')
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='IVA')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
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

    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            import uuid
            self.numero_pedido = f"MS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


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
