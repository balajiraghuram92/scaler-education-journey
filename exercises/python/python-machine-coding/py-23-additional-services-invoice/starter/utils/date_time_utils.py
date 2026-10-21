import math
from datetime import datetime


class DateTimeUtils:
    """
    Utility methods for date and time calculations in the parking lot system.
    """

    @staticmethod
    def calculate_hours(entry_time: datetime, exit_time: datetime) -> int:
        """
        Calculates the duration in hours between entry and exit, rounded up (ceiling).
        """
        diff_seconds = (exit_time - entry_time).total_seconds()
        return math.ceil(diff_seconds / 3600.0)
