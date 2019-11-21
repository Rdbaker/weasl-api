import pytest

from weasl.end_user.models import EndUser


@pytest.mark.usefixtures('db')
class TestEndUser:

    def test_encode_token(self, end_user):
        auth_token = end_user.encode_auth_token()
        assert isinstance(auth_token, bytes)

    def test_decode_token(self, end_user):
        auth_token = end_user.encode_auth_token()
        assert isinstance(auth_token, bytes)
        assert EndUser.decode_auth_token(auth_token) == str(end_user.id)
