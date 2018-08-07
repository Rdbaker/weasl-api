from flask import Blueprint, render_template


blueprint = Blueprint('landing', __name__)

@blueprint.route('/')
def index():
    """The index for the whole website."""
    return render_template("landing.html")