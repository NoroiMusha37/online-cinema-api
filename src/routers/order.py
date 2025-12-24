from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_active_user, get_current_admin
from src.models import User
from src.models.order import OrderStatusEnum
from src.schemas.order import OrderResponse, OrderDetail, OrderUpdate

from src.crud import order as order_crud
from src.utils.pagination import paginate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/me", response_model=OrderResponse)
async def get_user_orders(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    orders, count = await order_crud.get_user_orders(
        user_id=current_user.id,
        page=page,
        size=size,
        session=session
    )

    return paginate(
        items=orders,
        count=count,
        page=page,
        size=size,
        path="/orders/me/"
    )


@router.get("/me/{order_id}", response_model=OrderDetail)
async def get_order_detail(
        order_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    order = await order_crud.get_order_by_id(
        order_id=order_id,
        user_id=current_user.id,
        session=session
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )

    return order


@router.get("/", response_model=OrderResponse)
async def get_all_orders(
        user_id: int | None = Query(None, ge=1),
        start_date: int | None = Query(None, ge=1888),
        end_date: int | None = Query(None, ge=1888),
        status: OrderStatusEnum | None = Query(None),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        current_admin: User = Depends(get_current_admin),
        session: AsyncSession = Depends(get_db)
):
    orders, count = await order_crud.get_all_orders(
        user_id=user_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        size=size,
        session=session
    )

    return paginate(
        items=orders,
        count=count,
        page=page,
        size=size,
        path="/orders/"
    )


@router.post("/", response_model=OrderDetail)
async def create_order(
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    return await order_crud.checkout_cart(
        user_id=current_user.id,
        session=session
    )


@router.patch("/me/{order_id}/cancel", response_model=OrderDetail)
async def cancel_order(
        order_id: int,
        order_in: OrderUpdate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    return await order_crud.update_order(
        order_id=order_id,
        order_in=order_in,
        session=session,
        user_id=current_user.id,
    )


@router.patch("/{order_id}", response_model=OrderDetail)
async def update_order(
        order_id: int,
        order_in: OrderUpdate,
        current_admin: User = Depends(get_current_admin),
        session: AsyncSession = Depends(get_db)
):
    return await order_crud.update_order(
        order_id=order_id,
        order_in=order_in,
        session=session,
    )
