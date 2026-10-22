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
        self._service = service

    def lend_book(self, request: LendBookRequest) -> LendBookResponse:
        try:
            self._service.lend_book(request.member_id, request.isbn)
        except LibraryError as exc:
            return LendBookResponse(ResponseStatus.FAILURE, str(exc))
        return LendBookResponse(ResponseStatus.SUCCESS)
