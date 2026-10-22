import threading
from typing import Optional, Type, Any

from .config_manager import FileBasedConfigurationManager


class FileBasedConfigurationManagerImpl(FileBasedConfigurationManager):
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_instance() -> FileBasedConfigurationManager:
        if FileBasedConfigurationManagerImpl._instance is None:
            with FileBasedConfigurationManagerImpl._lock:
                if FileBasedConfigurationManagerImpl._instance is None:
                    FileBasedConfigurationManagerImpl._instance = (
                        FileBasedConfigurationManagerImpl()
                    )
        return FileBasedConfigurationManagerImpl._instance

    @staticmethod
    def reset_instance() -> None:
        with FileBasedConfigurationManagerImpl._lock:
            FileBasedConfigurationManagerImpl._instance = None

    def get_configuration(self, key: str) -> Optional[str]:
        return self.get_properties().get(key, None)

    def get_configuration_with_type(self, key: str, type_: Type) -> Optional[Any]:
        value = self.get_configuration(key)
        return self.convert(value, type_) if value is not None else None

    def set_configuration(self, key: str, value: str) -> None:
        self.get_properties().update({key: value})

    def set_configuration_with_value(self, key: str, value: Any) -> None:
        self.set_configuration(key, str(value))

    def remove_configuration(self, key: str) -> None:
        self.get_properties().pop(key, None)

    def clear(self) -> None:
        self.get_properties().clear()
