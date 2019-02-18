"""API routes for orgs."""

from flask import Blueprint, jsonify, request, g

from weasl.constants import Success, Errors
from weasl.end_user.models import EndUserPropertyTypes, EndUserProperty
from weasl.errors import BadRequest, Forbidden
from weasl.org.models import Org, OrgPropertyTypes, OrgPropertyNamespaces, OrgProperty
from weasl.org.schema import OrgSchema
from weasl.org.constants import Constant
from weasl.utils import login_required, client_id_required, end_user_as_weasl_user_required

blueprint = Blueprint('orgs', __name__, url_prefix='/orgs')

ORG_SCHEMA = OrgSchema()
PUBLIC_ORG_SCHEMA = OrgSchema(exclude=OrgSchema.private_fields)


@blueprint.route('/me', methods=['GET'])
@end_user_as_weasl_user_required
def get_my_org():
    org = g.end_user.org_for_admin()
    if org is None:
        org = Org.generate_new()
        EndUserProperty.save_prop_for_end_user(
            g.end_user.id,
            'org_id_as_admin',
            org.id,
            EndUserPropertyTypes.NUMBER,
            True
        )
    return jsonify(data=ORG_SCHEMA.dump(org)), 200


@blueprint.route('/theme/<string:property_name>', methods=['PUT', 'POST', 'PATCH'])
@end_user_as_weasl_user_required
def update_theme(property_name: str):
    value = request.json.get('value')
    if value is None:
        raise BadRequest(Errors.ATTRIBUTE_VALUE_MISSING)

    prop_type = request.json.get('type')
    if prop_type is None:
        prop_type = OrgPropertyTypes.STRING
    else:
        try:
            prop_type = OrgPropertyTypes[prop_type]
        except KeyError:
            raise BadRequest(Errors.BAD_PROPERTY_TYPE)

    org = g.end_user.org_for_admin()
    OrgProperty.save_prop_for_org(
        org.id,
        Constant(property_name=property_name, display_name=None, default=None),
        value=value,
        namespace=OrgPropertyNamespaces.THEME,
        prop_type=prop_type
    )

    return jsonify(data=ORG_SCHEMA.dump(org)), 200


@blueprint.route('/settings/<string:property_name>', methods=['PUT', 'POST', 'PATCH'])
@end_user_as_weasl_user_required
def update_integration(property_name: str):
    value = request.json.get('value')
    if value is None:
        raise BadRequest(Errors.ATTRIBUTE_VALUE_MISSING)

    prop_type = request.json.get('type')
    if prop_type is None:
        prop_type = OrgPropertyTypes.STRING
    else:
        try:
            prop_type = OrgPropertyTypes[prop_type]
        except KeyError:
            raise BadRequest(Errors.BAD_PROPERTY_TYPE)

    org = g.end_user.org_for_admin()
    OrgProperty.save_prop_for_org(
        org.id,
        Constant(property_name=property_name, display_name=None, default=None),
        value=value,
        namespace=OrgPropertyNamespaces.SETTINGS,
        prop_type=prop_type
    )

    return jsonify(data=ORG_SCHEMA.dump(org)), 200


@blueprint.route('<int:org_id>/gates/<string:gate_name>', methods=['PUT', 'POST', 'PATCH'])
@login_required
def update_gate(org_id: int, gate_name: str):
    if not g.current_user.is_admin:
        raise Forbidden(Errors.NOT_ADMIN)

    value = request.json.get('value')
    if value is None:
        raise BadRequest(Errors.ATTRIBUTE_VALUE_MISSING)

    OrgProperty.save_prop_for_org(
        org_id,
        Constant(property_name=gate_name, display_name=None, default=None),
        value=(value in ['true', 'True', True]),
        namespace=OrgPropertyNamespaces.GATES,
        prop_type=OrgPropertyTypes.BOOLEAN,
    )

    org = Org.find(org_id)
    return jsonify(data=ORG_SCHEMA.dump(org)), 200