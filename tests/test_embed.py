import pytest

from omni import OmniDashboardEmbedder
from omni.config import OmniConfigError
from omni.embed import OmniFilterDefinition, OmniFilterSet


@pytest.fixture
def embedder():
    return OmniDashboardEmbedder(organization_name="acme", embed_secret="super_secret")


@pytest.fixture
def vanity_domain_embedder():
    return OmniDashboardEmbedder(
        vanity_domain="foo.example.com", embed_secret="super_secret"
    )


@pytest.fixture(autouse=True)
def patch_uuid(monkeypatch):
    monkeypatch.setattr("uuid.UUID.hex", "365f7003aa5b4f3586d9b81b4a5d9f69")


class TestUnit:
    def test_basic_url(self, embedder, vanity_domain_embedder):
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
        )
        assert (
            url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=mToqUfdkmVSyDIGAl6Ggs9uAmGQAH9OzbbCZ-xgEU8c%3D"
        )

        url = vanity_domain_embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
        )
        assert (
            url
            == "https://foo.example.com/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=8HSOH-lXN3pJJ3FiaAw1XFhLCdzL44RtFS7z9S8thug%3D"
        )

    def test_kitchen_sink(self, embedder, vanity_domain_embedder):
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

        url = vanity_domain_embedder.build_url(
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
            "https://foo.example.com/embed/login?"
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
            "&signature=UFgVTk9HVXtEzbuoEBgvFaG1DvUdYVBJbfvfnE25WYY%3D"
        )

    def test_link_access(self, embedder, vanity_domain_embedder):
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

        url = vanity_domain_embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            link_access=True,
        )
        assert (
            url
            == "https://foo.example.com/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&linkAccess=__omni_link_access_open&signature=7tFx5JlpXvJCW0llSTTioLWg53m5iGQCKKn1Yz9EO2o%3D"
        )
        url = vanity_domain_embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            link_access=["abcd1234", "efgh5678"],
        )
        assert (
            url
            == "https://foo.example.com/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&linkAccess=abcd1234%2Cefgh5678&signature=UycR_auXAIHGVTDPahgMSt4NOUxDEVc92Y3ollHcU5Q%3D"
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

        empty_dict_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            filter_search_params={},
        )
        assert (
            empty_dict_url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=mToqUfdkmVSyDIGAl6Ggs9uAmGQAH9OzbbCZ-xgEU8c%3D"
        )

    def test_missing_organization_name_or_vanity_domain(self):
        with pytest.raises(OmniConfigError):
            OmniDashboardEmbedder(embed_secret="super_secret")

    def test_missing_embed_secret(self):
        with pytest.raises(OmniConfigError):
            OmniDashboardEmbedder(organization_name="acme")

        with pytest.raises(OmniConfigError):
            OmniDashboardEmbedder(vanity_domain="foo.example.com")

    def test_env_configuration_with_organization(self, monkeypatch):
        monkeypatch.setenv("OMNI_ORGANIZATION_NAME", "acme")
        monkeypatch.setenv("OMNI_EMBED_SECRET", "super_secret")
        embedder = OmniDashboardEmbedder()
        assert embedder.embed_secret == "super_secret"
        assert embedder.embed_login_url == "https://acme.embed-omniapp.co/embed/login"

    def test_env_configuration_with_vanity_domain(self, monkeypatch):
        monkeypatch.setenv("OMNI_VANITY_DOMAIN", "foo.example.com")
        monkeypatch.setenv("OMNI_EMBED_SECRET", "super_secret")
        embedder = OmniDashboardEmbedder()
        assert embedder.embed_login_url == "https://foo.example.com/embed/login"


class TestFilters:

    @pytest.mark.parametrize(
        "filter_type,operator,is_negative,values,expected",
        [
            (
                OmniFilterDefinition.Type.number,
                OmniFilterDefinition.Operator.equals,
                False,
                10,
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "EQUALS", "type": "number", "values": [10], "is_inclusive": false}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.number,
                OmniFilterDefinition.Operator.greater_than,
                False,
                10,
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "GREATER_THAN", "type": "number", "values": [10], "is_inclusive": false}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.number,
                OmniFilterDefinition.Operator.less_than,
                False,
                10,
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "LESS_THAN", "type": "number", "values": [10], "is_inclusive": false}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.number,
                OmniFilterDefinition.Operator.less_than_or_equal,
                False,
                10,
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "LESS_THAN", "type": "number", "values": [10], "is_inclusive": true}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.number,
                OmniFilterDefinition.Operator.greater_than_or_equal,
                False,
                10,
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "GREATER_THAN", "type": "number", "values": [10], "is_inclusive": true}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.number,
                OmniFilterDefinition.Operator.between,
                False,
                [10, 25],
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "BETWEEN", "type": "number", "values": [10, 25], "is_inclusive": false}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.string,
                OmniFilterDefinition.Operator.equals,
                False,
                "California",
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "EQUALS", "type": "string", "values": ["California"]}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.string,
                OmniFilterDefinition.Operator.starts_with,
                False,
                "California",
                (
                    "f--some.attr",
                    [
                        '{"is_negative": false, "kind": "STARTS_WITH", "type": "string", "values": ["California"]}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.string,
                OmniFilterDefinition.Operator.ends_with,
                True,
                "California",
                (
                    "f--some.attr",
                    [
                        '{"is_negative": true, "kind": "ENDS_WITH", "type": "string", "values": ["California"]}'
                    ],
                ),
            ),
            (
                OmniFilterDefinition.Type.string,
                OmniFilterDefinition.Operator.contains,
                True,
                "California",
                (
                    "f--some.attr",
                    [
                        '{"is_negative": true, "kind": "CONTAINS", "type": "string", "values": ["California"]}'
                    ],
                ),
            ),
        ],
    )
    def test_filters(self, filter_type, operator, is_negative, values, expected):
        filter = OmniFilterDefinition(
            field="some.attr",
            type=filter_type,
            operator=operator,
            is_negative=is_negative,
        )
        assert filter.get_filter_search_param_info(values) == expected

    def test_filter_negative_not_required(self):
        filter = OmniFilterDefinition(
            field="some.attr",
            type=OmniFilterDefinition.Type.string,
            operator=OmniFilterDefinition.Operator.contains,
        )
        assert filter.get_filter_search_param_info("California") == (
            "f--some.attr",
            [
                '{"is_negative": false, "kind": "CONTAINS", "type": "string", "values": ["California"]}'
            ],
        )

    def test_bad_filters_in_filter_set(self):
        with pytest.raises(TypeError):
            OmniFilterSet(fail="nope")

    def test_filter_set(self):
        filter_set = OmniFilterSet(
            latitude=OmniFilterDefinition(
                field="address.latitude_filter",
                type=OmniFilterDefinition.Type.number,
            ),
            longitude=OmniFilterDefinition(
                field="address.longitude_filter",
                type=OmniFilterDefinition.Type.number,
            ),
            distance=OmniFilterDefinition(
                field="address.distance_selected_to_address_in_miles",
                type=OmniFilterDefinition.Type.number,
                operator=OmniFilterDefinition.Operator.less_than,
            ),
        )
        assert filter_set.get_filter_search_params(
            {"latitude": 33.555, "longitude": -117.602, "distance": 10}
        ) == {
            "f--address.distance_selected_to_address_in_miles": [
                '{"is_negative": false, "kind": "LESS_THAN", "type": "number", "values": [10], "is_inclusive": false}'
            ],
            "f--address.latitude_filter": [
                '{"is_negative": false, "kind": "EQUALS", "type": "number", "values": [33.555], "is_inclusive": false}'
            ],
            "f--address.longitude_filter": [
                '{"is_negative": false, "kind": "EQUALS", "type": "number", "values": [-117.602], "is_inclusive": false}'
            ],
        }
