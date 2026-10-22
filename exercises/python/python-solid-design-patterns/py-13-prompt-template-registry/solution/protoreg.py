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
        self.client = client            # shared on purpose
        self.parent: "PromptTemplate | None" = None

    def __deepcopy__(self, memo: dict[int, Any]) -> "PromptTemplate":
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone          # register first so cycles resolve
        clone.name = self.name
        clone.system = self.system
        clone.examples = copy.deepcopy(self.examples, memo)
        clone.client = self.client      # never copy the client
        clone.parent = copy.deepcopy(self.parent, memo)
        return clone


class TemplateRegistry:
    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {}
        self._lock = threading.Lock()

    def register(self, template: PromptTemplate) -> None:
        with self._lock:
            if template.name in self._templates:
                raise KeyError(f"already registered: {template.name}")
            self._templates[template.name] = copy.deepcopy(template)  # own a private copy

    def get(self, name: str) -> PromptTemplate:
        with self._lock:
            try:
                stored = self._templates[name]
            except KeyError:
                raise KeyError(f"unknown template {name!r}; known: {sorted(self._templates)}") from None
            return copy.deepcopy(stored)

    def names(self) -> list[str]:
        with self._lock:
            return sorted(self._templates)


class Provider:
    registry: ClassVar[dict[str, type["Provider"]]] = {}

    def __init_subclass__(cls, /, name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        key = name or cls.__name__.removesuffix("Provider").lower()
        if key in Provider.registry:
            raise TypeError(f"duplicate provider {key!r}")
        Provider.registry[key] = cls

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> "Provider":
        try:
            provider_cls = Provider.registry[name]
        except KeyError:
            raise KeyError(f"unknown provider {name!r}; known: {sorted(Provider.registry)}") from None
        return provider_cls(**kwargs)
