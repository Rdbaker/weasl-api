from flask import g, request
from functools import wraps

from noath.constants import Errors
from noath.errors import Unauthorized
from noath.user.models import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized(Errors.LOGIN_REQUIRED)
        token = auth_header[7:]
        current_user = User.from_token(token)
        if not current_user:
            raise Unauthorized(Errors.LOGIN_REQUIRED)

        g.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function
