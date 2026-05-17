"""Vistas de autenticación, registro y perfil de usuario."""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FormularioLogin, FormularioRegistro, FormularioPerfil
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User


def vista_login(request):
    """Inicio de sesión segmentado por roles."""
    if request.user.is_authenticated:
        return redirect(_redireccion_por_rol(request.user))

    if request.method == 'POST':
        form = FormularioLogin(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bienvenido, {user.first_name or user.username}!')
            return redirect(_redireccion_por_rol(user))
        else:
            messages.error(request, 'Credenciales inválidas. Intente nuevamente.')
    else:
        form = FormularioLogin()

    return render(request, 'cuentas/login.html', {'form': form})


def vista_registro(request):
    """Registro de nuevos usuarios (pacientes e instituciones)."""
    if request.user.is_authenticated:
        return redirect('core:inicio')

    if request.method == 'POST':
        form = FormularioRegistro(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Requiere activación
            user.save()
            # Guardar el perfil que crea el formulario internamente (si aplica, form.save() ya lo maneja en el save de auth.User si es signal, pero nuestro form hace el save de auth user)
            form.save_m2m()
            
            # Enviar correo de activación
            current_site = get_current_site(request)
            subject = 'Activa tu cuenta en MediStock'
            message = render_to_string('cuentas/email_activacion.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, None, [user.email])
            
            messages.success(request, 'Cuenta creada. Por favor revisa tu correo para activar tu cuenta.')
            return redirect('cuentas:login')
    else:
        form = FormularioRegistro()

    return render(request, 'cuentas/registro.html', {'form': form})


def activar_cuenta(request, uidb64, token):
    """Vista para activar la cuenta mediante el enlace del correo."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, '¡Tu cuenta ha sido activada! Ahora puedes iniciar sesión.')
        return redirect('cuentas:login')
    else:
        messages.error(request, 'El enlace de activación es inválido o ha expirado.')
        return redirect('cuentas:login')


def vista_logout(request):
    """Cierre de sesión."""
    inactividad = request.GET.get('inactividad')
    logout(request)
    if inactividad:
        return redirect('/cuenta/login/?timeout=1')
    messages.info(request, 'Has cerrado sesión.')
    return redirect('core:inicio')


@login_required
def vista_perfil(request):
    """Perfil del usuario con edición de datos."""
    perfil = request.user.perfil
    if request.method == 'POST':
        form = FormularioPerfil(request.POST, instance=perfil)
        if form.is_valid():
            # Actualizar User
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('cuentas:perfil')
    else:
        form = FormularioPerfil(instance=perfil, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    return render(request, 'cuentas/perfil.html', {'form': form, 'perfil': perfil})


@login_required
def mis_pedidos(request):
    """Lista de pedidos del usuario."""
    pedidos = request.user.pedidos.all().order_by('-creado_en')
    return render(request, 'cuentas/mis_pedidos.html', {'pedidos': pedidos})


def _redireccion_por_rol(user):
    """Redirige al dashboard apropiado según el rol del usuario."""
    if hasattr(user, 'perfil'):
        rol = user.perfil.rol
        if rol == 'administrador':
            return 'dashboards:administrador'
        elif rol == 'ejecutivo':
            return 'dashboards:ejecutivo'
        elif rol == 'logistica':
            return 'dashboards:logistica'
        elif rol == 'analista':
            return 'dashboards:analista'
        elif rol == 'vendedor':
            return 'dashboards:vendedor'
    return 'core:inicio'
