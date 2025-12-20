from celery import shared_task
from fastapi_mail import (
    ConnectionConfig,
    MessageSchema,
    FastMail,
    MessageType
)

from src.core.config import settings
from .commons import run_async_task

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(email_to: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)

    await fm.send_message(message)


@shared_task(
    name="send_activation_email_task",
    bind=True,
    max_retries=5,
    default_retry_delay=300
)
def send_activation_email_task(self, email: str, token: str):
    body = f"""
    <h1>Activation Email</h1>
    <p>Your activation token: {token}
    """
    run_async_task(send_email(
        email, "Activate Account [Online Cinema]", body
    ))


@shared_task(
    name="send_reset_password_email_task",
    bind=True,
    max_retries=5,
    default_retry_delay=300
)
def send_reset_password_email_task(self, email: str, token: str):
    body = f"""
    <h1>Reset Password Email</h1>
    <p>Your token is: <b>{token}</b></p>
    """
    run_async_task(send_email(email, "Reset Password [Online Cinema]", body))


@shared_task(
    name="send_comment_notification_email_task",
    bind=True,
    max_retries=5,
    default_retry_delay=300
)
def send_comment_notification_email_task(
        self, email: str, comment_id: int, movie_name: str
):
    body = f"""
    <h1>Someone Replied To Your Comment</h1>
    <p>Your comment {comment_id} under the movie {movie_name} got a reply</p>
    """
    run_async_task(send_email(email, "New Reply! [Online Cinema]", body))
