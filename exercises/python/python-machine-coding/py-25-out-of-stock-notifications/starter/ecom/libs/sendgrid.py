def send_email(to: str, subject: str, body: str) -> bool:
    """Stand-in for the SendGrid SDK: pretends to send and reports success."""
    return True
