import pytest

from omni import OmniApiClient
from tests import omni_vcr


@pytest.fixture
def client():
    return OmniApiClient(organization_name="test", api_key="secret_token")


class TestClient:

    @omni_vcr.use_cassette()
    def test_refresh_model(self, client):
        assert client.refresh_model("b4dd2fbc-2b0c-4ae9-8f93-16a53f395514") is True

    def test_env_configuration(self, monkeypatch):
        monkeypatch.setenv("OMNI_ORGANIZATION_NAME", "acme")
        monkeypatch.setenv("OMNI_API_KEY", "api_key_1")
        client = OmniApiClient()
        assert client.api_key == "api_key_1"
        assert client.base_url == "https://acme.omniapp.co/api"
