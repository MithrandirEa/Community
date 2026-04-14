from functools import wraps

from flask import redirect, session, url_for


def require_role(*roles):
    """
    Décorateur de protection des routes par rôle.

    Usage : @require_role('officiel') ou @require_role('admin')
    Redirige vers /login si le rôle de session ne correspond pas.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') not in roles:
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
