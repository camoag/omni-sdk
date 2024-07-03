from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class OmniConfig:
    """Fetches configuration options from arguments or environment variables."""

    required_attrs: list[str]
    organization_name: str | None = None
    vanity_domain: str | None = None
    embed_secret: str | None = None
    api_key: str | None = None

    @staticmethod
    def _get_env_var(attr_name: str) -> str:
        return f"OMNI_{attr_name.upper()}"

    def __getattribute__(self, name: str) -> Any:
        """Overrides built-in `__getattribute__` to fall back to environment variables with the OMNI_ prefix."""
        value = super().__getattribute__(name)
        if value is None:
            value = os.environ.get(self._get_env_var(name))
        return value

    def __post_init__(self) -> None:
        """Raises an error if a required config setting is missing."""
        if missing_required_attrs := [
            a for a in self.required_attrs if not getattr(self, a)
        ]:
            message = (
                f"Omni SDK has not been configured correctly. You must pass the arguments {missing_required_attrs} and/or set "
                f"the environment variables {[self._get_env_var(a) for a in missing_required_attrs]}. Please see the documentation "
                "for more information on configuration."
            )
            raise OmniConfigError(message)


class OmniConfigError(Exception):
    pass
