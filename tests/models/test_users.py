import pytest

from noath.user.models import User


@pytest.mark.usefixtures('db')
class TestUser:

    def test_encode_token(self, user):
        auth_token = user.encode_auth_token()
        assert isinstance(auth_token, bytes)

    def test_decode_token(self, user):
        auth_token = user.encode_auth_token()
        assert isinstance(auth_token, bytes)
        assert User.decode_auth_token(auth_token) == str(user.id)
