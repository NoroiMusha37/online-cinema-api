from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.database import get_db
from src.core.deps import get_current_active_user
from src.models import User
from src.schemas.cart import CartResponse, CartItemResponse, CartItemCreate

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


@router.post("/items", response_model=CartItemResponse | dict)
async def add_to_cart(
        cart_item_in: CartItemCreate,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    new_cart_item = await cart_crud.create_cart_item(
        cart_item_in=cart_item_in,
        user_id=current_user.id,
        session=session
    )
    if not new_cart_item:
        return {"message": "This movie is already in the cart "
                           "or you have purchased it"}

    return new_cart_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
        item_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    await cart_crud.delete_cart_item(
        user_id=current_user.id,
        cart_item_id=item_id,
        session=session
    )


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db)
):
    await cart_crud.clear_cart(
        user_id=current_user.id,
        session=session
    )
