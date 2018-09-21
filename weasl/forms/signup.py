from wtforms import Form, StringField, validators


class SignupForm(Form):
    """A form for signing up."""
    email = StringField('Email Address', [validators.Length(min=5, max=100)], render_kw={'placeholder': 'email@example.com'})