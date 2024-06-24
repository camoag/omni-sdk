import pytest

from omni import OmniApiClient
from tests import omni_vcr


@pytest.fixture
def client():
    return OmniApiClient()


class TestClient:

    @omni_vcr.use_cassette()
    def test_refresh_model(self, client):
        assert client.refresh_model("f7390eb8-329a-460b-9ced-cb603e160558") is True
