class UpdateWaitListRequestDto:
    def __init__(self, user_id: int, number_of_seats: int):
        self.user_id = user_id
        self.number_of_seats = number_of_seats
