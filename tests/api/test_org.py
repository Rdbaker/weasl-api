# -*- encoding: utf-8 -*-
"""Test the views at /auth/email."""
import pytest


@pytest.mark.usefixtures('db')
class TestOrgThemeUpdate(object):
    """Test PUT|POST|PATCH /orgs/theme/<property_name>."""

    base_url = '/orgs/theme/{}'

    methods = ['post_json', 'put_json', 'patch_json']

    @pytest.mark.parametrize('method', methods)
    def test_bad_response_without_login(self, testapp, method):
        """Test that we get a 401 if we aren't logged in."""
        func = getattr(testapp, method)
        res = func(self.base_url.format('company_name'), status=401)
        assert res.status_code == 401

    @pytest.mark.parametrize('method', methods)
    def test_prop_create_bad_type(self, testapp, end_user_as_weasl_user, method):
        """Test that we get a 400 if we give a bad type."""
        token = end_user_as_weasl_user.encode_auth_token().decode('utf-8')
        func = getattr(testapp, method)
        res = func(self.base_url.format('company_name'), {'type': 'INVALID'}, status=400, headers={'Authorization': 'Bearer {}'.format(token)})
        assert res.status_code == 400

    @pytest.mark.parametrize('method', methods)
    def test_prop_created_if_acceptable(self, testapp, end_user_as_weasl_user, method):
        """Test that we create a new org prop if it's valid."""
        token = end_user_as_weasl_user.encode_auth_token().decode('utf-8')
        func = getattr(testapp, method)
        func(self.base_url.format('company_name'), {'value': 'my company name', 'type': 'STRING'}, headers={'Authorization': 'Bearer {}'.format(token)})
