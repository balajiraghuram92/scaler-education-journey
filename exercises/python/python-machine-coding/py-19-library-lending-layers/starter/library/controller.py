from dataclasses import dataclass
from enum import Enum

from library.exceptions import LibraryError
from library.service import LibraryService


class ResponseStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass(frozen=True)
class LendBookRequest:
    member_id: int
    isbn: str


@dataclass(frozen=True)
class LendBookResponse:
    status: ResponseStatus
    message: str = ""


class LibraryController:
    """Unwrap the request DTO, call the service, wrap the response DTO."""

    def __init__(self, service: LibraryService) -> None:
        raise NotImplementedError("keep the service")

    def lend_book(self, request: LendBookRequest) -> LendBookResponse:
        """SUCCESS on success; FAILURE with str(exc) as message for a LibraryError.

        Catch only LibraryError: any other exception is a bug and must propagate.
        """
        raise NotImplementedError
