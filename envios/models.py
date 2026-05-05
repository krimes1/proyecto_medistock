from django.db import models


class Envio(models.Model):
    """Envio asociado a un pedido. Integracion con API de tracking."""
    OPCIONES_ESTADO = [
        ('etiqueta_creada', 'Etiqueta Creada'),
        ('recogido', 'Recogido'),
        ('en_transito', 'En Transito'),
        ('en_reparto', 'En Reparto'),
        ('entregado', 'Entregado'),
        ('devuelto', 'Devuelto'),
    ]
    OPCIONES_TRANSPORTISTA = [
        ('chilexpress', 'Chilexpress'),
        ('starken', 'Starken'),
        ('bluexpress', 'Blue Express'),
        ('correos', 'Correos de Chile'),
    ]

    pedido = models.OneToOneField('pedidos.Pedido', on_delete=models.CASCADE, related_name='envio', verbose_name='Pedido')
    transportista = models.CharField(max_length=50, choices=OPCIONES_TRANSPORTISTA, default='chilexpress', verbose_name='Transportista')
    numero_seguimiento = models.CharField(max_length=100, blank=True, verbose_name='Nro de Seguimiento')
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='etiqueta_creada', verbose_name='Estado')
    entrega_estimada = models.DateField(null=True, blank=True, verbose_name='Entrega Estimada')
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name='Peso (kg)')
    despachado_en = models.DateTimeField(null=True, blank=True, verbose_name='Despachado el')
    entregado_en = models.DateTimeField(null=True, blank=True, verbose_name='Entregado el')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado')

    class Meta:
        verbose_name = 'Envio'
        verbose_name_plural = 'Envios'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Envio {self.numero_seguimiento or 'Sin tracking'} - {self.get_estado_display()}"


class EventoSeguimiento(models.Model):
    """Evento de tracking del envio (historial de estados)."""
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name='eventos', verbose_name='Envio')
    estado = models.CharField(max_length=100, verbose_name='Estado')
    ubicacion = models.CharField(max_length=200, blank=True, verbose_name='Ubicacion')
    descripcion = models.TextField(blank=True, verbose_name='Descripcion')
    fecha_hora = models.DateTimeField(verbose_name='Fecha/Hora')

    class Meta:
        verbose_name = 'Evento de Seguimiento'
        verbose_name_plural = 'Eventos de Seguimiento'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.estado} - {self.ubicacion} - {self.fecha_hora}"
