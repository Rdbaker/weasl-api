from wtforms import Form, StringField, validators


class SettingsForm(Form):
    """A form for updating org settings."""
    company_name = StringField('Company or Project name', [validators.Length(min=5, max=100)])
    text_login_message = StringField('Text Login Message', [validators.Length(min=5, max=250)])