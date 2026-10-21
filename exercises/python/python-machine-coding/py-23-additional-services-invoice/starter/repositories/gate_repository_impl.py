from typing import Dict, Optional
from models.gate import Gate
from repositories.gate_repository import GateRepository


class GateRepositoryImpl(GateRepository):
    """
    In-memory implementation of GateRepository using a dictionary.
    """

    def __init__(self):
        self._gates: Dict[int, Gate] = {}
        self._items = self._gates
        self._current_id: int = 1

    def find_by_id(self, gate_id: int) -> Optional[Gate]:
        """
        Retrieves a gate by its ID, or None if not found.
        """
        return self._gates.get(gate_id)

    def save(self, gate: Gate) -> Gate:
        """
        Saves a gate to the repository, assigning an auto-incrementing ID if needed.
        """
        if gate.id is None or gate.id <= 0:
            gate.id = self._current_id
            self._current_id += 1

        self._gates[gate.id] = gate
        return gate
