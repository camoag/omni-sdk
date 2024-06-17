from __future__ import annotations

import base64
import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Literal
import urllib.parse

from omni.utils import compact_json_dump


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

    def __str__(self):
        """String representation renders the complete URL for the embedded dashboard."""
        params = asdict(self)
        del params["base_url"]
        empty_keys = [key for key, value in params.items() if value is None]
        for key in empty_keys:
            del params[key]
        return f"{self.base_url}?{urllib.parse.urlencode(params)}"


class OmniDashboardEmbedder:

    class PrefersDark(Enum):
        yes = "true"
        no = "false"
        system = "system"

    class Theme(Enum):
        dawn = "dawn"
        vibes = "vibes"
        breeze = "breeze"
        blank = "blank"

    def __init__(self, organization_name: str, embed_secret: str):
        self.embed_login_url = (
            f"https://{organization_name}.embed-omniapp.co/embed/login"
        )
        self.embed_secret = embed_secret

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

        # Preprocess some values before passing to URL object.
        if link_access is True:
            link_access = "__omni_link_access_open"
        elif isinstance(link_access, list):
            link_access = ",".join(link_access)

        if custom_theme:
            custom_theme = compact_json_dump(custom_theme)

        if user_attributes:
            user_attributes = compact_json_dump(user_attributes)

        if isinstance(filter_search_params, dict):
            filter_search_params = urllib.parse.urlencode(
                filter_search_params, doseq=True
            )

        url = DashboardEmbedUrl(
            base_url=self.embed_login_url,
            contentPath=content_path,
            externalId=external_id,
            name=name,
            customTheme=custom_theme,
            entity=entity,
            filterSearchParam=filter_search_params,
            linkAccess=str(link_access),
            prefersDark=prefers_dark.value if prefers_dark else None,
            theme=theme.value if theme else None,
            userAttributes=user_attributes,
            nonce=uuid.uuid4().hex(),
        )
        self._sign_url(url)
        return str(url)

    def _sign_url(self, url: DashboardEmbedUrl) -> None:
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
        blob_items = [i for i in blob_items if i is not None]
        blob = "\n".join(blob_items)
        hmac_hash = hmac.new(
            self.embed_secret.encode("utf-8"), blob.encode("utf-8"), hashlib.sha256
        ).digest()
        url.signature = base64.urlsafe_b64encode(hmac_hash).decode("utf-8")
