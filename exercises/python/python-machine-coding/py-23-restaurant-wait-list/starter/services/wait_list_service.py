from abc import ABC, abstractmethod


class WaitListService(ABC):
    @abstractmethod
    def add_user_to_wait_list(self, user_id: int) -> int:
        pass

    @abstractmethod
    def get_wait_list_position(self, user_id: int) -> int:
        pass

    @abstractmethod
    def update_wait_list(self, admin_user_id: int, number_of_spots: int) -> None:
        pass
