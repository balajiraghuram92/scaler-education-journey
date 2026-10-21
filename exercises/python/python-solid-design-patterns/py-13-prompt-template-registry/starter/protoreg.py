import copy
import threading
from typing import Any, ClassVar


class HttpClient:
    """Stand-in for an expensive, non-copyable resource (it owns a lock)."""

    def __init__(self) -> None:
        self.lock = threading.Lock()


class PromptTemplate:
    def __init__(self, name: str, system: str, examples: list[str], client: HttpClient) -> None:
        self.name = name
        self.system = system
        self.examples = examples
        self.client = client  # shared on purpose
        self.parent: "PromptTemplate | None" = None

    def __deepcopy__(self, memo: dict[int, Any]) -> "PromptTemplate":
        """Selective deep copy.

        - ``examples`` and ``parent`` are deep-copied WITH the shared ``memo``.
        - ``client`` is shared by reference (a lock cannot be deep-copied).
        - Register the new object in ``memo`` BEFORE copying children, so cyclic
          ``parent`` references resolve instead of recursing forever.
        """
        raise NotImplementedError("Implement __deepcopy__")


class TemplateRegistry:
    """Thread-safe registry of prompt-template prototypes.

    - ``register`` stores a private deep copy and raises KeyError on a duplicate
      name (8 threads registering one name: exactly one succeeds).
    - ``get`` returns a fresh deep copy every call; an unknown name raises KeyError
      whose message names the unknown key and lists the known names.
    - ``names()`` returns the sorted names.
    """

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {}
        self._lock = threading.Lock()

    def register(self, template: PromptTemplate) -> None:
        raise NotImplementedError("Implement register")

    def get(self, name: str) -> PromptTemplate:
        raise NotImplementedError("Implement get")

    def names(self) -> list[str]:
        raise NotImplementedError("Implement names")


class Provider:
    """Base class whose subclasses register themselves in ``Provider.registry``.

    Use ``__init_subclass__(cls, /, name=None, **kwargs)``. Default key: the class
    name without a ``Provider`` suffix, lower-cased (``OpenAIProvider`` -> ``openai``).
    A duplicate key raises TypeError (message mentions ``duplicate``).
    ``Provider.create(name, **kwargs)`` instantiates the registered class; an unknown
    name raises KeyError whose message lists the known names.
    """

    registry: ClassVar[dict[str, type["Provider"]]] = {}

    def __init_subclass__(cls, /, name: str | None = None, **kwargs: Any) -> None:
        raise NotImplementedError("Implement __init_subclass__")

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> "Provider":
        raise NotImplementedError("Implement create")
