import pytest

from omni import OmniDashboardEmbedder


@pytest.fixture
def embedder():
    return OmniDashboardEmbedder(organization_name="acme", embed_secret="super_secret")


@pytest.fixture(autouse=True)
def patch_uuid(monkeypatch):
    monkeypatch.setattr("uuid.UUID.hex", "365f7003aa5b4f3586d9b81b4a5d9f69")


class TestEmbed:
    def test_basic_url(self, embedder):
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
        )
        assert (
            url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=mToqUfdkmVSyDIGAl6Ggs9uAmGQAH9OzbbCZ-xgEU8c%3D"
        )

    def test_kitchen_sink(self, embedder):
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            custom_theme={
                "dashboard-background": "#00FF00",
                "dashboard-tile-background": "#00FF00",
            },
            entity="Acme",
            filter_search_params={"state": "GA"},
            link_access=True,
            prefers_dark=OmniDashboardEmbedder.PrefersDark.yes,
            theme=OmniDashboardEmbedder.Theme.dawn,
            user_attributes={"country": "USA"},
        )
        assert url == (
            "https://acme.embed-omniapp.co/embed/login?"
            "contentPath=%2Fdashboards%2Fda24491e"
            "&externalId=1"
            "&name=Somebody"
            "&nonce=365f7003aa5b4f3586d9b81b4a5d9f69"
            "&customTheme=%7B%22dashboard-background%22%3A%22%2300FF00%22%2C%22dashboard-tile-background%22%3A%22%2300FF00%22%7D"
            "&entity=Acme"
            "&filterSearchParam=state%3DGA"
            "&linkAccess=__omni_link_access_open"
            "&prefersDark=true"
            "&theme=dawn"
            "&userAttributes=%7B%22country%22%3A%22USA%22%7D"
            "&signature=Y8Alg2Sfdi5WdbwzU4QEugs3HdwLfEvXuBv8UU3BBZw%3D"
        )

    def test_link_access(self, embedder):
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            link_access=True,
        )
        assert (
            url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&linkAccess=__omni_link_access_open&signature=0-XD5eTE8myI7n2Taew-ADXmm3c_kYNCkQFHFkfOvqU%3D"
        )
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            link_access=["abcd1234", "efgh5678"],
        )
        assert (
            url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&linkAccess=abcd1234%2Cefgh5678&signature=rKpBYpOKIVQmCXNfhB7J8Z0WYnlELI5KmH4uPHc1048%3D"
        )

    def test_filter_search_params(self, embedder):
        str_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            filter_search_params="state=GA&county=Fulton",
        )
        dict_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            filter_search_params={"state": "GA", "county": "Fulton"},
        )
        assert (
            str_url
            == dict_url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&filterSearchParam=state%3DGA%26county%3DFulton&signature=ekzTS_BikwetRpIJK40t2V11YxKPMQ_YgaiN9b9GE9Y%3D"
        )

    def test_missing_organization_name(self):
        with pytest.raises(ValueError):
            OmniDashboardEmbedder(embed_secret="super_secret")

    def test_missing_embed_secret(self):
        with pytest.raises(ValueError):
            OmniDashboardEmbedder(organization_name="acme")

    def test_env_configuration(self, monkeypatch):
        monkeypatch.setenv("OMNI_ORGANIZATION_NAME", "acme")
        monkeypatch.setenv("OMNI_EMBED_SECRET", "super_secret")
        OmniDashboardEmbedder()
