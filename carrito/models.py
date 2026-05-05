from django.db import models
from django.contrib.auth.models import User


class Carrito(models.Model):
    """Carrito de compras."""
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='carritos', verbose_name='Usuario')
    clave_sesion = models.CharField(max_length=40, null=True, blank=True, verbose_name='Clave de Sesion')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name='Actualizado')

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        if self.usuario:
            return f"Carrito de {self.usuario.username}"
        return f"Carrito anonimo ({self.clave_sesion})"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    """Item individual dentro del carrito."""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items', verbose_name='Carrito')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, verbose_name='Producto')
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')

    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ['carrito', 'producto']

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad
