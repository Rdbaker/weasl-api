"""API routes for users."""

from flask import Blueprint, jsonify, request, g

from weasl.user.models import SMSToken, User
from weasl.user.schema import UserSchema
from weasl.utils import login_required

blueprint = Blueprint('users', __name__, url_prefix='/users')

USER_SCHEMA = UserSchema()


@blueprint.route('/me', methods=['GET'])
@login_required
def get_me():
    return jsonify(data=USER_SCHEMA.dump(g.current_user)), 200
