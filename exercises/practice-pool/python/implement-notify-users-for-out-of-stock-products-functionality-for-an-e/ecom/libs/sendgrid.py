def send_email(
        to: str,
        subject: str,
        body: str
) -> bool:
    # Code to send email using Sendgrid backend API
    print(
        f"Sending email to {to} with subject: {subject} and body: {body}"
    )
    return True
