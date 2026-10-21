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
        """Keep an ordered list of entries and an id counter starting at 1."""
        raise NotImplementedError('TODO: implement __init__')

    def save(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        """Assign the next id, append the entry (insertion order is the queue order) and return it."""
        raise NotImplementedError('TODO: implement save')

    def find_all(self) -> List[WaitListPosition]:
        """A copy of the entries in insertion order."""
        raise NotImplementedError('TODO: implement find_all')

    def delete(self, wait_list_position: WaitListPosition) -> WaitListPosition:
        """Remove the entry and return it."""
        raise NotImplementedError('TODO: implement delete')
