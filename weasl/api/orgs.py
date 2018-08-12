"""API routes for orgs."""

from flask import Blueprint, jsonify, request, g

from weasl.org.models import Org
from weasl.org.schema import OrgSchema
from weasl.utils import login_required, client_id_required

blueprint = Blueprint('orgs', __name__, url_prefix='/orgs')

ORG_SCHEMA = OrgSchema()
PUBLIC_ORG_SCHEMA = OrgSchema(exclude=OrgSchema.private_fields)


@blueprint.route('/public', methods=['GET'])
@client_id_required
def get_public_org():
    # TODO: figure out what "public data" is
    return jsonify(data=PUBLIC_ORG_SCHEMA.dump(g.current_org)), 200

@blueprint.route('/me', methods=['GET'])
@login_required
def get_my_org():
    org = Org.find(g.current_user.org_id)
    return jsonify(data=ORG_SCHEMA.dump(org)), 200
