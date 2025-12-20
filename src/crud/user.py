from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from src.core.security import hash_password
from src.models.user import User, UserGroup, UserGroupEnum, UserProfile
from src.schemas.user import UserCreate, UserProfileUpdate, UserUpdateAdmin


async def get_user_by_email(
        email: str, session: AsyncSession
) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
    result = await session.execute(select(User)
                                   .options(
        selectinload(User.group),
        selectinload(User.profile)
    )
                                   .where(User.id == user_id)
                                   )
    return result.scalar_one_or_none()


async def create_user(user_in: UserCreate, session: AsyncSession) -> User:
    if await get_user_by_email(user_in.email, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    result = await session.execute(select(UserGroup)
                                   .where(UserGroup.name == "USER"))
    group = result.scalar_one_or_none()
    if not group:
        group = UserGroup(name=UserGroupEnum.USER)
        session.add(group)
        await session.flush()

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        group_id=group.id,
        profile=UserProfile(
            first_name="",
            last_name="",
        )
    )

    session.add(user)
    await session.commit()

    return await get_user_by_id(user_id=user.id, session=session)


async def update_password(
        user_id: int,
        new_password: str,
        session: AsyncSession
) -> None:
    await session.execute(update(User)
                          .where(User.id == user_id)
                          .values(hashed_password=new_password)
                          )
    await session.commit()


async def get_profile_by_user_id(
        user_id: int, session: AsyncSession
) -> UserProfile | None:
    result = await session.execute(select(UserProfile)
                                   .where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def update_profile(
        user_id: int, profile_in: UserProfileUpdate, session: AsyncSession
) -> UserProfile | None:
    update_data = profile_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_profile_by_user_id(user_id, session)

    await session.execute(update(UserProfile)
                          .where(UserProfile.user_id == user_id)
                          .values(**update_data)
                          .execution_options(synchronize_session="fetch")
                          )
    await session.commit()

    return await get_profile_by_user_id(user_id, session)


async def update_user_admin(
        user_id: int, user_in: UserUpdateAdmin, session: AsyncSession
) -> User | None:
    update_data = user_in.model_dump(exclude_unset=True)
    if not update_data:
        return await get_user_by_id(user_id, session)

    await session.execute(update(User)
                          .where(User.id == user_id)
                          .values(**update_data)
                          .execution_options(synchronize_session="fetch")
                          )

    await session.commit()
    return await get_user_by_id(user_id, session)
