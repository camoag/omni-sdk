from __future__ import annotations

import os


class __OmniEnv:
    """Fetches configuration options from environment variables."""

    @property
    def ORGANIZATION_NAME(self) -> str | None:
        return os.environ.get("OMNI_ORGANIZATION_NAME")

    @property
    def VANITY_DOMAIN(self) -> str | None:
        """Configured Omni vanity domain (https://docs.omni.co/docs/embed/private-embedding#use-a-vanity-domain)

        Expects host, e.g. if vanity domain is https://foo.example.com, value should be 'foo.example.com'
        """
        return os.environ.get("OMNI_VANITY_DOMAIN")

    @property
    def EMBED_SECRET(self) -> str | None:
        return os.environ.get("OMNI_EMBED_SECRET")

    @property
    def API_KEY(self) -> str | None:
        return os.environ.get("OMNI_API_KEY")


OmniEnv = __OmniEnv()
