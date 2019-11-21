from flask import Blueprint, render_template, request

from weasl.org.models import Org


blueprint = Blueprint('landing', __name__)


@blueprint.route('/')
def index():
    """The index for the whole website."""
    return render_template("landing2.html")


@blueprint.route('/privacy-policy')
def privacy_policy():
    return render_template("privacy.html")


@blueprint.route('/terms-of-service')
def tos():
    return render_template("tos.html")