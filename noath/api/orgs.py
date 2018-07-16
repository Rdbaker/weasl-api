"""API routes for orgs."""

from flask import Blueprint, jsonify, request, g

from noath.org.models import Org
from noath.org.schema import OrgSchema
from noath.utils import login_required

blueprint = Blueprint('orgs', __name__, url_prefix='/orgs')

ORG_SCHEMA = OrgSchema()


@blueprint.route('/me', methods=['GET'])
@login_required
def get_my_org():
    org = Org.find(g.current_user.org_id)
    return jsonify(data=ORG_SCHEMA.dump(org)), 200
