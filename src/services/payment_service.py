import stripe
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.models.order import OrderStatusEnum
from src.models.payment import PaymentStatusEnum, Payment

from src.core.config import settings
from src.schemas.payment import PaymentCreate
from src.crud import payment as payment_crud
from src.crud import order as order_crud

stripe.api_key = settings.STRIPE_SECRET_KEY

async def initiate_checkout_session(
        order_id: int,
        user_id: int,
        session: AsyncSession,
) -> str:
    order = await order_crud.get_order_by_id(
        order_id=order_id,
        user_id=user_id,
        session=session,
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    if order.status != OrderStatusEnum.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pay for order that is {order.status.value}",
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Order #{order.id}"},
                    "unit_amount": int(order.total_amount * 100)
                },
                "quantity": 1
            }],
            mode="payment",
            payment_intent_data={
                "metadata": {
                    "user_id": str(user_id),
                    "order_id": str(order.id),
                }
            },
            success_url=f"http://127.0.0.1:8000/orders/me/{order_id}",
            cancel_url=f"http://127.0.0.1:8000/orders/me/{order_id}",
        )
        return checkout_session.url


    except stripe.error.StripeError:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Payment provider error."
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error."
        )



async def handle_stripe_webhook(
        request: Request, session: AsyncSession
) -> Payment | None:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe Signature",
        )

    intent = event["data"]["object"]
    status_mapping = {
        "payment_intent.succeeded": PaymentStatusEnum.SUCCESSFUL,
        "payment_intent.canceled": PaymentStatusEnum.CANCELED,
        "payment_intent.payment_failed": PaymentStatusEnum.CANCELED,
    }
    internal_status = status_mapping.get(event["type"])

    if not internal_status:
        return

    metadata = intent.get("metadata", {})
    user_id = metadata.get("user_id")
    order_id = metadata.get("order_id")

    payment_in = PaymentCreate(
        user_id=int(user_id),
        order_id=int(order_id),
        amount=intent["amount"] / 100,
        external_payment_id=intent["id"],
        status=internal_status
    )

    return await payment_crud.create_payment(
        payment_in=payment_in,
        session=session,
    )
