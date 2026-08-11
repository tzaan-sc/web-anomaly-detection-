"""Active Defense middleware."""
from datetime import datetime, timezone
from flask import g, abort

def check_active_defense():
    """Middleware to block requests if the user is locked."""
    if hasattr(g, 'current_user') and g.current_user is not None:
        if getattr(g.current_user, 'locked_until', None):
            locked_until = g.current_user.locked_until
            # Chuẩn hóa: nếu locked_until không có timezone thì gắn UTC vào
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if locked_until > datetime.now(timezone.utc):
                abort(403, "Tài khoản của bạn đã bị khóa tạm thời do phát hiện hành vi bất thường.")
