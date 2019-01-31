from wtforms import Form, StringField, validators
from wtforms.validators import ValidationError
from validate_email import validate_email


def check_email(form, field):
    if not validate_email(field.data):
        raise ValidationError('That is not a valid email')

class SignupForm(Form):
    """A form for signing up."""
    email = StringField('Email Address', [validators.Length(min=5, max=100), check_email], render_kw={'placeholder': 'email@example.com'})