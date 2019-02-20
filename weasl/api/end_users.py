"""API routes for end users."""
from datetime import datetime as dt

from flask import Blueprint, jsonify, request, g

from weasl.errors import BadRequest, Unauthorized
from weasl.end_user.models import SMSToken, EmailToken, EndUser, EndUserPropertyTypes, EndUserProperty
from weasl.end_user.schema import EndUserSchema, SMSTokenSchema, EmailTokenSchema
from weasl.utils import get_request_secret_key, client_secret_required, client_id_required, friendly_arg_get, end_user_as_weasl_user_required, end_user_login_required
from weasl.constants import Errors

blueprint = Blueprint('end_users', __name__, url_prefix='/end_users')

END_USER_SCHEMA = EndUserSchema()
SMS_TOKEN_SCHEMA = SMSTokenSchema()
EMAIL_TOKEN_SCHEMA = EmailTokenSchema()


@blueprint.route('/me', methods=['GET'], strict_slashes=False)
@client_id_required
@end_user_login_required
def get_me():
    return jsonify(data=END_USER_SCHEMA.dump(g.end_user)), 200


@blueprint.route('/email-logins', methods=['GET'], strict_slashes=False)
@end_user_as_weasl_user_required
def list_end_user_email_logins():
    page_num = friendly_arg_get('page', 1, int)
    per_page = friendly_arg_get('per_page', 10, int)

    # TODO: allow ordering
    org = g.end_user.org_for_admin()
    page = EmailToken.query.filter(EmailToken.org_id==org.id).paginate(page=page_num, per_page=per_page)

    meta_pagination = {
        'first': request.path + '?page={page}&per_page={per_page}'.format(
            page=1, per_page=page.per_page),
        'next': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.next_num, per_page=page.per_page),
        'last': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.pages or 1, per_page=page.per_page),
        'prev': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.prev_num, per_page=page.per_page),
        'total': page.pages
    }

    if not page.has_next:
        meta_pagination.pop('next')
    if not page.has_prev:
        meta_pagination.pop('prev')

    return jsonify(data=EMAIL_TOKEN_SCHEMA.dump(page.items, many=True),
                   meta={'pagination': meta_pagination})



@blueprint.route('/sms-logins', methods=['GET'], strict_slashes=False)
@end_user_as_weasl_user_required
def list_end_user_sms_logins():
    page_num = friendly_arg_get('page', 1, int)
    per_page = friendly_arg_get('per_page', 10, int)

    # TODO: allow ordering
    org = g.end_user.org_for_admin()
    page = SMSToken.query.filter(SMSToken.org_id==org.id).paginate(page=page_num, per_page=per_page)

    meta_pagination = {
        'first': request.path + '?page={page}&per_page={per_page}'.format(
            page=1, per_page=page.per_page),
        'next': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.next_num, per_page=page.per_page),
        'last': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.pages or 1, per_page=page.per_page),
        'prev': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.prev_num, per_page=page.per_page),
        'total': page.pages
    }

    if not page.has_next:
        meta_pagination.pop('next')
    if not page.has_prev:
        meta_pagination.pop('prev')

    return jsonify(data=SMS_TOKEN_SCHEMA.dump(page.items, many=True),
                   meta={'pagination': meta_pagination})


@blueprint.route('', methods=['GET'], strict_slashes=False)
@end_user_as_weasl_user_required
def list_my_end_users():
    page_num = friendly_arg_get('page', 1, int)
    per_page = friendly_arg_get('per_page', 10, int)

    # TODO: allow ordering
    org = g.end_user.org_for_admin()
    page = EndUser.query.filter(EndUser.org_id==org.id).paginate(page=page_num, per_page=per_page)

    meta_pagination = {
        'first': request.path + '?page={page}&per_page={per_page}'.format(
            page=1, per_page=page.per_page),
        'next': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.next_num, per_page=page.per_page),
        'last': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.pages or 1, per_page=page.per_page),
        'prev': request.path + '?page={page}&per_page={per_page}'.format(
            page=page.prev_num, per_page=page.per_page),
        'total': page.pages
    }

    if not page.has_next:
        meta_pagination.pop('next')
    if not page.has_prev:
        meta_pagination.pop('prev')

    return jsonify(data=END_USER_SCHEMA.dump(page.items, many=True),
                   meta={'pagination': meta_pagination})


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
            trusted = g.current_org.client_secret == secret_key,
        )
    return jsonify(data=END_USER_SCHEMA.dump(end_user)), 200