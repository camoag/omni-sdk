import pytest

from omni import OmniApiClient
from tests import omni_vcr


@pytest.fixture
def client():
    return OmniApiClient()


class TestClient:

    @omni_vcr.use_cassette()
    def test_refresh_model(self, client):
        assert client.refresh_model("b4dd2fbc-2b0c-4ae9-8f93-16a53f395514") is True
