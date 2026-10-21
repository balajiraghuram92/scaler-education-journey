from abc import ABC

from .storage import FileStorage
from .utils import StorageUtils


class BaseFileDecorator(FileStorage, ABC):
    def __init__(self, file_storage: FileStorage):
        self._file_storage = file_storage

    def store_file(self, file_data: bytes, file_name: str):
        self._file_storage.store_file(file_data, file_name)

    def retrieve_file(self, file_name: str) -> bytes:
        return self._file_storage.retrieve_file(file_name)


class CompressionDecorator(BaseFileDecorator):
    def store_file(self, file_data: bytes, file_name: str):
        super().store_file(StorageUtils.compress(file_data), file_name)

    def retrieve_file(self, file_name: str) -> bytes:
        return StorageUtils.decompress(super().retrieve_file(file_name))


class VirusScanDecorator(BaseFileDecorator):
    def store_file(self, file_data: bytes, file_name: str):
        if not StorageUtils.scan_for_virus(file_data):
            raise ValueError("File contains virus and cannot be stored")
        super().store_file(file_data, file_name)
