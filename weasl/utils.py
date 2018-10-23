from flask import g, request, make_response, current_app
from functools import wraps, update_wrapper

from weasl.constants import Errors
from weasl.errors import Unauthorized
from weasl.user.models import User
from weasl.end_user.models import EndUser
from weasl.org.models import Org


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        cookie_session = request.cookies.get('WEASL_AUTH')
        if auth_header:
            token = auth_header[7:]
        elif cookie_session:
            token = cookie_session
        else:
            raise Unauthorized(Errors.LOGIN_REQUIRED)
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
