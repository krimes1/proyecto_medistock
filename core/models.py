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
