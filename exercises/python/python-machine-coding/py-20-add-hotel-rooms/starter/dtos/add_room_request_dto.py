class AddRoomRequestDto:
    def __init__(self):
        self.user_id: int = 0
        self.name: str = ""
        self.price: float = 0.0
        self.room_type: str = ""
        self.description: str = ""
