from typing import Dict, Optional

from .app_config import Configuration, ConfigurationType
from .registry import ConfigurationPrototypeRegistry


class ConfigurationPrototypeRegistryImpl(ConfigurationPrototypeRegistry):
    """Keeps one prototype configuration per ConfigurationType and hands out clones."""

    def __init__(self):
        self.prototypes: Dict[ConfigurationType, Configuration] = {}

    def add_prototype(self, configuration: Configuration) -> None:
        """Store the configuration keyed by its ``type_`` (a second one of the same type replaces it)."""
        raise NotImplementedError("Implement add_prototype")

    def get_prototype(self, type_: ConfigurationType) -> Optional[Configuration]:
        """Return the stored prototype itself, or None if there is none."""
        raise NotImplementedError("Implement get_prototype")

    def clone(self, type_: ConfigurationType) -> Optional[Configuration]:
        """Return a CLONE of the stored prototype, or None for an unknown type."""
        raise NotImplementedError("Implement clone")
