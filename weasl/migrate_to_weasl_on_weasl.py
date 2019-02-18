from weasl.end_user.models import EndUser, EndUserPropertyTypes, EndUserProperty
from weasl.user.models import User

users=User.query.all()
master_org_id = 1

def create_new_end_user(user):
    try:
        return EndUser.create(org_id=master_org_id, email=user.email, phone_number=user.phone_number, created_at=user.created_at, last_login_at=user.last_login_at, updated_at=user.updated_at)
    except Exception as exc:
        print('could not create new end user from user', user, exc)
        EndUser.query.session.rollback()

def create_org_admin_pro_for_end_user(end_user, user):
    try:
        EndUserProperty.save_prop_for_end_user(end_user.id, 'org_id_as_admin', user.org_id, EndUserPropertyTypes.NUMBER, True)
    except Exception as exc:
        print('could not save org admin prop for end user', end_user, exc)
        EndUser.query.session.rollback()

def run_migration():
    for user in users:
        end_user = create_new_end_user(user)
        if end_user is not None:
            create_org_admin_pro_for_end_user(end_user, user)