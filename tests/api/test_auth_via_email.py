# -*- encoding: utf-8 -*-
"""Test the views at /auth/email."""
import uuid

import pytest

from noath.user.models import EmailToken, User


@pytest.mark.usefixtures('db')
class TestSendEmail(object):
    """Test PUT|POST|PATCH /auth/email/send."""

    base_url = '/auth/email/send'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_email(self, testapp, method):
        """Test that we get a 400 if we don't give an email."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400)
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_user_created_if_new_email(self, testapp, method):
        """Test that we create a new user if it's a new email."""
        old_count = User.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'email': 'test-email@noath.org'})
        assert old_count + 1 == User.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_user_not_created_if_known_email(self, testapp, user, method):
        """Test that we don't create a new user if the email is already known."""
        old_count = User.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'email': user.email})
        assert old_count == User.query.count()

    @pytest.mark.parametrize('method', methods)
    def test_token_created(self, testapp, user, method):
        """Test that we create a new token when requested."""
        old_count = EmailToken.query.count()
        func = getattr(testapp, method)
        func(self.base_url, {'email': user.email})
        assert old_count < EmailToken.query.count()


@pytest.mark.usefixtures('db')
class TestVerifyEmail(object):
    """Test PUT|POST|PATCH /auth/email/verify."""

    base_url = '/auth/email/verify'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_token(self, testapp, method):
        """Test that we get a 400 if we don't give an email token."""
        func = getattr(testapp, method)
        res = func(self.base_url, status=400)
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_with_invalid_token(self, testapp, method):
        """Test that we get a 400 if we send an invalid token."""
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': 'invalid-boy'}, status=400)
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_unauthorized_with_unknown_token(self, testapp, method):
        """Test that we get a 401 if we send an unknown token."""
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': uuid.uuid4().hex}, status=401)
        assert res.status_code == 401

    @pytest.mark.parametrize('method', methods)
    def test_get_jwt_with_good_token(self, testapp, user, method):
        """Test that we get a jwt with a good token."""
        email_token = EmailToken.generate(user)
        func = getattr(testapp, method)
        res = func(self.base_url, {'token_string': email_token.token.hex})
        assert res.status_code == 200
        assert 'JWT' in res.json
