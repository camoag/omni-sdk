from __future__ import annotations

import os


class __OmniEnv:
    """Fetches configuration options from environment variables."""

    @property
    def ORGANIZATION_NAME(self) -> str | None:
        return os.environ.get("OMNI_ORGANIZATION_NAME")

    @property
    def EMBED_SECRET(self) -> str | None:
        return os.environ.get("OMNI_EMBED_SECRET")


OmniEnv = __OmniEnv()
