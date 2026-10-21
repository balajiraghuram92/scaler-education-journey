from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cloneable import Cloneable


class ConfigurationType(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    CUSTOM = "custom"
    DEFAULT = "default"


@dataclass
class Configuration(Cloneable["Configuration"]):
    theme_color: str
    auto_save: bool
    language: str
    dark_mode: bool
    font_size: int
    font_family: str
    type_: ConfigurationType

    def clone_object(self) -> Configuration:
        """Return an independent copy of this configuration (the Prototype operation).

        Changing the copy must never change the original.
        """
        raise NotImplementedError("Implement clone_object")
