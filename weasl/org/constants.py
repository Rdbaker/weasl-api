from collections import namedtuple


Constant = namedtuple('OrgPropertyConstant', ['display_name', 'property_name', 'default'])


class OrgPropertyConstants:
    COMPANY_NAME = Constant(display_name='Company Name', property_name='company_name', default=None)
    TEXT_LOGIN_MESSAGE = Constant(display_name='Text Login Message', property_name='text_login_message', default='Use this code to login')