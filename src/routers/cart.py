from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.deps import get_current_active_user
from src.models import User
from src.schemas.cart import CartResponse

from src.crud import cart as cart_crud
from src.utils.pagination import paginate

router = APIRouter(prefix="/cart")


@router.get("/me", response_model=CartResponse)
async def get_cart(
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    cart_items, count = cart_crud.get_cart_items(
        user_id=current_user.id,
        page=page,
        size=size,
        session=session
    )

    return paginate(
        items=cart_items,
        count=count,
        page=page,
        size=size,
        path="/cart/me/"
    )
