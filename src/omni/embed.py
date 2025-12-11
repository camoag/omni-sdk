from __future__ import annotations

import base64
import hashlib
import hmac
import json
import urllib.parse
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Literal

from .config import OmniConfig, OmniConfigError
from .utils import compact_json_dump


@dataclass
class DashboardEmbedUrl:
    base_url: str
    contentPath: str
    externalId: str
    name: str
    nonce: str
    accessBoost: str | None = None
    connectionRoles: str | None = None
    customTheme: str | None = None
    customThemeId: str | None = None
    email: str | None = None
    entity: str | None = None
    entityFolderContentRole: str | None = None
    entityFolderGroupContentRole: str | None = None
    entityFolderLabel: str | None = None
    entityGroupLabel: str | None = None
    filterSearchParam: str | None = None
    groups: str | None = None
    linkAccess: str | None = None
    mode: str | None = None
    modelRoles: str | None = None
    prefersDark: str | None = None
    preserveEntityFolderContentRole: str | None = None
    theme: str | None = None
    uiSettings: str | None = None
    userAttributes: str | None = None
    signature: str | None = None

    def __str__(self) -> str:
        """String representation renders the complete URL for the embedded dashboard."""
        params = asdict(self)
        del params["base_url"]
        empty_keys = [key for key, value in params.items() if value is None]
        for key in empty_keys:
            del params[key]
        return f"{self.base_url}?{urllib.parse.urlencode(params)}"


class OmniDashboardEmbedder:
    """Factory class for building and signing dashboard embedding URLs.

    Args:
        organization_name: organization_name: Omni organization name. OMNI_ORGANIZATION_NAME environment variable will
            be used as a fallback.
        embed_secret: Omni embed secret. OMNI_EMBED_SECRET environment variable will be used as a fallback.
        vanity_domain: Vanity domain configured with Omni. Should not be fully qualified. OMNI_VANITY_DOMAIN
            environment variable will be used as a fallback.

    Attributes:
        embed_login_url: Base url of embedded dashboard urls.
        embed_secret: Omni embed secret.
    """

    class AccessMode(Enum):
        """AccessMode options

        Attributes:
            application: APPLICATION
            single_content: SINGLE_CONTENT
        """

        application = "APPLICATION"
        single_content = "SINGLE_CONTENT"

    class ContentRole(Enum):
        """ContentRole options

        Attributes:
            viewer: VIEWER
            editor: EDITOR
            manager: MANAGER
            no_access: NO_ACCESS
        """

        viewer = "VIEWER"
        editor = "EDITOR"
        manager = "MANAGER"
        no_access = "NO_ACCESS"

    class PrefersDark(Enum):
        """PrefersDark options

        Attributes:
            yes: true
            no: false
            system: system
        """

        yes = "true"
        no = "false"
        system = "system"

    class Theme(Enum):
        """Theme options

        Attributes:
            dawn: dawn
            vibes: vibes
            breeze: breeze
            blank: blank
        """

        dawn = "dawn"
        vibes = "vibes"
        breeze = "breeze"
        blank = "blank"

    def __init__(
        self,
        organization_name: str | None = None,
        embed_secret: str | None = None,
        vanity_domain: str | None = None,
    ):
        omni_config = OmniConfig(
            required_attrs=["embed_secret"],
            organization_name=organization_name,
            embed_secret=embed_secret,
            vanity_domain=vanity_domain,
        )
        if not omni_config.vanity_domain and not omni_config.organization_name:
            raise OmniConfigError(
                "You must pass the vanity_domain or organization_name arguments OR "
                "set the OMNI_ORGANIZATION_NAME or OMNI_VANITY_DOMAIN environment variables."
            )
        embed_host = (
            omni_config.vanity_domain
            or f"{omni_config.organization_name}.embed-omniapp.co"
        )
        self.embed_login_url = f"https://{embed_host}/embed/login"

        # Required to appease mypy. If embed_secret is missing an OmniConfigError will have already been raised by the OmniConfig class.
        assert omni_config.embed_secret

        self.embed_secret = omni_config.embed_secret

    def build_url(
        self,
        content_path: str,
        external_id: str,
        name: str,
        access_boost: bool | None = None,
        connection_roles: dict | None = None,
        custom_theme: dict | None = None,
        custom_theme_id: str | None = None,
        email: str | None = None,
        entity: str | None = None,
        entity_folder_content_role: ContentRole | None = None,
        entity_folder_group_content_role: ContentRole | None = None,
        entity_folder_label: str | None = None,
        entity_group_label: str | None = None,
        filter_search_params: str | dict | None = None,
        groups: list[str] | None = None,
        link_access: bool | list[str] | None = None,
        mode: AccessMode | None = None,
        model_roles: dict | None = None,
        prefers_dark: PrefersDark | None = None,
        preserve_entity_folder_content_role: bool | None = None,
        theme: Theme | None = None,
        ui_settings: dict | None = None,
        user_attributes: dict | None = None,
    ) -> str:
        """
        Builds a signed dashboard embedding URL. For more information on the options see the Omni Docs:
        https://docs.omni.co/embed/setup/url-parameters

        Args:
            access_boost (bool, optional): Enables AccessBoost for the embedded dashboard.
            connection_roles (dict, optional): Level of access for all models in a connection.
            content_path (str): Path pointing to the dashboard you wish to embed.
            custom_theme (dict, optional): Custom theme properties for styling embedded dashboards.
            custom_theme_id (str, optional): Theme ID from your Omni instance to stylize embedded dashboards.
            email (str, optional): Email for entity users when sharing content or sending deliveries.
            entity (str, optional): User group identifier to associate the embed user with a larger group.
            entity_folder_content_role (str, optional): Content role for the embed user's shared entity folder.
            entity_folder_group_content_role (str, optional): Content role for the embed entity group shared folder.
            entity_folder_label (str, optional): Label for the embed user's associated entity folder.
            entity_group_label (str, optional): Label for the embed user's associated entity group.
            external_id (str): Unique ID for the embed user.
            filter_search_params (str | dict, optional): Filters to apply for the embedded content.
            groups (list[str], optional): Associate embed user with existing user groups in your Omni instance.
            link_access (bool | list[str], optional): Controls which Omni dashboards can be linked to from the embedded dashboard.
            mode (AccessMode, optional): Type of access users will have to Omni in the iframe.
            model_roles (dict, optional): Level of access for individual models in a connection.
            name (str): Name for the embed user's name property.
            prefers_dark (PrefersDark, optional): Light or dark mode appearance.
            preserve_entity_folder_content_role (bool, optional): Retains the embed user's existing entity folder content role.
            theme (Theme, optional): Built-in Omni application theme.
            ui_settings (dict, optional): General settings of the application in embed.
            user_attributes (dict, optional): User attributes to apply to the embed user.

        Returns:
            str: Signed dashboard embedding URL.
        """

        # Preprocess some values before passing to URL object.
        if link_access is True:
            _link_access = "__omni_link_access_open"
        elif isinstance(link_access, list):
            _link_access = ",".join(link_access)
        elif not link_access:
            _link_access = None
        else:
            raise ValueError(
                "link_access must be a list of dashboard IDs or True to allow links to all dashboards."
            )

        # Convert empty dicts and strings to None.
        filter_search_params = filter_search_params or None
        if isinstance(filter_search_params, dict):
            filter_search_params = urllib.parse.urlencode(
                filter_search_params, doseq=True
            )

        url = DashboardEmbedUrl(
            base_url=self.embed_login_url,
            contentPath=content_path,
            externalId=external_id,
            name=name,
            accessBoost="true" if access_boost else None,
            connectionRoles=(
                compact_json_dump(connection_roles) if connection_roles else None
            ),
            customTheme=compact_json_dump(custom_theme) if custom_theme else None,
            customThemeId=custom_theme_id,
            email=email,
            entity=entity,
            entityFolderContentRole=(
                entity_folder_content_role.value if entity_folder_content_role else None
            ),
            entityFolderGroupContentRole=(
                entity_folder_group_content_role.value
                if entity_folder_group_content_role
                else None
            ),
            entityFolderLabel=entity_folder_label,
            entityGroupLabel=entity_group_label,
            filterSearchParam=filter_search_params,
            groups=compact_json_dump(groups) if groups else None,
            linkAccess=_link_access,
            mode=mode.value if mode else None,
            modelRoles=compact_json_dump(model_roles) if model_roles else None,
            prefersDark=prefers_dark.value if prefers_dark else None,
            preserveEntityFolderContentRole=(
                "true" if preserve_entity_folder_content_role else None
            ),
            theme=theme.value if theme else None,
            uiSettings=compact_json_dump(ui_settings) if ui_settings else None,
            userAttributes=(
                compact_json_dump(user_attributes) if user_attributes else None
            ),
            nonce=uuid.uuid4().hex,
        )

        self._sign_url(url)
        return str(url)

    def _sign_url(self, url: DashboardEmbedUrl) -> None:
        """Creates a signature and adds it to the URL object."""

        # IMPORTANT: These must be in the correct order as documented here
        # https://docs.omni.co/embed/setup/standard-sso#manual-generation

        blob_items = [
            url.base_url,
            url.contentPath,
            url.externalId,
            url.name,
            url.nonce,
            url.accessBoost,
            url.connectionRoles,
            url.customTheme,
            url.customThemeId,
            url.email,
            url.entity,
            url.entityFolderContentRole,
            url.entityFolderGroupContentRole,
            url.entityFolderLabel,
            url.entityGroupLabel,
            url.filterSearchParam,
            url.groups,
            url.linkAccess,
            url.mode,
            url.modelRoles,
            url.prefersDark,
            url.preserveEntityFolderContentRole,
            url.theme,
            url.uiSettings,
            url.userAttributes,
        ]
        blob = "\n".join([i for i in blob_items if i is not None])
        hmac_hash = hmac.new(
            self.embed_secret.encode("utf-8"), blob.encode("utf-8"), hashlib.sha256
        ).digest()
        url.signature = base64.urlsafe_b64encode(hmac_hash).decode("utf-8")


@dataclass
class OmniFilterDefinition:
    """Defines an Omni dashboard filter. Used to populate an OmniFilterSet and generate the filter search params
    for an embedded dashboard URL.

    Args:
        field: Name of the Omni field a filter exists for. Generally a dot-path representing a dimension in a view.
        type: Type of the value to be filtered on.
        operator: Type of filter operation to perform.

    Attributes:
        field: Name of the Omni field a filter exists for. Generally a dot-path representing a dimension in a view.
        type: Type of the value to be filtered on.
        operator: Type of filter operation to perform.

    """

    class Type(Enum):
        """Omni Filter Type Options

        Attributes:
            number: number
            string: string
        """

        number = "number"
        string = "string"

    class Operator(Enum):
        """Omni Filter Operator Options

        Attributes:
            equals: EQUALS
            less_than: LESS_THAN
            greater_than: GREATER_THAN
            less_than_or_equal = LESS_THAN_OR_EQUAL
            greater_than_or_equal = GREATER_THAN_OR_EQUAL
            contains = CONTAINS
            between = BETWEEN
            starts_with = STARTS_WITH
            ends_with = ENDS_WITH
        """

        equals = "EQUALS"
        less_than = "LESS_THAN"
        greater_than = "GREATER_THAN"
        less_than_or_equal = "LESS_THAN_OR_EQUAL"
        greater_than_or_equal = "GREATER_THAN_OR_EQUAL"
        contains = "CONTAINS"
        between = "BETWEEN"
        starts_with = "STARTS_WITH"
        ends_with = "ENDS_WITH"

    field: str
    type: Type
    operator: Operator = Operator.equals
    is_negative: bool = False

    def get_filter_search_param_info(
        self, values: str | int | float | list[str | int | float]
    ) -> tuple[str, list[str]]:
        """Returns the key and value to be used in a query string for an Omni Dashboard.

        Args:
            values: Value or list of values to filter on.

        Returns:
            : Key and value to use in the filter search params when building an embedded dashboard URL.
        """
        if not isinstance(values, list):
            values = [values]
        filter_key = f"f--{self.field}"

        is_inclusive = False

        operator_kind = self.operator.value

        if self.operator == self.Operator.greater_than_or_equal:
            is_inclusive = True
            operator_kind = self.Operator.greater_than.value
        elif self.operator == self.Operator.less_than_or_equal:
            is_inclusive = True
            operator_kind = self.Operator.less_than.value

        filter_value_param = {
            "is_negative": self.is_negative,
            "kind": operator_kind,
            "type": self.type.value,
            "values": values,
        }

        if self.type == self.Type.number:
            filter_value_param["is_inclusive"] = is_inclusive

        filter_value = [json.dumps(filter_value_param)]
        return filter_key, filter_value


class OmniFilterSet:
    """Helper class for generating a set of filter search parameters for an embedded dashboard. This class is designed
    to abstract the complexity of the Omni filters and create a simple interface for generating the filter values to
    be used by the OmniDashboardEmbedder.

    Args:
        **filters: Arbitrary kwargs defining filter definitions. The kwarg is the name of the filter and defines the
            schema for the dict that should be passed to the get_filter_search_params method. The value for each kwarg is
            the OmniFilterDefinition object that will be used to translate the value to a viable Omni filter search param.

    """

    def __init__(self, **filters: OmniFilterDefinition) -> None:
        for value in filters.values():
            if not isinstance(value, OmniFilterDefinition):
                raise TypeError("Filters must be an OmniFilterDefinition object.")
        self._filters = filters

    @property
    def filters(self) -> dict[str, OmniFilterDefinition]:
        """Filters in this filter set. This defines the schema of the dict that should be passed to the
        `get_filter_search_params` method.
        """
        # Using a property function here to discourage manipulating filters after instantiation.
        return self._filters

    def get_filter_search_params(
        self, filter_values: dict[str, str | int | float]
    ) -> dict[str, list[str]]:
        """Given a dictionary of filter keys and values this function returns the dictionary of expected to populate
        the filter_search_params kwarg when calling OmniDashboardEmbedder.build_url. This method is ideal for
        translating query params in the encapsulating application to Omni filter search parameters.

        Args:
            filter_values: Dict where the keys are the filter names and values are the values to filter on. The
                list of available filters can be found in the `filters` property.

        Returns:
            : Dict to be passed as the `filter_search_params` kwarg in the `OmniDashboardEmbedder.build_url` method.
        """
        filter_search_params = {}
        for query_param, value in filter_values.items():
            omni_filter = self.filters[query_param]
            filter_key, filter_value = omni_filter.get_filter_search_param_info(value)
            filter_search_params[filter_key] = filter_value
        return filter_search_params
