from app.schemas import UserResponse
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, timedelta
from app.schemas import (
    ProjectBase,
    ProjectResponse,
    ProjectUpdate,
    TaskResponse
)
from app.models import (
    Project,
    User,
    ProjectMember,
    ProjectStatus,
    SprintPeriodicity
)
from app.security import get_current_active_user
from app.database import get_db
from sqlalchemy.future import select
from sqlalchemy import and_

router = APIRouter()

DEFAULT_STATUSES = ["Новая", "В работе", "Тестирование", "Готова к релизу", "Выполнена", "Отменена"]

@router.post("/create", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Проверяем, что владелец существует
    result = await db.execute(select(User).where(User.id == project_data.owner_id))
    owner = result.scalars().first()
    if not owner or owner.is_deleted:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    # Проверяем периодичность
    result = await db.execute(
        select(SprintPeriodicity).where(SprintPeriodicity.name == project_data.periodicity)
    )
    periodicity = result.scalars().first()
    if not periodicity:
        raise HTTPException(status_code=400, detail="Invalid periodicity")
    
    # Создаем проект
    project = Project(
        name=project_data.name,
        owner_id=project_data.owner_id,
        periodicity_id=periodicity.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Добавляем статусы
    statuses = project_data.statuses if project_data.statuses else DEFAULT_STATUSES
    for i, status_name in enumerate(statuses):
        status = ProjectStatus(
            project_id=project.id,
            name=status_name,
            order=i
        )
        db.add(status)
    
    # Добавляем участников
    members = project_data.members if project_data.members else []
    if project_data.owner_id not in members:
        members.append(project_data.owner_id)
    
    for member_id in members:
        # Проверяем, что пользователь существует
        result = await db.execute(select(User).where(User.id == member_id))
        member = result.scalars().first()
        if not member or member.is_deleted:
            continue
        
        project_member = ProjectMember(
            project_id=project.id,
            user_id=member_id
        )
        db.add(project_member)
    
    await db.commit()
    
    return project

@router.post("/delete")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проект
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем права (только владелец может удалить проект)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Помечаем проект как удаленный
    project.is_deleted = True
    await db.commit()
    
    return {"message": "Project deleted successfully"}

@router.get("/open", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем, что пользователь является участником проекта
    result = await db.execute(
        select(ProjectMember).where(
            and_(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == current_user.id
            )
        )
    )
    member = result.scalars().first()
    
    if not member and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a project member")
    
    return project

@router.post("/change")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем права (только владелец может изменять проект)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Обновляем данные
    if project_data.name:
        project.name = project_data.name
    if project_data.owner_id:
        # Проверяем, что новый владелец существует
        result = await db.execute(select(User).where(User.id == project_data.owner_id))
        new_owner = result.scalars().first()
        if not new_owner or new_owner.is_deleted:
            raise HTTPException(status_code=404, detail="New owner not found")
        project.owner_id = project_data.owner_id
    
    # Обновляем участников, если они указаны
    if project_data.members is not None:
        # Удаляем старых участников (кроме владельца)
        await db.execute(
            delete(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id != project.owner_id
                )
            )
        )
        
        # Добавляем новых участников (включая владельца, если он не в списке)
        members = project_data.members
        if project.owner_id not in members:
            members.append(project.owner_id)
        
        for member_id in members:
            # Проверяем, что пользователь существует
            result = await db.execute(select(User).where(User.id == member_id))
            member = result.scalars().first()
            if not member or member.is_deleted:
                continue
            
            project_member = ProjectMember(
                project_id=project.id,
                user_id=member_id
            )
            db.add(project_member)
    
    await db.commit()
    
    return {"message": "Project updated successfully"}

@router.get("/projectOwner", response_model=UserResponse)
async def get_project_owner(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем, что пользователь является участником проекта
    result = await db.execute(
        select(ProjectMember).where(
            and_(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == current_user.id
            )
        )
    )
    member = result.scalars().first()
    
    if not member and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a project member")
    
    # Получаем владельца
    result = await db.execute(select(User).where(User.id == project.owner_id))
    owner = result.scalars().first()
    
    return owner

@router.get("/projectStatuses", response_model=List[str])
async def get_project_statuses(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем, что пользователь является участником проекта
    result = await db.execute(
        select(ProjectMember).where(
            and_(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == current_user.id
            )
        )
    )
    member = result.scalars().first()
    
    if not member and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a project member")
    
    # Получаем статусы проекта
    result = await db.execute(
        select(ProjectStatus).where(ProjectStatus.project_id == project.id).order_by(ProjectStatus.order)
    )
    statuses = [status.name for status in result.scalars().all()]
    
    return statuses

@router.get("/projectUsers", response_model=List[UserResponse])
async def get_project_users(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем, что пользователь является участником проекта
    result = await db.execute(
        select(ProjectMember).where(
            and_(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == current_user.id
            )
        )
    )
    member = result.scalars().first()
    
    if not member and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not a project member")
    
    # Получаем участников проекта
    result = await db.execute(
        select(User).join(ProjectMember).where(ProjectMember.project_id == project.id)
    )
    users = result.scalars().all()
    
    return users

@router.get("/list", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем проекты, где пользователь является участником или владельцем
    result = await db.execute(
        select(Project).join(ProjectMember).where(
            and_(
                Project.is_deleted == False,
                ProjectMember.user_id == current_user.id
            )
        ).union(
            select(Project).where(
                and_(
                    Project.is_deleted == False,
                    Project.owner_id == current_user.id
                )
            )
        )
    )
    projects = result.scalars().all()
    
    return projects