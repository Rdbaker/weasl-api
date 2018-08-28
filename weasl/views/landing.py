from datetime import datetime as dt
import uuid

from flask import Blueprint, render_template, request, make_response, flash, redirect, url_for, g

from weasl.forms.signup import SignupForm
from weasl.user.controller import auth_via_email
from weasl.user.models import EmailToken
from weasl.utils import login_required
from weasl.org.models import Org


blueprint = Blueprint('landing', __name__)

@blueprint.route('/')
def index():
    """The index for the whole website."""
    form = SignupForm(request.form)
    return render_template("landing.html", form=form)


@blueprint.route('/signup', methods=['POST'])
def register():
    form = SignupForm(request.form)
    if form.validate():
        if auth_via_email(form.email.data):
            flash('We sent you an email with a link to sign in')
    return render_template("landing.html", form=form)


@blueprint.route('/magiclink/<string:token>')
def login_via_magiclink(token):
    try:
        uuid_token = uuid.UUID(token)
    except:
        # TODO: redirect to failed login
        # raise BadRequest(Errors.BAD_GUID)
        return redirect(url_for('landing.index'))
    email_token = EmailToken.use(uuid_token)
    if email_token:
        current_user = email_token.user
        current_user.update(last_login_at=dt.utcnow())
        response = redirect(url_for('landing.welcome'))
        response.set_cookie('WEASL_AUTH', value=email_token.user.encode_auth_token().decode('utf-8'))
        return response
    else:
        # TODO: redirect to failed login
        # raise Unauthorized(Errors.BAD_TOKEN)
        return redirect(url_for('landing.index'))


@blueprint.route('/welcome')
@login_required
def welcome():
    # TODO: make this the "home" route
    org = Org.find(g.current_user.org_id)
    return render_template("welcome.html", client_id=org.client_id)