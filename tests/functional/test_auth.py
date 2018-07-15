# -*- encoding: utf-8 -*-
"""Test that authentication flows work."""
import uuid

import pytest

from noath.user.models import EmailToken, SMSToken, User


@pytest.mark.usefixtures('db')
class TestLoginWithEmail(object):
    """Test the flow of users logging in via email"""

    base_url = '/auth/email/{}'
    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_login_no_account(self, testapp, method):
        """Test that we can login without having an account"""
        func = getattr(testapp, method)
        # user sends email to /auth/email/send
        user_email = 'test@noath.org'
        send_res = func(self.base_url.format('send'), {'email': user_email})
        assert send_res.status_code == 200

        # ...user goes to their inbox to get the token
        email_token = EmailToken.query.first()
        # make sure we got the right token
        assert email_token.user.email == user_email

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': email_token.token.hex})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json

    @pytest.mark.parametrize('method', methods)
    def test_login_with_account(self, testapp, user, method):
        """Test that we can login after creating an account"""
        func = getattr(testapp, method)
        # user sends email to /auth/email/send
        user_email = user.email
        send_res = func(self.base_url.format('send'), {'email': user_email})
        assert send_res.status_code == 200

        # ...user goes to their inbox to get the token
        email_token = EmailToken.query.first()
        # make sure we got the right token
        assert email_token.user.email == user_email

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': email_token.token.hex})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json


@pytest.mark.usefixtures('db')
class TestLoginWithSMS(object):
    """Test the flow of users logging in via sms"""

    base_url = '/auth/sms/{}'
    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_login_no_account(self, testapp, method):
        """Test that we can login without having an account"""
        func = getattr(testapp, method)
        # user sends phone number to /auth/sms/send
        user_phone = '5555555555'
        send_res = func(self.base_url.format('send'), {'phone_number': user_phone})
        assert send_res.status_code == 200

        # ...user goes to their messages to get the token
        sms_token = SMSToken.query.first()
        # make sure we got the right token
        assert sms_token.user.phone_number == user_phone

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': sms_token.token})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json

    @pytest.mark.parametrize('method', methods)
    def test_login_with_account(self, testapp, user, method):
        """Test that we can login after creating an account"""
        func = getattr(testapp, method)
        # user sends email to /auth/sms/send
        user_phone = user.phone_number
        send_res = func(self.base_url.format('send'), {'phone_number': user_phone})
        assert send_res.status_code == 200

        # ...user goes to their messages to get the token
        sms_token = SMSToken.query.first()
        # make sure we got the right token
        assert sms_token.user.phone_number == user_phone

        # user goes back to app to send token
        verify_res = func(self.base_url.format('verify'), {'token_string': sms_token.token})
        assert verify_res.status_code == 200
        assert 'JWT' in verify_res.json
