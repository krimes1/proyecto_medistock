"""Modelos del core: Alianzas Estratégicas con Clínicas."""
from django.db import models
from django.contrib.auth.models import User


class AlianzaClinica(models.Model):
    """Alianza estratégica entre MediStock y una clínica/institución de salud."""
    OPCIONES_ESTADO = [
        ('prospecto', 'Prospecto'),
        ('en_negociacion', 'En Negociación'),
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
    ]
    OPCIONES_TIPO = [
        ('distribucion_exclusiva', 'Distribución Exclusiva'),
        ('contrato_suministro', 'Contrato de Suministro'),
        ('precio_preferencial', 'Precio Preferencial'),
        ('consignacion', 'Consignación'),
    ]

    nombre_clinica = models.CharField(max_length=200, verbose_name='Nombre de la Clínica')
    rut_clinica = models.CharField(max_length=12, blank=True, verbose_name='RUT Clínica')
    contacto_nombre = models.CharField(max_length=200, verbose_name='Nombre del Contacto')
    contacto_email = models.EmailField(verbose_name='Email del Contacto')
    contacto_telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.TextField(blank=True, verbose_name='Dirección')
    ciudad = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    region = models.CharField(max_length=100, blank=True, verbose_name='Región')
    tipo_alianza = models.CharField(max_length=30, choices=OPCIONES_TIPO, default='contrato_suministro', verbose_name='Tipo de Alianza')
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='prospecto', verbose_name='Estado')
    descuento_acordado = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Descuento Acordado (%)')
    volumen_mensual_estimado = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Volumen Mensual Estimado (CLP)')
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name='Fecha de Inicio')
    fecha_fin = models.DateField(null=True, blank=True, verbose_name='Fecha de Fin')
    notas = models.TextField(blank=True, verbose_name='Notas Internas')
    creada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alianzas_creadas', verbose_name='Creada por')
    creada_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    actualizada_en = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Alianza Estratégica'
        verbose_name_plural = 'Alianzas Estratégicas'
        ordering = ['-creada_en']

    def __str__(self):
        return f"{self.nombre_clinica} — {self.get_tipo_alianza_display()} ({self.get_estado_display()})"


class Cotizacion(models.Model):
    """Cotización formal generada por un vendedor para una institución/clínica."""
    OPCIONES_ESTADO = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('vencida', 'Vencida'),
        ('convertida', 'Convertida a Pedido'),
    ]

    numero = models.CharField(max_length=20, unique=True, verbose_name='Nº Cotización')
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cotizaciones', verbose_name='Vendedor')
    # Cliente destino
    cliente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='cotizaciones_recibidas', verbose_name='Cliente / Institución')
    nombre_cliente = models.CharField(max_length=200, verbose_name='Nombre del Cliente')
    email_cliente = models.EmailField(verbose_name='Email del Cliente')
    telefono_cliente = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion_cliente = models.TextField(blank=True, verbose_name='Dirección')
    # Detalles comerciales
    estado = models.CharField(max_length=15, choices=OPCIONES_ESTADO, default='borrador', verbose_name='Estado')
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Descuento (%)')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Subtotal')
    descuento_monto = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Monto Descuento')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
    valida_hasta = models.DateField(verbose_name='Válida Hasta')
    notas = models.TextField(blank=True, verbose_name='Notas / Condiciones')
    pedido_generado = models.ForeignKey('pedidos.Pedido', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='cotizacion_origen', verbose_name='Pedido Generado')
    creada_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    actualizada_en = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-creada_en']

    def __str__(self):
        return f"COT-{self.numero} → {self.nombre_cliente} ({self.get_estado_display()})"

    def calcular_totales(self):
        """Recalcula subtotal, descuento y total basado en los items."""
        from django.db.models import Sum, F
        agg = self.items.aggregate(sub=Sum(F('cantidad') * F('precio_unitario')))
        self.subtotal = agg['sub'] or 0
        self.descuento_monto = self.subtotal * self.descuento_porcentaje / 100
        self.total = self.subtotal - self.descuento_monto
        self.save(update_fields=['subtotal', 'descuento_monto', 'total'])


class ItemCotizacion(models.Model):
    """Línea de producto dentro de una cotización."""
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='items', verbose_name='Cotización')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, verbose_name='Producto')
    cantidad = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Unitario')

    class Meta:
        verbose_name = 'Ítem de Cotización'
        verbose_name_plural = 'Ítems de Cotización'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} @ ${self.precio_unitario}"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class VisitaAsesoramiento(models.Model):
    """Registro de visita de asesoramiento técnico a una institución."""
    OPCIONES_TIPO = [
        ('visita_tecnica', 'Visita Técnica'),
        ('capacitacion', 'Capacitación'),
        ('demostracion', 'Demostración de Producto'),
        ('seguimiento', 'Seguimiento Comercial'),
        ('reclamo', 'Atención de Reclamo'),
    ]
    OPCIONES_RESULTADO = [
        ('exitosa', 'Exitosa'),
        ('pendiente', 'Pendiente de Seguimiento'),
        ('sin_interes', 'Sin Interés'),
        ('reprogramada', 'Reprogramada'),
    ]

    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visitas', verbose_name='Vendedor')
    nombre_institucion = models.CharField(max_length=200, verbose_name='Institución')
    contacto_nombre = models.CharField(max_length=200, verbose_name='Persona de Contacto')
    contacto_cargo = models.CharField(max_length=100, blank=True, verbose_name='Cargo')
    tipo = models.CharField(max_length=20, choices=OPCIONES_TIPO, default='visita_tecnica', verbose_name='Tipo de Visita')
    fecha_visita = models.DateField(verbose_name='Fecha de Visita')
    resultado = models.CharField(max_length=20, choices=OPCIONES_RESULTADO, default='exitosa', verbose_name='Resultado')
    productos_presentados = models.TextField(blank=True, verbose_name='Productos Presentados')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    proxima_accion = models.TextField(blank=True, verbose_name='Próxima Acción')
    fecha_seguimiento = models.DateField(null=True, blank=True, verbose_name='Fecha de Seguimiento')
    creada_en = models.DateTimeField(auto_now_add=True, verbose_name='Registrada el')

    class Meta:
        verbose_name = 'Visita de Asesoramiento'
        verbose_name_plural = 'Visitas de Asesoramiento'
        ordering = ['-fecha_visita']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.nombre_institucion} ({self.fecha_visita})"
