class UserNotFoundError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class OutOfStockError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass


class OrderCannotBeCancelledError(Exception):
    pass


class UnauthorizedAccessError(Exception):
    pass


class AddressNotFoundError(Exception):
    pass


class ProductInStockError(Exception):
    pass


class NotificationNotFoundError(Exception):
    pass
