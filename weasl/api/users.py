"""API routes for users."""

from flask import Blueprint, jsonify, request, g

from weasl.user.models import SMSToken, User
from weasl.user.schema import UserSchema
from weasl.utils import login_required, admin_required

blueprint = Blueprint('users', __name__, url_prefix='/users')

USER_SCHEMA = UserSchema()


@blueprint.route('/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(data=USER_SCHEMA.dump(g.current_user)), 200


@blueprint.route('/<string:uid>/login-token', methods=['GET'])
@admin_required
def get_login_token(uid: str) -> str:
    user = User.find(uid)
    if user is None:
        raise NotFound(Errors.USER_NOT_FOUND)
    return user.encode_auth_token()
