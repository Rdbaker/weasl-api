from datetime import datetime as dt

from weasl.user.models import EmailToken, User
from weasl.org.models import Org


def auth_via_email(email):
    user = User.query.filter(User.email == email).first()
    if user is None:
        # create a new user
        org = Org.generate_new()
        user = User.create(
            email=email,
            org_id=org.id,
            created_at=dt.utcnow(),
            updated_at=dt.utcnow(),
        )
    # create an email token and send it
    token = EmailToken.generate(user)
    token.send()
    return True