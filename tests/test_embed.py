import base64
import hashlib
import hmac
import json
import urllib.parse
import zlib
from typing import Any

import pytest

from omni import OmniDashboardEmbedder
from omni.config import OmniConfigError
from omni.embed import (
    DEFAULT_EXPIRES_IN,
    MAX_EXPIRES_IN,
    OmniFilterDefinition,
    OmniFilterSet,
)

NOW = 1700000000


def decode_payload(url: str, secret: str = "super_secret") -> dict[str, Any]:
    """Verifies the signature of a v1 URL and returns the decoded payload parameters."""
    base_url, _, query = url.partition("?")
    params = urllib.parse.parse_qs(query, strict_parsing=True)
    assert sorted(params) == ["payload", "signature"]

    payload = params["payload"][0]
    expected_signature = base64.urlsafe_b64encode(
        hmac.new(
            secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
        ).digest()
    ).decode("ascii")
    assert params["signature"][0] == expected_signature

    # Raw DEFLATE (RFC 1951) - a negative wbits means there is no zlib wrapper.
    decompressed = zlib.decompress(base64.urlsafe_b64decode(payload), -zlib.MAX_WBITS)
    decoded: dict[str, Any] = json.loads(decompressed.decode("utf-8"))
    assert decoded["loginUrl"] == base_url
    return decoded


@pytest.fixture
def embedder() -> OmniDashboardEmbedder:
    return OmniDashboardEmbedder(organization_name="acme", embed_secret="super_secret")


@pytest.fixture
def vanity_domain_embedder() -> OmniDashboardEmbedder:
    return OmniDashboardEmbedder(
        vanity_domain="foo.example.com", embed_secret="super_secret"
    )


@pytest.fixture(autouse=True)
def patch_uuid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("uuid.UUID.hex", "365f7003aa5b4f3586d9b81b4a5d9f69")


@pytest.fixture(autouse=True)
def patch_time(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.time", lambda: float(NOW))


class TestUnit:
    def test_basic_url(
        self,
        embedder: OmniDashboardEmbedder,
        vanity_domain_embedder: OmniDashboardEmbedder,
    ) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
        )
        assert (
            url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=mToqUfdkmVSyDIGAl6Ggs9uAmGQAH9OzbbCZ-xgEU8c%3D"
        )

        url = vanity_domain_embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
        )
        assert (
            url
            == "https://foo.example.com/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=8HSOH-lXN3pJJ3FiaAw1XFhLCdzL44RtFS7z9S8thug%3D"
        )

    def test_kitchen_sink(
        self,
        embedder: OmniDashboardEmbedder,
        vanity_domain_embedder: OmniDashboardEmbedder,
    ) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
            access_boost=True,
            connection_roles={"123456789": "VIEWER"},
            custom_theme={"dashboard-background": "#00FF00"},
            custom_theme_id="theme-123",
            email="user@example.com",
            entity="Acme",
            entity_folder_content_role=OmniDashboardEmbedder.ContentRole.editor,
            entity_folder_group_content_role=OmniDashboardEmbedder.ContentRole.viewer,
            entity_folder_label="EntityLabel",
            entity_group_label="GroupLabel",
            filter_search_params={"state": "GA"},
            groups=["group1", "group2"],
            link_access=True,
            mode=OmniDashboardEmbedder.AccessMode.application,
            model_roles={"model": "read"},
            prefers_dark=OmniDashboardEmbedder.PrefersDark.yes,
            preserve_entity_folder_content_role=True,
            theme=OmniDashboardEmbedder.Theme.dawn,
            ui_settings={"showNavigation": False},
            user_attributes={"country": "USA"},
        )

        assert url == (
            "https://acme.embed-omniapp.co/embed/login?"
            "contentPath=%2Fdashboards%2Fda24491e"
            "&externalId=1"
            "&name=Somebody"
            "&nonce=365f7003aa5b4f3586d9b81b4a5d9f69"
            "&accessBoost=true&connectionRoles=%7B%22123456789%22%3A%22VIEWER%22%7D"
            "&customTheme=%7B%22dashboard-background%22%3A%22%2300FF00%22%7D"
            "&customThemeId=theme-123"
            "&email=user%40example.com"
            "&entity=Acme&entityFolderContentRole=EDITOR"
            "&entityFolderGroupContentRole=VIEWER"
            "&entityFolderLabel=EntityLabel"
            "&entityGroupLabel=GroupLabel"
            "&filterSearchParam=state%3DGA"
            "&groups=%5B%22group1%22%2C%22group2%22%5D"
            "&linkAccess=__omni_link_access_open"
            "&mode=APPLICATION&modelRoles=%7B%22model%22%3A%22read%22%7D"
            "&prefersDark=true"
            "&preserveEntityFolderContentRole=true"
            "&theme=dawn"
            "&uiSettings=%7B%22showNavigation%22%3Afalse%7D"
            "&userAttributes=%7B%22country%22%3A%22USA%22%7D"
            "&signature=MmUEWVKKyuO3iDDtZGERxG1ousOQ5Ln342C-bftoxHs%3D"
        )

        url = vanity_domain_embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
            access_boost=True,
            connection_roles={"123456789": "VIEWER"},
            custom_theme={"dashboard-background": "#00FF00"},
            custom_theme_id="theme-123",
            email="user@example.com",
            entity="Acme",
            entity_folder_content_role=OmniDashboardEmbedder.ContentRole.editor,
            entity_folder_group_content_role=OmniDashboardEmbedder.ContentRole.viewer,
            entity_folder_label="EntityLabel",
            entity_group_label="GroupLabel",
            filter_search_params={"state": "GA"},
            groups=["group1", "group2"],
            link_access=True,
            mode=OmniDashboardEmbedder.AccessMode.application,
            model_roles={"model": "read"},
            prefers_dark=OmniDashboardEmbedder.PrefersDark.yes,
            preserve_entity_folder_content_role=True,
            theme=OmniDashboardEmbedder.Theme.dawn,
            ui_settings={"showNavigation": False},
            user_attributes={"country": "USA"},
        )

        assert url == (
            "https://foo.example.com/embed/login?"
            "contentPath=%2Fdashboards%2Fda24491e"
            "&externalId=1"
            "&name=Somebody"
            "&nonce=365f7003aa5b4f3586d9b81b4a5d9f69"
            "&accessBoost=true&connectionRoles=%7B%22123456789%22%3A%22VIEWER%22%7D"
            "&customTheme=%7B%22dashboard-background%22%3A%22%2300FF00%22%7D"
            "&customThemeId=theme-123"
            "&email=user%40example.com"
            "&entity=Acme&entityFolderContentRole=EDITOR"
            "&entityFolderGroupContentRole=VIEWER"
            "&entityFolderLabel=EntityLabel"
            "&entityGroupLabel=GroupLabel"
            "&filterSearchParam=state%3DGA"
            "&groups=%5B%22group1%22%2C%22group2%22%5D"
            "&linkAccess=__omni_link_access_open"
            "&mode=APPLICATION&modelRoles=%7B%22model%22%3A%22read%22%7D"
            "&prefersDark=true"
            "&preserveEntityFolderContentRole=true"
            "&theme=dawn"
            "&uiSettings=%7B%22showNavigation%22%3Afalse%7D"
            "&userAttributes=%7B%22country%22%3A%22USA%22%7D"
            "&signature=Zgjny-NQyWKZoosKJogKv-1fxVj7bmnSjOxb2O_ISz0%3D"
        )

    def test_link_access(
        self,
        embedder: OmniDashboardEmbedder,
        vanity_domain_embedder: OmniDashboardEmbedder,
    ) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
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
            signing_version="v0",
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
            signing_version="v0",
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
            signing_version="v0",
            link_access=["abcd1234", "efgh5678"],
        )
        assert (
            url
            == "https://foo.example.com/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&linkAccess=abcd1234%2Cefgh5678&signature=UycR_auXAIHGVTDPahgMSt4NOUxDEVc92Y3ollHcU5Q%3D"
        )

    def test_filter_search_params(self, embedder: OmniDashboardEmbedder) -> None:
        str_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
            filter_search_params="state=GA&county=Fulton",
        )
        dict_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v0",
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
            signing_version="v0",
            filter_search_params={},
        )
        assert (
            empty_dict_url
            == "https://acme.embed-omniapp.co/embed/login?contentPath=%2Fdashboards%2Fda24491e&externalId=1&name=Somebody&nonce=365f7003aa5b4f3586d9b81b4a5d9f69&signature=mToqUfdkmVSyDIGAl6Ggs9uAmGQAH9OzbbCZ-xgEU8c%3D"
        )

    def test_missing_organization_name_or_vanity_domain(self) -> None:
        with pytest.raises(OmniConfigError):
            OmniDashboardEmbedder(embed_secret="super_secret")

    def test_missing_embed_secret(self) -> None:
        with pytest.raises(OmniConfigError):
            OmniDashboardEmbedder(organization_name="acme")

        with pytest.raises(OmniConfigError):
            OmniDashboardEmbedder(vanity_domain="foo.example.com")

    def test_env_configuration_with_organization(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OMNI_ORGANIZATION_NAME", "acme")
        monkeypatch.setenv("OMNI_EMBED_SECRET", "super_secret")
        embedder = OmniDashboardEmbedder()
        assert embedder.embed_secret == "super_secret"
        assert embedder.embed_login_url == "https://acme.embed-omniapp.co/embed/login"

    def test_env_configuration_with_vanity_domain(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OMNI_VANITY_DOMAIN", "foo.example.com")
        monkeypatch.setenv("OMNI_EMBED_SECRET", "super_secret")
        embedder = OmniDashboardEmbedder()
        assert embedder.embed_login_url == "https://foo.example.com/embed/login"


class TestV1Signing:
    def test_basic_url(
        self,
        embedder: OmniDashboardEmbedder,
        vanity_domain_embedder: OmniDashboardEmbedder,
    ) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
        )
        assert url.startswith("https://acme.embed-omniapp.co/embed/login?payload=")
        assert decode_payload(url) == {
            "loginUrl": "https://acme.embed-omniapp.co/embed/login",
            "contentPath": "/dashboards/da24491e",
            "externalId": "1",
            "name": "Somebody",
            "nonce": "365f7003aa5b4f3586d9b81b4a5d9f69",
            "exp": NOW + DEFAULT_EXPIRES_IN,
        }

        url = vanity_domain_embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
        )
        assert decode_payload(url)["loginUrl"] == "https://foo.example.com/embed/login"

    def test_v1_is_the_default(self, embedder: OmniDashboardEmbedder) -> None:
        default_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
        )
        explicit_url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            signing_version="v1",
        )
        assert default_url == explicit_url

    def test_kitchen_sink(self, embedder: OmniDashboardEmbedder) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            access_boost=True,
            connection_roles={"123456789": "VIEWER"},
            custom_theme={"dashboard-background": "#00FF00"},
            custom_theme_id="theme-123",
            email="user@example.com",
            entity="Acme",
            entity_folder_content_role=OmniDashboardEmbedder.ContentRole.editor,
            entity_folder_group_content_role=OmniDashboardEmbedder.ContentRole.viewer,
            entity_folder_label="EntityLabel",
            entity_group_label="GroupLabel",
            filter_search_params={"state": "GA"},
            groups=["group1", "group2"],
            link_access=True,
            mode=OmniDashboardEmbedder.AccessMode.application,
            model_roles={"model": "read"},
            prefers_dark=OmniDashboardEmbedder.PrefersDark.yes,
            preserve_entity_folder_content_role=True,
            theme=OmniDashboardEmbedder.Theme.dawn,
            ui_settings={"showNavigation": False},
            user_attributes={"country": "USA"},
        )

        # JSON-valued parameters are real JSON in v1, not pre-stringified strings.
        assert decode_payload(url) == {
            "loginUrl": "https://acme.embed-omniapp.co/embed/login",
            "contentPath": "/dashboards/da24491e",
            "externalId": "1",
            "name": "Somebody",
            "nonce": "365f7003aa5b4f3586d9b81b4a5d9f69",
            "exp": NOW + DEFAULT_EXPIRES_IN,
            "accessBoost": True,
            "connectionRoles": {"123456789": "VIEWER"},
            "customTheme": {"dashboard-background": "#00FF00"},
            "customThemeId": "theme-123",
            "email": "user@example.com",
            "entity": "Acme",
            "entityFolderContentRole": "EDITOR",
            "entityFolderGroupContentRole": "VIEWER",
            "entityFolderLabel": "EntityLabel",
            "entityGroupLabel": "GroupLabel",
            "filterSearchParam": "state=GA",
            "groups": ["group1", "group2"],
            "linkAccess": "__omni_link_access_open",
            "mode": "APPLICATION",
            "modelRoles": {"model": "read"},
            "prefersDark": "true",
            "preserveEntityFolderContentRole": True,
            "theme": "dawn",
            "uiSettings": {"showNavigation": False},
            "userAttributes": {"country": "USA"},
        }

    def test_link_access(self, embedder: OmniDashboardEmbedder) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            link_access=["abcd1234", "efgh5678"],
        )
        assert decode_payload(url)["linkAccess"] == "abcd1234,efgh5678"

    def test_filter_search_params(self, embedder: OmniDashboardEmbedder) -> None:
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
        # filterSearchParam stays a URI-encoded query fragment, since that is what the parameter holds.
        assert str_url == dict_url
        assert decode_payload(str_url)["filterSearchParam"] == "state=GA&county=Fulton"

    def test_empty_values_are_omitted(self, embedder: OmniDashboardEmbedder) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            access_boost=False,
            connection_roles={},
            filter_search_params={},
            groups=[],
            user_attributes={},
        )
        assert set(decode_payload(url)) == {
            "loginUrl",
            "contentPath",
            "externalId",
            "name",
            "nonce",
            "exp",
        }

    def test_expires_in(self, embedder: OmniDashboardEmbedder) -> None:
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            expires_in=3600,
        )
        assert decode_payload(url)["exp"] == NOW + 3600

        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            expires_in=MAX_EXPIRES_IN,
        )
        assert decode_payload(url)["exp"] == NOW + MAX_EXPIRES_IN

    @pytest.mark.parametrize("expires_in", [0, -1, MAX_EXPIRES_IN + 1])
    def test_invalid_expires_in(
        self, embedder: OmniDashboardEmbedder, expires_in: int
    ) -> None:
        with pytest.raises(ValueError, match="expires_in"):
            embedder.build_url(
                content_path="/dashboards/da24491e",
                external_id="1",
                name="Somebody",
                expires_in=expires_in,
            )

    def test_expires_in_ignored_for_v0(self, embedder: OmniDashboardEmbedder) -> None:
        # v0 URLs have nowhere to carry an expiry, so the value is accepted and ignored.
        url = embedder.build_url(
            content_path="/dashboards/da24491e",
            external_id="1",
            name="Somebody",
            expires_in=-1,
            signing_version="v0",
        )
        assert "exp" not in urllib.parse.parse_qs(url.partition("?")[2])

    def test_invalid_signing_version(self, embedder: OmniDashboardEmbedder) -> None:
        with pytest.raises(ValueError, match="signing_version"):
            embedder.build_url(
                content_path="/dashboards/da24491e",
                external_id="1",
                name="Somebody",
                signing_version="v2",  # type: ignore[arg-type]
            )

    def test_payload_too_large(self, embedder: OmniDashboardEmbedder) -> None:
        # Random-ish values so the payload can't be compressed under the size limit.
        user_attributes = {
            f"attr_{i}": hashlib.sha256(str(i).encode()).hexdigest()
            for i in range(5000)
        }
        with pytest.raises(ValueError, match="larger than"):
            embedder.build_url(
                content_path="/dashboards/da24491e",
                external_id="1",
                name="Somebody",
                user_attributes=user_attributes,
            )


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
    def test_filters(
        self,
        filter_type: OmniFilterDefinition.Type,
        operator: OmniFilterDefinition.Operator,
        is_negative: bool,
        values: Any,
        expected: Any,
    ) -> None:
        filter = OmniFilterDefinition(
            field="some.attr",
            type=filter_type,
            operator=operator,
            is_negative=is_negative,
        )
        assert filter.get_filter_search_param_info(values) == expected

    def test_filter_negative_not_required(self) -> None:
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

    def test_bad_filters_in_filter_set(self) -> None:
        with pytest.raises(TypeError):
            OmniFilterSet(fail="nope")

    def test_filter_set(self) -> None:
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
