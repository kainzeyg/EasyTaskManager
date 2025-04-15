from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas import UserResponse, UserUpdate
from app.models import User
from app.security import get_current_active_user
from app.database import get_db
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

@router.get("/list", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(User).where(User.is_deleted == False))
    users = result.scalars().all()
    return users

@router.post("/change")
async def change_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем пользователя для изменения
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, что текущий пользователь имеет права на изменение
    if current_user.id != user.id and current_user.id != 1:  # Предполагаем, что id=1 - это admin
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Обновляем данные
    if user_data.username:
        user.username = user_data.username
    if user_data.login:
        # Проверяем уникальность логина
        if user_data.login != user.login:
            result = await db.execute(select(User).where(User.login == user_data.login))
            if result.scalars().first():
                raise HTTPException(status_code=400, detail="Login already taken")
        user.login = user_data.login
    if user_data.profile_picture:
        user.profile_picture = user_data.profile_picture
    if user_data.password:
        from app.security import get_password_hash
        user.password_hash = get_password_hash(user_data.password)
    
    await db.commit()
    
    # Если пользователь менял свои данные - разлогиниваем его
    if current_user.id == user.id:
        from app.security import oauth2_scheme
        # Здесь нужно реализовать удаление токена из Redis
        # Это зависит от вашей реализации хранения сессий
        
    return {"message": "User updated successfully"}

@router.post("/delete")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем пользователя для удаления
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем права
    if current_user.id != user.id and current_user.id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # "Удаляем" пользователя
    user.is_deleted = True
    user.username = "DELETED"
    user.login = None
    user.password_hash = None
    user.profile_picture = "/static/default_avatar.png"
    
    await db.commit()
    
    return {"message": "User deleted successfully"}

@router.get("/open", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user