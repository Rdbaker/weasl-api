from weasl.end_user.models import EndUser, EmailToken, SMSToken

def get_ordered_end_users_for_org(org_id):
    return EndUser.query.filter(EndUser.org_id == org_id).order_by(EndUser.last_login_at.desc()).all()