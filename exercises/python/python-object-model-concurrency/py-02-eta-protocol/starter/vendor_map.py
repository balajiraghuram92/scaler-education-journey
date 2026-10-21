class VendorMapETA:
    """Third-party provider; it does NOT inherit from the protocol.

    ``estimate_minutes(origin, destination)`` always returns ``42.0``.
    """

    def estimate_minutes(self, origin, destination) -> float:
        raise NotImplementedError("Implement VendorMapETA.estimate_minutes")
