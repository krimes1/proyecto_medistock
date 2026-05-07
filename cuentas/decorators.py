"""Decoradores para control de acceso por rol."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def rol_requerido(*roles_permitidos):
    """Decorador que verifica que el usuario tenga uno de los roles permitidos."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if hasattr(request.user, 'perfil') and request.user.perfil.rol in roles_permitidos:
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:inicio')
        return wrapper
    return decorator
