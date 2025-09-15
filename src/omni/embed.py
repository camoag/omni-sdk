from __future__ import annotations

import base64
import hashlib
import hmac
import json
import urllib.parse
import uuid
from dataclasses import asdict, dataclass
from enum import Enum

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
    entity: str | None = None
    filterSearchParam: str | None = None
    groups: str | None = None
    linkAccess: str | None = None
    prefersDark: str | None = None
    theme: str | None = None
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
        entity: str | None = None,
        filter_search_params: str | dict | None = None,
        groups: list[str] | None = None,
        link_access: bool | list[str] | None = None,
        prefers_dark: PrefersDark | None = None,
        theme: Theme | None = None,
        user_attributes: dict | None = None,
    ) -> str:
        """Builds a signed dashboard embedding URL. For more information on the options see the [Omni Docs](
        https://docs.omni.co/docs/embed/private-embedding#embed-url-customization-options)

        Args:
            content_path: Path pointing to the dashboard you wish to build a URL to embed.
            external_id: Required parameter creating a unique ID. This can be any alphanumeric value.
            name: Required parameter and can contain a non-unique name for the embed user's name property.
            custom_theme: Allows you to stylize your embedded dashboard to your preferred colors.
            access_boost: Boolean setting to enable Access Boost for the embedded dashboard.
            connection_roles: Required. Defines the connection roles available for embed users. Restricted queriers can create new content, Viewers can only consume dashboards.
            entity: An id to reference the entity the user belongs to. Commonly is the customer name or other
                identifying organization for this user.
            filter_search_params: Encoded string or a dict representing dashboard filter values . This can be derived
                by copying the substring after the "?" from a dashboard URL with non-empty filter values or using the
                `OmniFilterSet` helper class.
            groups: An array of group names that allows you to associate the resulting embed user with existing groups on your Omni instance.
            link_access: Allows you to customize which other Omni dashboards can be linked to from the embedded dashboard.
                If set to True, all links on the embedded dashboard are permissed and shown. Alternatively, a list of
                dashboard IDs can be passed (i.e. ["abcd1234", "efgh5678", "ijkl9999"]) to only permiss to specific
                dashboard IDs. Finally, if the parameter is None, all links to other Omni dashboards are
                restricted. Note that link URLs to anything other than an Omni Dashboard will be shown and permissed
                regardless of the linkAccess parameter.
            prefers_dark: Dark mode setting.
            theme: Visual theming options.
            user_attributes: Dictionary of attributes matching defined user attributes in your Omni account.

        Returns:
            : Signed dashboard embedding URL.
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
            entity=entity,
            filterSearchParam=filter_search_params,
            groups=compact_json_dump(groups) if groups else None,
            linkAccess=_link_access,
            prefersDark=prefers_dark.value if prefers_dark else None,
            theme=theme.value if theme else None,
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
        # https://docs.omni.co/docs/embed/private-embedding#manually-generate-a-signature-and-url-hard-mode
        blob_items = [
            url.base_url,
            url.contentPath,
            url.externalId,
            url.name,
            url.nonce,
            url.accessBoost,
            url.connectionRoles,
            url.customTheme,
            url.entity,
            url.filterSearchParam,
            url.groups,
            url.linkAccess,
            url.prefersDark,
            url.theme,
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
