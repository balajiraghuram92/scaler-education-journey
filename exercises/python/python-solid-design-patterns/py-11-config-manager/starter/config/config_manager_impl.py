from typing import Any, Optional, Type

from .config_manager import FileBasedConfigurationManager


class FileBasedConfigurationManagerImpl(FileBasedConfigurationManager):
    """System-wide configuration manager: a thread-safe, lazily created singleton.

    Keep the shared instance in a class attribute guarded by a class-level
    ``threading.Lock`` and use double-checked locking in ``get_instance``.
    All settings live in the inherited ``self.properties`` dict (use
    ``get_properties()``); do not edit the abstract base class.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_instance() -> FileBasedConfigurationManager:
        """Return the one shared instance, creating it on first use (thread-safe)."""
        raise NotImplementedError("Implement get_instance")

    @staticmethod
    def reset_instance() -> None:
        """Forget the instance so the next get_instance() builds a new object."""
        raise NotImplementedError("Implement reset_instance")

    def get_configuration(self, key: str) -> Optional[str]:
        """Return the string value for ``key`` or None when absent."""
        raise NotImplementedError("Implement get_configuration")

    def get_configuration_with_type(self, key: str, type_: Type) -> Optional[Any]:
        """Return the value converted with ``self.convert`` or None when absent."""
        raise NotImplementedError("Implement get_configuration_with_type")

    def set_configuration(self, key: str, value: str) -> None:
        """Store a string value."""
        raise NotImplementedError("Implement set_configuration")

    def set_configuration_with_value(self, key: str, value: Any) -> None:
        """Store ``str(value)``."""
        raise NotImplementedError("Implement set_configuration_with_value")

    def remove_configuration(self, key: str) -> None:
        """Remove ``key``; do nothing when it is absent."""
        raise NotImplementedError("Implement remove_configuration")

    def clear(self) -> None:
        """Remove all settings."""
        raise NotImplementedError("Implement clear")
