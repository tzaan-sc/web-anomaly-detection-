"""Active Defense middleware."""
from datetime import datetime, timezone
from flask import g, abort

def check_active_defense():
    """Middleware to block requests if the user is locked."""
    if hasattr(g, 'current_user') and g.current_user is not None:
        if getattr(g.current_user, 'locked_until', None):
            if g.current_user.locked_until > datetime.now(timezone.utc):
                abort(403, "Tài khoản của bạn đã bị khóa tạm thời do phát hiện hành vi bất thường.")
