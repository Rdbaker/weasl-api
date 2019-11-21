from flask import g, request, make_response, current_app
from functools import wraps, update_wrapper

from weasl.constants import Errors
from weasl.errors import Unauthorized, Forbidden, BadRequest
from weasl.end_user.models import EndUser
from weasl.org.models import Org


def friendly_arg_get(key, default=None, type_cast=None):
    """Same as request.args.get but returns default on ValueError."""
    try:
        return request.args.get(key, default=default, type=type_cast)
    except:
        return default


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


def end_user_as_weasl_user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise Unauthorized(Errors.LOGIN_REQUIRED)
        token = auth_header[7:]
        end_user = EndUser.from_token(token)
        if not end_user:
            raise Unauthorized(Errors.LOGIN_REQUIRED)
        # if end_user.org_id != 1:
        #     raise BadRequest(Errors.NOT_USER)

        g.end_user = end_user
        return f(*args, **kwargs)
    return decorated_function


def client_secret_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = get_request_secret_key()
        if not auth_header:
            raise Unauthorized(Errors.CLIENT_SECRET_REQUIRED)
        org = Org.from_client_secret(auth_header)
        if not org:
            raise Unauthorized(Errors.INVALID_CLIENT_SECRET)

        g.current_org = org
        return f(*args, **kwargs)
    return decorated_function


def client_id_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('X-Weasl-Client-Id')
        if not auth_header:
            raise Unauthorized(Errors.CLIENT_ID_REQUIRED)
        org = Org.from_client_id(auth_header)
        if not org:
            raise Unauthorized(Errors.INVALID_CLIENT_ID)

        g.current_org = org
        return f(*args, **kwargs)
    return decorated_function


def get_request_secret_key():
    header = request.headers.get('X-Weasl-Client-Secret')
    return header
