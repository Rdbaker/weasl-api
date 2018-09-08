from datetime import datetime as dt
import uuid

from flask import Blueprint, render_template, request, make_response, flash, redirect, url_for, g

from weasl.forms.settings import SettingsForm
from weasl.user.controller import auth_via_email
from weasl.user.models import EmailToken
from weasl.end_user.controller import get_ordered_end_users_for_org
from weasl.utils import login_required
from weasl.org.models import Org, OrgProperty, OrgPropertyNamespaces
from weasl.org.constants import OrgPropertyConstants


blueprint = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@blueprint.route('/')
@login_required
def index():
    """The index for the dashboard."""
    org = Org.find(g.current_user.org_id)
    return render_template('dashboard/index.html', client_id=org.client_id)


@blueprint.route('/activity')
@login_required
def activity():
    """The index for the dashboard."""
    return render_template('dashboard/coming-soon.html', page='activity', description='see all logins that happen on your website')


@blueprint.route('/users')
@login_required
def users():
    """The index for the dashboard."""
    return render_template(
        'dashboard/users.html',
        ordered_users=get_ordered_end_users_for_org(g.current_user.org_id)
    )


@blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """The index for the dashboard."""
    if request.method == 'GET':
        form = SettingsForm(
            company_name=OrgProperty.get_for_org_with_default(g.current_user.org_id, OrgPropertyConstants.COMPANY_NAME),
            text_login_message=OrgProperty.get_for_org_with_default(g.current_user.org_id, OrgPropertyConstants.TEXT_LOGIN_MESSAGE),
            email_magiclink=OrgProperty.get_for_org_with_default(g.current_user.org_id, OrgPropertyConstants.EMAIL_MAGICLINK),
        )
    else:
        form = SettingsForm(request.form)
        if form.validate():
            OrgProperty.save_prop_for_org(
                g.current_user.org_id,
                OrgPropertyConstants.COMPANY_NAME,
                value=form.company_name.data,
                namespace=OrgPropertyNamespaces.THEME,
            )
            OrgProperty.save_prop_for_org(
                g.current_user.org_id,
                OrgPropertyConstants.TEXT_LOGIN_MESSAGE,
                value=form.text_login_message.data,
                namespace=OrgPropertyNamespaces.THEME,
            )
            OrgProperty.save_prop_for_org(
                g.current_user.org_id,
                OrgPropertyConstants.EMAIL_MAGICLINK,
                value=form.email_magiclink.data,
                namespace=OrgPropertyNamespaces.THEME,
            )

    return render_template('dashboard/settings.html', form=form)
