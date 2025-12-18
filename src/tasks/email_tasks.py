from celery import shared_task
from fastapi_mail import ConnectionConfig, MessageSchema
from fastapi_mail import FastMail
import asyncio

from src.core.config import settings

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
    from fastapi_mail import MessageType
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)

    await fm.send_message(message)


@shared_task(name="send_activation_email_task")
def send_activation_email_task(email: str, token: str):
    body = f"""
    <h1>Activation Email</h1>
    <p>Your activation token: {token}
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_email(
        email, "Activate Account [Online Cinema]", body
    )
    )


@shared_task(name="send_reset_password_email_task")
def send_reset_password_email_task(email: str, token: str):
    body = f"""
    <h1>Reset Password Email</h1>
    <p>Your token is: <b>{token}</b></p>
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_email(
        email, "Reset Password [Online Cinema]", body
    )
    )
