"""Formularios para el módulo de Administración y Vendedor."""
from django import forms
from .models import AlianzaClinica, Cotizacion, VisitaAsesoramiento


class AlianzaClinicaForm(forms.ModelForm):
    """Formulario para crear/editar alianzas estratégicas."""
    class Meta:
        model = AlianzaClinica
        fields = [
            'nombre_clinica', 'rut_clinica', 'contacto_nombre', 'contacto_email',
            'contacto_telefono', 'direccion', 'ciudad', 'region',
            'tipo_alianza', 'estado', 'descuento_acordado',
            'volumen_mensual_estimado', 'fecha_inicio', 'fecha_fin', 'notas',
        ]
        widgets = {
            'nombre_clinica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Clínica Santa María'}),
            'rut_clinica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 76.000.000-0'}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contacto_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_alianza': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'descuento_acordado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'volumen_mensual_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ReporteFiltroForm(forms.Form):
    """Formulario para filtrar reportes por fecha."""
    fecha_desde = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False, label='Desde',
    )
    fecha_hasta = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False, label='Hasta',
    )


class CotizacionForm(forms.ModelForm):
    """Formulario para crear/editar cotizaciones."""
    class Meta:
        model = Cotizacion
        fields = [
            'nombre_cliente', 'email_cliente', 'telefono_cliente',
            'direccion_cliente', 'descuento_porcentaje', 'valida_hasta', 'notas',
        ]
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Clínica Las Condes'}),
            'email_cliente': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_cliente': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'descuento_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '50'}),
            'valida_hasta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Condiciones de pago, plazos de entrega, etc.'}),
        }


class VisitaForm(forms.ModelForm):
    """Formulario para registrar visitas de asesoramiento."""
    class Meta:
        model = VisitaAsesoramiento
        fields = [
            'nombre_institucion', 'contacto_nombre', 'contacto_cargo',
            'tipo', 'fecha_visita', 'resultado', 'productos_presentados',
            'observaciones', 'proxima_accion', 'fecha_seguimiento',
        ]
        widgets = {
            'nombre_institucion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Hospital del Salvador'}),
            'contacto_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'contacto_cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Jefe de Abastecimiento'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_visita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'resultado': forms.Select(attrs={'class': 'form-control'}),
            'productos_presentados': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Guantes quirúrgicos, mascarillas N95...'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proxima_accion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Enviar cotización por 5000 unidades'}),
            'fecha_seguimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
