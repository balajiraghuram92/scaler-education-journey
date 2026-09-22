class NotFoundError(Exception):
    pass


class UnauthorizedAccessError(Exception):
    pass


class InvalidGateException(Exception):
    pass


class InvalidParkingLotException(Exception):
    pass


class UnsupportedAdditionalService(Exception):
    pass


class AdditionalServiceNotSupportedByVehicle(Exception):
    pass
