# -*- encoding: utf-8 -*-
"""Test the views at /auth/email."""
import pytest

from weasl.user.models import SMSToken, User


@pytest.mark.usefixtures('db')
class TestSendSMS(object):
    """Test PUT|POST|PATCH /auth/email/send."""

    base_url = '/auth/sms/send'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_phone(self, testapp, method):
        """Test that we get a 400 if we don't give a phone number."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400)
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_user_created_if_new_phone(self, testapp, method):
        """Test that we create a new user if it's a new phone number."""
        old_count = User.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'phone_number': '5555555555'})
        assert old_count + 1 == User.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_user_not_created_if_known_phone(self, testapp, user, method):
        """Test that we don't create a new user if the phone number is already known."""
        old_count = User.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'phone_number': user.phone_number})
        assert old_count == User.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_token_created(self, testapp, user, method):
        """Test that we create a new token when requested."""
        old_count = SMSToken.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'phone_number': user.phone_number})
        assert old_count < SMSToken.query.count()


@pytest.mark.usefixtures('db')
class TestVerifySMS(object):
    """Test PUT|POST|PATCH /auth/sms/verify."""

    base_url = '/auth/sms/verify'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_token(self, testapp, method):
        """Test that we get a 400 if we don't give an sms token."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400)
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_unauthorized_with_unknown_token(self, testapp, method):
        """Test that we get a 401 if we send an unknown token."""
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': SMSToken.create_random_token()}, status=401)
        assert res.status_code == 401

    @pytest.mark.parametrize('method', methods)
    def test_get_jwt_with_good_token(self, testapp, user, method):
        """Test that we get a jwt with a good token."""
        sms_token = SMSToken.generate(user)
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': sms_token.token})
        assert res.status_code == 200
        assert 'JWT' in res.json

    @pytest.mark.parametrize('method', methods)
    def test_get_jwt_case_insensitive_token(self, testapp, user, method):
        """Test that we get a jwt with a case insentivie token."""
        sms_token = SMSToken.generate(user)
        if sms_token.token == sms_token.token.lower():
            other_token = sms_token.token.upper()
        else:
            other_token = sms_token.token.lower()
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': other_token})
        assert res.status_code == 200
        assert 'JWT' in res.json
