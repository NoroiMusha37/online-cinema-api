from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.core.database import get_db
from src.core.deps import get_current_active_user, get_current_admin
from src.models import User
from src.models.payment import PaymentStatusEnum
from src.schemas.payment import PaymentResponse, PaymentDetail

from src.crud import payment as payment_crud
from src.services import payment_service
from src.utils.pagination import paginate
from src.tasks.email_tasks import send_payment_notification_email_task

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/me", response_model=PaymentResponse)
async def get_user_payments(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    payments, count = await payment_crud.get_user_payments(
        user_id=current_user.id,
        page=page,
        size=size,
        session=session
    )

    return paginate(
        items=payments,
        count=count,
        page=page,
        size=size,
        path="/payments/me/"
    )


@router.get("/me/{payment_id}", response_model=PaymentDetail)
async def get_payment_detail(
        payment_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    payment = await payment_crud.get_payment_by_id(
        payment_id=payment_id,
        session=session
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found."
        )

    return payment


@router.get("/", response_model=PaymentResponse)
async def get_all_payments(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        user_id: int | None = Query(None, ge=1),
        start_date: int | None = Query(None, ge=1888),
        end_date: int | None = Query(None, ge=1888),
        status: PaymentStatusEnum | None = Query(None),
        current_admin: User = Depends(get_current_admin),
        session: AsyncSession = Depends(get_db)
):
    payments, count = await payment_crud.get_all_payments(
        page=page,
        size=size,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        session=session
    )

    return paginate(
        items=payments,
        count=count,
        page=page,
        size=size,
        path="/payments/"
    )


@router.post("/me/{payment_id}/refund", response_model=PaymentDetail)
async def refund_payment(
        payment_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    payment =  await payment_crud.process_refund(
        payment_id=payment_id,
        user_id=current_user.id,
        session=session
    )

    send_payment_notification_email_task.delay(
        email=current_user.email,
        order_id=payment.order_id,
        status=payment.status.value,
    )
    return payment


@router.post("/checkout")
async def create_checkout_session(
        order_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db),
):
    checkout_url = await payment_service.initiate_checkout_session(
        order_id=order_id,
        user_id=current_user.id,
        session=session
    )

    return {"checkout_url": checkout_url}


@router.post("/webhook")
async def stripe_webhook(
        request: Request,
        session: AsyncSession = Depends(get_db)
):
    payment = await payment_service.handle_stripe_webhook(
        request=request, session=session
    )

    if not payment:
        return {"status": "ignored"}

    send_payment_notification_email_task.delay(
        email=payment.user.email,
        order_id=payment.order_id,
        status=payment.status.value,
    )

    return {"status": "success", "payment_id": payment.id}
