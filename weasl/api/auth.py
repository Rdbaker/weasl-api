"""API routes for authentication."""
from datetime import datetime as dt
import uuid

from flask import Blueprint, jsonify, request
import pytz

from weasl.constants import Errors
from weasl.errors import BadRequest, Unauthorized
from weasl.user.models import EmailToken, SMSToken, User
from weasl.org.models import Org

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


@blueprint.route('/sms/verify', methods=['POST', 'PUT', 'PATCH'])
def verify_via_sms():
    if request.method == 'GET':
        token_string = request.args.get('token_string')
    else:
        token_string = request.json.get('token_string')
    if token_string is None:
        raise BadRequest(Errors.NO_TOKEN)
    sms_token = SMSToken.use(token_string)
    if sms_token:
        current_user = sms_token.user
        current_user.update(last_login_at=dt.utcnow().replace(tzinfo=pytz.utc))
        return jsonify({'JWT': sms_token.user.encode_auth_token().decode('utf-8')})
    else:
        raise Unauthorized(Errors.BAD_TOKEN)


@blueprint.route('/sms/send', methods=['POST', 'PUT', 'PATCH'])
def send_to_sms():
    phone_number = request.json.get('phone_number')
    if phone_number is None:
        raise BadRequest(Errors.PHONE_REQUIRED)
    user = User.query.filter(User.phone_number == phone_number).first()
    if user is None:
        # create a new user
        org = Org.generate_new()
        user = User.create(
            phone_number=phone_number,
            org_id=org.id,
            created_at=dt.utcnow().replace(tzinfo=pytz.utc),
            updated_at=dt.utcnow().replace(tzinfo=pytz.utc),
        )
    # create an SMS token and send it
    token = SMSToken.generate(user)
    token.send()
    return jsonify({'message': 'token successfully sent'}), 200


@blueprint.route('/email/verify', methods=['GET', 'POST', 'PUT', 'PATCH'])
def verify_via_email():
    if request.method == 'GET':
        token_string = request.args.get('token_string')
    else:
        token_string = request.json.get('token_string')
    if token_string is None:
        raise BadRequest(Errors.NO_TOKEN)
    try:
        uuid_token = uuid.UUID(token_string)
    except:
        raise BadRequest(Errors.BAD_GUID)
    email_token = EmailToken.use(uuid_token)
    if email_token:
        current_user = email_token.user
        current_user.update(last_login_at=dt.utcnow().replace(tzinfo=pytz.utc))
        return jsonify({'JWT': email_token.user.encode_auth_token().decode('utf-8')})
    else:
        raise Unauthorized(Errors.BAD_TOKEN)


@blueprint.route('/email/send', methods=['POST', 'PUT', 'PATCH'])
def send_to_email():
    email = request.json.get('email')
    if email is None:
        raise BadRequest(Errors.EMAIL_REQUIRED)
    user = User.query.filter(User.email == email).first()
    if user is None:
        # create a new user
        org = Org.generate_new()
        user = User.create(
            email=email,
            org_id=org.id,
            created_at=dt.utcnow().replace(tzinfo=pytz.utc),
            updated_at=dt.utcnow().replace(tzinfo=pytz.utc),
        )
    # create an email token and send it
    token = EmailToken.generate(user)
    token.send()
    return jsonify({'message': 'token successfully sent'}), 200
