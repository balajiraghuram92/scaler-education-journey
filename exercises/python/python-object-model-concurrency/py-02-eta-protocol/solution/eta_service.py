from eta_protocol import ETAProvider


class InternalETAProvider:
    def estimate_minutes(self, origin, destination) -> float:
        return abs(hash(origin) - hash(destination)) % 60


def get_eta(provider, origin, destination):
    if not isinstance(provider, ETAProvider):
        raise TypeError("Provider does not implement ETAProvider.")

    return provider.estimate_minutes(origin, destination)
