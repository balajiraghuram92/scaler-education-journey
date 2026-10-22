from eta_protocol import ETAProvider  # noqa: F401


class InternalETAProvider:
    """Does NOT inherit from the protocol.

    ``estimate_minutes(origin, destination)`` returns ``abs(hash(origin) - hash(destination)) % 60``.
    """

    def estimate_minutes(self, origin, destination) -> float:
        raise NotImplementedError("Implement InternalETAProvider.estimate_minutes")


def get_eta(provider, origin, destination):
    """Raise ``TypeError`` unless ``isinstance(provider, ETAProvider)``, then return
    ``provider.estimate_minutes(origin, destination)``."""
    raise NotImplementedError("Implement get_eta")
