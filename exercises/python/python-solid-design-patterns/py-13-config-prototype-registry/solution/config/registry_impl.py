from typing import Dict, Optional

from .app_config import Configuration, ConfigurationType
from .registry import ConfigurationPrototypeRegistry


class ConfigurationPrototypeRegistryImpl(ConfigurationPrototypeRegistry):

    def __init__(self):
        self.prototypes: Dict[ConfigurationType, Configuration] = {}

    def add_prototype(self, configuration: Configuration) -> None:
        self.prototypes[configuration.type_] = configuration

    def get_prototype(self, type_: ConfigurationType) -> Optional[Configuration]:
        return self.prototypes.get(type_)

    def clone(self, type_: ConfigurationType) -> Optional[Configuration]:
        return (
            self.prototypes[type_].clone_object() if type_ in self.prototypes else None
        )
