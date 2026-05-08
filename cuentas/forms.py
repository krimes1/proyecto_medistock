"""Formularios de autenticación y perfil."""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import PerfilUsuario


class FormularioLogin(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o email'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )


class FormularioRegistro(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repetir contraseña'})
    )
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            user.perfil.rol = 'paciente'
            user.perfil.save()
        return user


REGIONES_CHILE = [
    ('', 'Seleccione una región...'),
    ('Arica y Parinacota', 'Arica y Parinacota'),
    ('Tarapacá', 'Tarapacá'),
    ('Antofagasta', 'Antofagasta'),
    ('Atacama', 'Atacama'),
    ('Coquimbo', 'Coquimbo'),
    ('Valparaíso', 'Valparaíso'),
    ('Metropolitana de Santiago', 'Metropolitana de Santiago'),
    ('O\'Higgins', 'O\'Higgins'),
    ('Maule', 'Maule'),
    ('Ñuble', 'Ñuble'),
    ('Biobío', 'Biobío'),
    ('La Araucanía', 'La Araucanía'),
    ('Los Ríos', 'Los Ríos'),
    ('Los Lagos', 'Los Lagos'),
    ('Aysén', 'Aysén'),
    ('Magallanes', 'Magallanes'),
]

CIUDADES_CHILE = [
    ('', 'Seleccione una ciudad...'),
    ('Arica', 'Arica'),
    ('Iquique', 'Iquique'),
    ('Antofagasta', 'Antofagasta'),
    ('Copiapó', 'Copiapó'),
    ('La Serena', 'La Serena'),
    ('Coquimbo', 'Coquimbo'),
    ('Valparaíso', 'Valparaíso'),
    ('Viña del Mar', 'Viña del Mar'),
    ('Santiago', 'Santiago'),
    ('Providencia', 'Providencia'),
    ('Maipú', 'Maipú'),
    ('Puente Alto', 'Puente Alto'),
    ('Rancagua', 'Rancagua'),
    ('Talca', 'Talca'),
    ('Chillán', 'Chillán'),
    ('Concepción', 'Concepción'),
    ('Temuco', 'Temuco'),
    ('Valdivia', 'Valdivia'),
    ('Puerto Montt', 'Puerto Montt'),
    ('Punta Arenas', 'Punta Arenas'),
]

class FormularioPerfil(forms.ModelForm):
    first_name = forms.CharField(
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PerfilUsuario
        fields = ['rut', 'telefono', 'direccion', 'ciudad', 'region', 'razon_social', 'rut_empresa']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ciudad': forms.Select(choices=CIUDADES_CHILE, attrs={'class': 'form-control'}),
            'region': forms.Select(choices=REGIONES_CHILE, attrs={'class': 'form-control'}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'rut_empresa': forms.TextInput(attrs={'class': 'form-control'}),
        }
