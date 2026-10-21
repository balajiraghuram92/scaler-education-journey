from typing import List
from repositories.wait_list_position_repository import WaitListPositionRepository
from models.wait_list_position import WaitListPosition


class WaitListPositionRepositoryImpl(WaitListPositionRepository):
    """
    The in-memory implementation of WaitListPositionRepository.

    We store all wait list entries in a Python list.
    A list is the right data structure here because:
      - It preserves insertion order (first added = position 1)
      - We need to remove entries from the front (like a queue)

    A counter (_current_id) gives each entry a unique ID.
    """

    def __init__(self):
        # Our in-memory wait list — preserves insertion order
        self._wait_list: List[WaitListPosition] = []
        # Auto-increment counter for assigning IDs
        self._current_id: int = 1

    def save(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        # Assign the next available ID to this entry
        wait_list_position.id = self._current_id
        self._current_id += 1
        # Append to the end of the list — this person is last in the queue
        self._wait_list.append(wait_list_position)
        return wait_list_position

    def find_all(self) -> List[WaitListPosition]:
        # Return a copy of the list so callers cannot accidentally modify
        # our internal list by changing the returned list
        return list(self._wait_list)

    def delete(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        # Remove the specific entry from the list
        self._wait_list.remove(wait_list_position)
        return wait_list_position
