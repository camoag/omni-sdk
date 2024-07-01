from __future__ import annotations

import base64
import hashlib
import hmac
import urllib.parse
import uuid
from dataclasses import asdict, dataclass
from enum import Enum

from .env import OmniEnv
from .utils import compact_json_dump


@dataclass
class DashboardEmbedUrl:
    base_url: str
    contentPath: str
    externalId: str
    name: str
    nonce: str
    customTheme: str | None = None
    entity: str | None = None
    filterSearchParam: str | None = None
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
    """Factory class that can build dashboard embedding URLs. The class can be instantiated with the omni
    organization_name and embed_secret or if either of the kwargs are omitted their values will be pulled from the
    environment variables OMNI_ORGANIZATION_NAME and OMNI_EMBED_SECRET.
    """

    class PrefersDark(Enum):
        yes = "true"
        no = "false"
        system = "system"

    class Theme(Enum):
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
        _organization_name = organization_name or OmniEnv.ORGANIZATION_NAME
        _vanity_domain = vanity_domain or OmniEnv.VANITY_DOMAIN
        if not (_organization_name or _vanity_domain):
            raise ValueError("'vanity_domain' or 'organization_name' are required.")
        _embed_secret = embed_secret or OmniEnv.EMBED_SECRET
        if not _embed_secret:
            raise ValueError(
                "embed_secret is required if it is not configured in environment variables."
            )

        embed_host = _vanity_domain or f"{_organization_name}.embed-omniapp.co"
        self.embed_login_url = f"https://{embed_host}/embed/login"
        self.embed_secret = _embed_secret

    def build_url(
        self,
        content_path: str,
        external_id: str,
        name: str,
        custom_theme: dict | None = None,
        entity: str | None = None,
        filter_search_params: str | dict | None = None,
        link_access: bool | list[str] | None = None,
        prefers_dark: PrefersDark | None = None,
        theme: Theme | None = None,
        user_attributes: dict | None = None,
    ) -> str:
        """Builds a signed dashboard embedding URL. For more information on the options see the [Omni Docs](
        https://docs.omni.co/docs/embed/private-embedding#embed-url-customization-options)
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
            customTheme=compact_json_dump(custom_theme) if custom_theme else None,
            entity=entity,
            filterSearchParam=filter_search_params,
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
            url.customTheme,
            url.entity,
            url.filterSearchParam,
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
