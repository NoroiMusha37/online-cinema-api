from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.deps import get_current_admin
from src.models.user import User
from src.schemas.user import UserUpdateAdmin, UserRead
from src.crud import user as user_crud

router = APIRouter(prefix="/admin")

@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user(
        user_id: int,
        user_in: UserUpdateAdmin,
        session: AsyncSession = Depends(get_db),
        current_admin: User = Depends(get_current_admin)
):
    return await user_crud.update_user_admin(
        user_id=user_id,
        user_in=user_in,
        session=session,
    )
