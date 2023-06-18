import pytest
import io
from authentication import SSHAuthenticator

@pytest.fixture
def test_authenticator():
    host = "185.231.233.25"
    port = 22
    username = "root"
    private_key = "tests/keys/id_rsa"

    return SSHAuthenticator(host, port, username, private_key=private_key)

def test_enter_with_key_auth(test_authenticator):
    test_authenticator.private_key = "tests/keys/id_rsa"
    
    authenticator = SSHAuthenticator(
        test_authenticator.host,
        test_authenticator.port,
        test_authenticator.username,
        private_key = test_authenticator.private_key
    )

    with authenticator as client:
        assert authenticator.client is not None
        assert client is authenticator.client

def test_exit(test_authenticator):
    test_authenticator.client = None
   
