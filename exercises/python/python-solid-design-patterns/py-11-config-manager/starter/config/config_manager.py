from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Type


class FileBasedConfigurationManager(ABC):
    def __init__(self) -> None:
        self.properties: Dict[str, str] = {}

    def load(self, file_path: Path) -> None:
        try:
            with open(file_path, "r") as file:
                for line in file:
                    key, value = line.strip().split("=")
                    self.properties[key.strip()] = value.strip()
        except IOError as e:
            raise RuntimeError("Error while loading configuration file") from e

    @staticmethod
    def get_instance() -> FileBasedConfigurationManager:
        pass

    @staticmethod
    def reset_instance() -> None:
        pass

    @abstractmethod
    def get_configuration(self, key: str) -> str:
        pass

    @abstractmethod
    def get_configuration_with_type(self, key: str, type_: Type) -> Any:
        pass

    @abstractmethod
    def set_configuration(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def remove_configuration(self, key: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    def get_properties(self) -> Dict[str, str]:
        return self.properties

    @staticmethod
    def convert(value: str, type_: Type) -> Any:
        print(f"Converting {value} to {type_.__name__}")
        try:
            return type_(value)
        except ValueError:
            raise ValueError("Cannot convert value to specified type")
