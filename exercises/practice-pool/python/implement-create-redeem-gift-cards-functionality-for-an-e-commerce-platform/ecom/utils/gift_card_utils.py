from uuid import uuid4


def generate_gift_card_code() -> str:
    return uuid4().hex.upper()[:10]