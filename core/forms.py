"""Formularios para el módulo de Administración."""
from django import forms
from .models import AlianzaClinica


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
