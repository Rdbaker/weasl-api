from uuid import uuid4

from flask import Blueprint, render_template


blueprint = Blueprint('email_preview', __name__, url_prefix='/email-preview')


@blueprint.route('/magiclink')
def magiclink():
    return render_template("emails/magiclink.html", magic_link_token=str(uuid4()))
