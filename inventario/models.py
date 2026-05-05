from django.db import models


class Bodega(models.Model):
    """Bodega / Centro de distribucion de MEDISTOCK."""
    nombre = models.CharField(max_length=100, verbose_name='Nombre')
    codigo = models.CharField(max_length=10, unique=True, verbose_name='Codigo')
    direccion = models.TextField(verbose_name='Direccion')
    ciudad = models.CharField(max_length=100, verbose_name='Ciudad')
    region = models.CharField(max_length=100, verbose_name='Region')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.ciudad})"


class ItemStock(models.Model):
    """Control de stock por producto, bodega y lote."""
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, related_name='items_stock', verbose_name='Producto')
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name='items_stock', verbose_name='Bodega')
    numero_lote = models.CharField(max_length=50, verbose_name='Numero de Lote')
    fecha_vencimiento = models.DateField(verbose_name='Fecha de Vencimiento')
    cantidad = models.PositiveIntegerField(default=0, verbose_name='Cantidad Disponible')
    stock_minimo = models.PositiveIntegerField(default=10, verbose_name='Stock Minimo')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Registrado')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        verbose_name = 'Item de Stock'
        verbose_name_plural = 'Items de Stock'
        unique_together = ['producto', 'bodega', 'numero_lote']
        ordering = ['fecha_vencimiento']

    def __str__(self):
        return f"{self.producto.nombre} - Lote {self.numero_lote} - Bodega {self.bodega.codigo}"

    @property
    def stock_bajo(self):
        return self.cantidad <= self.stock_minimo

    @property
    def esta_vencido(self):
        from django.utils import timezone
        return self.fecha_vencimiento < timezone.now().date()
