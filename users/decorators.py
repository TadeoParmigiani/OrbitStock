# decorators.py
from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth.models import AnonymousUser

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verificar si el usuario está autenticado
            if isinstance(request.user, AnonymousUser):
                return HttpResponseForbidden("Debes iniciar sesión para acceder a esta página")
            
            # Verificar si el rol del usuario coincide con el rol requerido
            if request.user.role != role:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
