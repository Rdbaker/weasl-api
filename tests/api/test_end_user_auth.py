# -*- encoding: utf-8 -*-
"""Test the views at /auth/email."""
import uuid

import pytest

from weasl.end_user.models import SMSToken, EndUser, EmailToken


@pytest.mark.usefixtures('db')
class TestSendSMS(object):
    """Test PUT|POST|PATCH /widget/email/send."""

    base_url = '/widget/sms/send'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_phone(self, testapp, org, method):
        """Test that we get a 400 if we don't give a phone number."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_end_user_created_if_new_phone(self, testapp, org, method):
        """Test that we create a new end_user if it's a new phone number."""
        old_count = EndUser.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'phone_number': '5555555555'}, headers={'X-Weasl-Client-Id': org.client_id})
        assert old_count + 1 == EndUser.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_end_user_not_created_if_known_phone(self, testapp, end_user, org, method):
        """Test that we don't create a new end user if the phone number is already known."""
        old_count = EndUser.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'phone_number': end_user.phone_number}, headers={'X-Weasl-Client-Id': org.client_id})
        assert old_count == EndUser.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_token_created(self, testapp, end_user, org, method):
        """Test that we create a new token when requested."""
        old_count = SMSToken.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'phone_number': end_user.phone_number}, headers={'X-Weasl-Client-Id': org.client_id})
        assert old_count < SMSToken.query.count()


@pytest.mark.usefixtures('db')
class TestVerifySMS(object):
    """Test PUT|POST|PATCH /widget/sms/verify."""

    base_url = '/widget/sms/verify'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_token(self, testapp, org, method):
        """Test that we get a 400 if we don't give an sms token."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_unauthorized_with_unknown_token(self, testapp, org, method):
        """Test that we get a 401 if we send an unknown token."""
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': SMSToken.create_random_token()}, status=401, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 401

    @pytest.mark.parametrize('method', methods)
    def test_get_jwt_with_good_token(self, testapp, end_user, org, method):
        """Test that we get a jwt with a good token."""
        sms_token = SMSToken.generate(end_user)
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': sms_token.token}, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 200
        assert 'JWT' in res.json

    @pytest.mark.parametrize('method', methods)
    def test_get_jwt_case_insensitive_token(self, testapp, end_user, org, method):
        """Test that we get a jwt with a case insentivie token."""
        sms_token = SMSToken.generate(end_user)
        if sms_token.token == sms_token.token.lower():
            other_token = sms_token.token.upper()
        else:
            other_token = sms_token.token.lower()
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': other_token}, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 200
        assert 'JWT' in res.json



@pytest.mark.usefixtures('db')
class TestSendEmail(object):
    """Test PUT|POST|PATCH /widget/email/send."""

    base_url = '/widget/email/send'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_email(self, testapp, org, method):
        """Test that we get a 400 if we don't give an email."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_end_user_created_if_new_email(self, testapp, org, method):
        """Test that we create a new end_user if it's a new email."""
        old_count = EndUser.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'email': 'test-email@weasl.org'}, headers={'X-Weasl-Client-Id': org.client_id})
        assert old_count + 1 == EndUser.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_end_user_not_created_if_known_email(self, testapp, end_user, org, method):
        """Test that we don't create a new end_user if the email is already known."""
        old_count = EndUser.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'email': end_user.email}, headers={'X-Weasl-Client-Id': org.client_id})
        assert old_count == EndUser.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_token_created(self, testapp, end_user, org, method):
        """Test that we create a new token when requested."""
        old_count = EmailToken.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'email': end_user.email}, headers={'X-Weasl-Client-Id': org.client_id})
        assert old_count < EmailToken.query.count()


@pytest.mark.usefixtures('db')
class TestVerifyEmail(object):
    """Test PUT|POST|PATCH /widget/email/verify."""

    base_url = '/widget/email/verify'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_token(self, testapp, org, method):
        """Test that we get a 400 if we don't give an email token."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_with_invalid_token(self, testapp, org, method):
        """Test that we get a 400 if we send an invalid token."""
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': 'invalid-boy'}, status=400, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_unauthorized_with_unknown_token(self, testapp, org, method):
        """Test that we get a 401 if we send an unknown token."""
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': uuid.uuid4().hex}, status=401, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 401

    @pytest.mark.parametrize('method', methods)
    def test_get_jwt_with_good_token(self, testapp, end_user, org, method):
        """Test that we get a jwt with a good token."""
        email_token = EmailToken.generate(end_user)
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': email_token.token.hex}, headers={'X-Weasl-Client-Id': org.client_id})
        assert res.status_code == 200
        assert 'JWT' in res.json
