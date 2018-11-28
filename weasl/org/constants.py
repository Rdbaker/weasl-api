from collections import namedtuple


Constant = namedtuple('OrgPropertyConstant', ['display_name', 'property_name', 'default'])


_COMPANY_NAME = Constant(display_name='Company Name', property_name='company_name', default=None)
_TEXT_LOGIN_MESSAGE = Constant(display_name='Text Login Message', property_name='text_login_message', default='Use this code to login')
_EMAIL_MAGICLINK = Constant(display_name='Email magiclink', property_name='email_magiclink', default=None)


_CONSTANTS = [
    _COMPANY_NAME,
    _TEXT_LOGIN_MESSAGE,
    _EMAIL_MAGICLINK,
]


class OrgPropertyConstants:
    COMPANY_NAME = _COMPANY_NAME
    TEXT_LOGIN_MESSAGE = _TEXT_LOGIN_MESSAGE
    EMAIL_MAGICLINK = _EMAIL_MAGICLINK

    @staticmethod
    def get_constant_by_name(property_name):
        """Returns the OrgPropertyConstant by property_name."""
        constant = [c for c in _CONSTANTS if c.property_name == property_name]
        if len(constant) == 0:
            return None
        else:
            return constant[0]

    @staticmethod
    def is_valid_property(property_name):
        """Returns true if the property is something we will take based on the white list."""
        return any([c.property_name == property_name for c in _CONSTANTS])