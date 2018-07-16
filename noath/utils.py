from flask import g, request
from functools import wraps

from noath.constants import Errors
from noath.errors import Unauthorized
from noath.user.models import User
from noath.end_user.models import EndUser
from noath.org.models import Org


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


def end_user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized(Errors.LOGIN_REQUIRED)
        token = auth_header[7:]
        end_user = EndUser.from_token(token)
        if not end_user:
            raise Unauthorized(Errors.LOGIN_REQUIRED)

        g.end_user = end_user
        return f(*args, **kwargs)
    return decorated_function


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized(Errors.API_KEY_REQUIRED)
        api_key = auth_header[7:]
        org = Org.from_api_key(api_key)
        if not org:
            raise Unauthorized(Errors.INVALID_API_KEY)

        g.current_org = org
        return f(*args, **kwargs)
    return decorated_function