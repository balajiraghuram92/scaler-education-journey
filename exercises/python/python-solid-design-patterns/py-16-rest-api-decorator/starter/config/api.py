from abc import ABC, abstractmethod


# Base API interface
class Api(ABC):
    @abstractmethod
    def execute_request(self, request_data) -> str:
        pass


# Concrete API implementation
class ECommerceApi(Api):
    def execute_request(self, request_data) -> str:
        print("Processing request:", request_data)
        return "Response data"
