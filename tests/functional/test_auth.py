# -*- encoding: utf-8 -*-
"""Test that authentication flows work."""
import uuid

import pytest

from weasl.end_user.models import EmailToken, SMSToken, EndUser


@pytest.mark.usefixtures('db')
class TestLoginWithEmail(object):
    """Test the flow of users logging in via email"""

    base_url = '/widget/email/{}'
    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_login_no_account(self, testapp, org, method):
        """Test that we can login without having an account"""
        func = getattr(testapp, method)
        # user sends email to /widget/email/send
        user_email = 'test@weasl.org'
        send_res = func(self.base_url.format('send'), {'email': user_email}, headers={'X-Weasl-Client-Id': org.client_id})
        assert send_res.status_code == 200

        # ...user goes to their inbox to get the token
        email_token = EmailToken.query.first()
        # make sure we got the right token
        assert email_token.end_user.email == user_email

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': email_token.token.hex}, headers={'X-Weasl-Client-Id': org.client_id})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json

    @pytest.mark.parametrize('method', methods)
    def test_login_with_account(self, testapp, end_user, org, method):
        """Test that we can login after creating an account"""
        func = getattr(testapp, method)
        # user sends email to /widget/email/send
        user_email = end_user.email
        send_res = func(self.base_url.format('send'), {'email': user_email}, headers={'X-Weasl-Client-Id': org.client_id})
        assert send_res.status_code == 200

        # ...user goes to their inbox to get the token
        email_token = EmailToken.query.first()
        # make sure we got the right token
        assert email_token.end_user.email == user_email

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': email_token.token.hex}, headers={'X-Weasl-Client-Id': org.client_id})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json


@pytest.mark.usefixtures('db')
class TestLoginWithSMS(object):
    """Test the flow of users logging in via sms"""

    base_url = '/widget/sms/{}'
    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_login_no_account(self, testapp, org, method):
        """Test that we can login without having an account"""
        func = getattr(testapp, method)
        # user sends phone number to /widget/sms/send
        user_phone = '5555555555'
        send_res = func(self.base_url.format('send'), {'phone_number': user_phone}, headers={'X-Weasl-Client-Id': org.client_id})
        assert send_res.status_code == 200

        # ...user goes to their messages to get the token
        sms_token = SMSToken.query.first()
        # make sure we got the right token
        assert sms_token.end_user.phone_number == user_phone

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': sms_token.token}, headers={'X-Weasl-Client-Id': org.client_id})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json

    @pytest.mark.parametrize('method', methods)
    def test_login_with_account(self, testapp, end_user, org, method):
        """Test that we can login after creating an account"""
        func = getattr(testapp, method)
        # user sends email to /auth/sms/send
        user_phone = end_user.phone_number
        send_res = func(self.base_url.format('send'), {'phone_number': user_phone}, headers={'X-Weasl-Client-Id': org.client_id})
        assert send_res.status_code == 200

        # ...user goes to their messages to get the token
        sms_token = SMSToken.query.first()
        # make sure we got the right token
        assert sms_token.end_user.phone_number == user_phone

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': sms_token.token}, headers={'X-Weasl-Client-Id': org.client_id})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json
