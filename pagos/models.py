from django.db import models


class Pago(models.Model):
    """Registro de pago asociado a un pedido. Integracion WebPay Plus."""
    OPCIONES_METODO = [
        ('webpay_credito', 'WebPay Credito'),
        ('webpay_debito', 'WebPay Debito'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    OPCIONES_ESTADO = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]

    pedido = models.OneToOneField('pedidos.Pedido', on_delete=models.CASCADE, related_name='pago', verbose_name='Pedido')
    metodo = models.CharField(max_length=20, choices=OPCIONES_METODO, verbose_name='Metodo de Pago')
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='pendiente', verbose_name='Estado')
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto')
    id_transaccion = models.CharField(max_length=100, blank=True, verbose_name='ID de Transaccion')
    codigo_autorizacion = models.CharField(max_length=50, blank=True, verbose_name='Codigo de Autorizacion')
    ultimos_cuatro = models.CharField(max_length=4, blank=True, verbose_name='Ultimos 4 digitos')
    confirmado_por = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='pagos_confirmados', verbose_name='Confirmado por')
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    completado_en = models.DateTimeField(null=True, blank=True, verbose_name='Completado el')

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-creado_en']

    def __str__(self):
        return f"Pago {self.id_transaccion or 'N/A'} - {self.get_estado_display()} - ${self.monto}"


class Boleta(models.Model):
    """Boleta electronica generada tras pago exitoso."""
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='boleta', verbose_name='Pago')
    numero_boleta = models.CharField(max_length=50, unique=True, verbose_name='Nro de Boleta')
    rut_emisor = models.CharField(max_length=12, default='76.000.000-0', verbose_name='RUT Emisor')
    rut_receptor = models.CharField(max_length=12, blank=True, verbose_name='RUT Receptor')
    monto_neto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto Neto')
    monto_iva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='IVA (19%)')
    monto_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Total')
    archivo_pdf = models.FileField(upload_to='boletas/', blank=True, null=True, verbose_name='PDF Boleta')
    emitida_en = models.DateTimeField(auto_now_add=True, verbose_name='Emitida el')

    class Meta:
        verbose_name = 'Boleta Electronica'
        verbose_name_plural = 'Boletas Electronicas'
        ordering = ['-emitida_en']

    def __str__(self):
        return f"Boleta Nro {self.numero_boleta}"
