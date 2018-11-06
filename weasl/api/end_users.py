"""API routes for end users."""
from datetime import datetime as dt
import uuid

from flask import Blueprint, jsonify, request, g, Response
import pytz
from sqlalchemy.exc import IntegrityError

from weasl.errors import BadRequest, Unauthorized
from weasl.end_user.models import SMSToken, EmailToken, EndUser, EndUserPropertyTypes, EndUserProperty
from weasl.end_user.schema import EndUserSchema
from weasl.utils import client_id_required, end_user_login_required, get_request_secret_key
from weasl.constants import Success, Errors

blueprint = Blueprint('end_users', __name__, url_prefix='/end_users')

END_USER_SCHEMA = EndUserSchema()


@blueprint.route('/me', methods=['GET'], strict_slashes=False)
@client_id_required
@end_user_login_required
def get_me():
    return jsonify(data=END_USER_SCHEMA.dump(g.end_user)), 200


@blueprint.route('', methods=['POST'], strict_slashes=False)
@client_id_required
def create_end_user():
    """Create an end user for the org."""
    end_user_data = END_USER_SCHEMA.load(request.json)
    end_user_data.update({
        'org_id': g.current_org.id,
        'created_at': dt.utcnow(),
        'updated_at': dt.utcnow(),
    })
    try:
        end_user = EndUser.create(**end_user_data)
    except IntegrityError as e:
        if 'email' in str(e):
            raise BadRequest(Errors.END_USER_DUPLICATE_EMAIL)
        else:
            raise BadRequest(Errors.END_USER_DUPLICATE_PHONE)
    return jsonify(data=END_USER_SCHEMA.dump(end_user),
                   message=Success.END_USER_CREATED), 201


@blueprint.route('/sms/verify', methods=['POST', 'PUT', 'PATCH'])
@client_id_required
def verify_via_sms():
    if request.method == 'GET':
        token_string = request.args.get('token_string')
    else:
        token_string = request.json.get('token_string')
    if token_string is None:
        raise BadRequest(Errors.NO_TOKEN)
    sms_token = SMSToken.use(token_string, g.current_org.id)
    if sms_token:
        end_user = sms_token.end_user
        end_user.update(last_login_at=dt.utcnow().replace(tzinfo=pytz.utc))
        return jsonify({'JWT': sms_token.end_user.encode_auth_token().decode('utf-8')})
    else:
        raise Unauthorized(Errors.BAD_TOKEN)


@blueprint.route('/sms/send', methods=['POST', 'PUT', 'PATCH'])
@client_id_required
def send_to_sms():
    phone_number = request.json.get('phone_number')
    if phone_number is None:
        raise BadRequest(Errors.PHONE_REQUIRED)
    end_user = EndUser.query.filter(
        EndUser.phone_number == phone_number,
        EndUser.org_id == g.current_org.id,
    ).first()
    if end_user is None:
        # create a new user
        end_user = EndUser.create(
            phone_number=phone_number,
            org_id=g.current_org.id,
            created_at=dt.utcnow(),
            updated_at=dt.utcnow(),
        )
    # create an SMS token and send it
    token = SMSToken.generate(end_user)
    token.send()
    return jsonify({'message': 'token successfully sent'}), 200


@blueprint.route('/email/verify', methods=['GET', 'POST', 'PUT', 'PATCH'])
@client_id_required
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
    email_token = EmailToken.use(uuid_token, g.current_org.id)
    if email_token:
        end_user = email_token.end_user
        end_user.update(last_login_at=dt.utcnow().replace(tzinfo=pytz.utc))
        return jsonify({'JWT': email_token.end_user.encode_auth_token().decode('utf-8')})
    else:
        raise Unauthorized(Errors.BAD_TOKEN)


@blueprint.route('/email/send', methods=['POST', 'PUT', 'PATCH'])
@client_id_required
def send_to_email():
    email = request.json.get('email')
    if email is None:
        raise BadRequest(Errors.EMAIL_REQUIRED)
    email = email.lower()
    end_user = EndUser.query.filter(
        EndUser.email == email,
        EndUser.org_id == g.current_org.id,
    ).first()
    if end_user is None:
        # create a new user
        end_user = EndUser.create(
            email=email,
            org_id=g.current_org.id,
            created_at=dt.utcnow(),
            updated_at=dt.utcnow(),
        )
    # create an email token and send it
    token = EmailToken.generate(end_user)
    token.send()
    return jsonify({'message': 'token successfully sent'}), 200


@blueprint.route('/attributes/<string:attribute_name>', methods=['POST', 'PATCH', 'PUT'])
@end_user_login_required
@client_id_required
def update_attributes(attribute_name):
    value = request.json.get('value')
    if value is None:
        raise BadRequest(Errors.ATTRIBUTE_VALUE_MISSING)
    attr_type = request.json.get('type')
    if attr_type is None:
        attr_type = EndUserPropertyTypes.STRING
    try:
        attr_type = EndUserPropertyTypes[attr_type]
    except KeyError:
        raise BadRequest(Errors.BAD_PROPERTY_TYPE)
    secret_key = get_request_secret_key()
    prop = EndUserProperty.query.get((g.end_user.id, attribute_name))
    if prop is not None:
        prop.update(
            property_type = attr_type,
            property_value = value,
            trusted = g.current_org.client_secret == secret_key,
        )
    else:
        EndUserProperty.create(
            end_user_id = g.end_user.id,
            property_type = attr_type,
            property_name = attribute_name,
            property_value = value,
            trusted = g.current_org.client_secret == secret_key,
        )
    return jsonify(data=END_USER_SCHEMA.dump(g.end_user)), 200


@blueprint.route('/<string:uid>/attributes/<string:attribute_name>', methods=['POST', 'PATCH', 'PUT'])
@client_secret_required
def update_attribute(uid, attribute_name):
    end_user = EndUser.find(uid)
    if end_user is None:
        raise NotFound(Errors.END_USER_NOT_FOUND)
    value = request.json.get('value')
    if value is None:
        raise BadRequest(Errors.ATTRIBUTE_VALUE_MISSING)
    attr_type = request.json.get('type')
    if attr_type is None:
        attr_type = EndUserPropertyTypes.STRING
    try:
        attr_type = EndUserPropertyTypes[attr_type]
    except KeyError:
        raise BadRequest(Errors.BAD_PROPERTY_TYPE)
    secret_key = get_request_secret_key()
    prop = EndUserProperty.query.get((end_user.id, attribute_name))
    if prop is not None:
        prop.update(
            property_type = attr_type,
            property_value = value,
            trusted = g.current_org.client_secret == secret_key,
        )
    else:
        EndUserProperty.create(
            end_user_id = end_user.id,
            property_type = attr_type,
            property_name = attribute_name,
            property_value = value,
            trusted = current_org.client_secret == secret_key,
        )
    return jsonify(data=END_USER_SCHEMA.dump(end_user)), 200