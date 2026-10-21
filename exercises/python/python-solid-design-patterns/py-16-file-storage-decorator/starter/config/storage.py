from abc import ABC

class FileStorage(ABC):
    def store_file(self, file_data: bytes, file_name: str):
        pass

    def retrieve_file(self, file_name: str) -> bytes:
        pass