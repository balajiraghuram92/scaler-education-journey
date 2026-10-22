from abc import ABC

from .storage import FileStorage
from .utils import StorageUtils


class BaseFileDecorator(ABC):
    """Base decorator: it IS a FileStorage and it HAS a FileStorage.

    - inherit from FileStorage
    - __init__(file_storage) keeps the wrapped storage in ``self._file_storage``
    - store_file(file_data, file_name) and retrieve_file(file_name) delegate to it
      (retrieve_file returns the wrapped result)
    """


class CompressionDecorator(BaseFileDecorator):
    """store_file: store StorageUtils.compress(file_data) in the wrapped storage.
    retrieve_file: fetch from the wrapped storage and return StorageUtils.decompress(...).
    """


class VirusScanDecorator(BaseFileDecorator):
    """store_file: if StorageUtils.scan_for_virus(file_data) is True store the file,
    otherwise raise ValueError("File contains virus and cannot be stored") and store nothing.
    retrieve_file: delegate only; it must NOT call the scanner.
    """
