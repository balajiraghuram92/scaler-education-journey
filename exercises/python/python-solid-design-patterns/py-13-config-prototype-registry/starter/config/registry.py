from abc import ABC, abstractmethod
from typing import Optional

from .app_config import Configuration, ConfigurationType


class ConfigurationPrototypeRegistry(ABC):

    @abstractmethod
    def add_prototype(self, configuration: Configuration) -> None:
        pass

    @abstractmethod
    def get_prototype(self, type_: ConfigurationType) -> Optional[Configuration]:
        pass

    @abstractmethod
    def clone(self, type_: ConfigurationType) -> Optional[Configuration]:
        pass
