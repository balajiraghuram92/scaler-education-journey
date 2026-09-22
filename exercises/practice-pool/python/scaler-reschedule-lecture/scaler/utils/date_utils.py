from datetime import datetime, timedelta


def get_future_schedule_dates(
        previous_lecture_date: datetime,
        schedule: str,
        count: int = 1

):
    days_delta = [2, 2, 3]
    times = []
    for i in range(count):
        prev_lecture_day = previous_lecture_date.weekday()
        delta_index = prev_lecture_day//2
        previous_lecture_date = previous_lecture_date + timedelta(days=days_delta[delta_index])
        if schedule.endswith("MORNING"):
            start_time = previous_lecture_date.replace(hour=7, minute=0)
            end_time = previous_lecture_date.replace(hour=9, minute=30)
            times.append([start_time, end_time])
        elif schedule.endswith("EVENING"):
            start_time = previous_lecture_date.replace(hour=21, minute=0)
            end_time = previous_lecture_date.replace(hour=23, minute=30)
            times.append([start_time, end_time])

    return times
