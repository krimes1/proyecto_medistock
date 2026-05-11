from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """Perfil extendido del usuario con roles segmentados."""
    OPCIONES_ROL = [
        ('administrador', 'Administrador'),
        ('ejecutivo', 'Ejecutivo de Cuentas'),
        ('logistica', 'Operador Logistico'),
        ('analista', 'Analista de Finanzas'),
        ('vendedor', 'Vendedor de Insumos'),
        ('institucion', 'Institucion / Clinica'),
        ('paciente', 'Paciente'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='Usuario')
    rol = models.CharField(max_length=20, choices=OPCIONES_ROL, default='paciente', verbose_name='Rol')
    rut = models.CharField(max_length=12, blank=True, verbose_name='RUT')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono')
    direccion = models.TextField(blank=True, verbose_name='Direccion')
    ciudad = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    region = models.CharField(max_length=100, blank=True, verbose_name='Region')
    # Campos B2B (solo instituciones)
    razon_social = models.CharField(max_length=200, blank=True, verbose_name='Razon Social')
    rut_empresa = models.CharField(max_length=12, blank=True, verbose_name='RUT Empresa')
    # Campo para el Vendedor
    codigo_vendedor = models.CharField(max_length=20, blank=True, unique=True, null=True, verbose_name='Codigo de Vendedor')

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.get_rol_display()}"

    @property
    def es_interno(self):
        return self.rol in ('administrador', 'ejecutivo', 'logistica', 'analista', 'vendedor')

    @property
    def es_cliente(self):
        return self.rol in ('institucion', 'paciente')


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        # Auto-generar codigo si es vendedor y no tiene
        if instance.perfil.rol == 'vendedor' and not instance.perfil.codigo_vendedor:
            import random
            import string
            base = instance.username[:4].upper()
            aleatorio = ''.join(random.choices(string.digits, k=4))
            instance.perfil.codigo_vendedor = f"VEN-{base}-{aleatorio}"
        instance.perfil.save()
