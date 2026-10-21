from trip import Trip  # noqa: F401  (you will need it for the Trip implementation)


def estimate_fare(x):
    """Estimate a fare, choosing the behaviour from the TYPE of ``x`` with ``functools.singledispatch``.

    - the undecorated base function raises ``NotImplementedError``
    - ``float`` -> ``15 * distance``
    - ``str`` (route code) -> ``"HSR-AIRPORT"`` is 600, ``"MG-AIRPORT"`` is 550, any other code is 0
    - ``Trip`` -> ``15 * trip.distance_km``
    - an ``int`` is not a ``float``, so ``estimate_fare(10)`` must raise ``NotImplementedError``
    """
    raise NotImplementedError("Make this a singledispatch function and register the implementations")
