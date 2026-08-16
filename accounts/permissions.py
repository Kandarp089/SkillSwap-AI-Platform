from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def control_center_required(allowed_roles=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/accounts/login/?next=' + request.path)
            if not request.user.has_control_panel_access():
                messages.error(request, "Access denied. You do not have permissions for the Control Center.")
                raise PermissionDenied
            if allowed_roles:
                user_role = request.user.role
                if not request.user.is_superuser and user_role not in allowed_roles and user_role != 'SUPER_ADMIN':
                    messages.error(request, "Access denied for your role.")
                    raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
