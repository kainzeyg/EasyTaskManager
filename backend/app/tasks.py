from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.schemas import TaskBase, TaskResponse
from app.models import Task, Project, User, ProjectStatus, Sprint
from app.security import get_current_active_user
from app.database import get_db
from sqlalchemy.future import select
from sqlalchemy import and_

router = APIRouter()

@router.post("/create", response_model=TaskResponse)
async def create_task(
    task_data: TaskBase,
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Проверяем, что проект существует
    result = await db.execute(
        select(Project).where(and_(Project.id == task_data.project_id, Project.is_deleted == False))
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
    
    # Проверяем исполнителя, если указан
    if task_data.assignee_id:
        result = await db.execute(
            select(ProjectMember).where(
                and_(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id == task_data.assignee_id
                )
            )
        )
        assignee_member = result.scalars().first()
        
        if not assignee_member:
            raise HTTPException(status_code=400, detail="Assignee is not a project member")
    
    # Получаем статусы проекта
    result = await db.execute(
        select(ProjectStatus).where(ProjectStatus.project_id == project.id).order_by(ProjectStatus.order)
    )
    statuses = result.scalars().all()
    
    if not statuses:
        raise HTTPException(status_code=500, detail="Project has no statuses")
    
    # Определяем статус задачи
    status_id = None
    if task_data.status:
        for s in statuses:
            if s.name == task_data.status:
                status_id = s.id
                break
        if not status_id:
            raise HTTPException(status_code=400, detail="Invalid status")
    else:
        status_id = statuses[0].id
    
    # Определяем спринт
    sprint_id = None
    if task_data.sprint_id:
        result = await db.execute(
            select(Sprint).where(
                and_(
                    Sprint.id == task_data.sprint_id,
                    Sprint.project_id == project.id
                )
            )
        )
        sprint = result.scalars().first()
        if not sprint:
            raise HTTPException(status_code=400, detail="Invalid sprint")
        sprint_id = sprint.id
    else:
        # Получаем текущий активный спринт
        result = await db.execute(
            select(Sprint).where(
                and_(
                    Sprint.project_id == project.id,
                    Sprint.actual_end_date == None
                )
            ).order_by(Sprint.start_date.desc())
        )
        sprint = result.scalars().first()
        if sprint:
            sprint_id = sprint.id
    
    # Читаем файл, если он есть
    file_data = None
    if file:
        file_data = await file.read()
    
    # Создаем задачу
    task = Task(
        name=task_data.name,
        description=task_data.description,
        file_data=file_data,
        file_format=task_data.file_format,
        assignee_id=task_data.assignee_id,
        project_id=task_data.project_id,
        status_id=status_id,
        sprint_id=sprint_id
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return task

@router.post("/delete")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем задачу
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.is_deleted == False))
    )
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == task.project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    # Проверяем права (владелец проекта или создатель задачи)
    if project.owner_id != current_user.id and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Помечаем задачу как удаленную
    task.is_deleted = True
    await db.commit()
    
    return {"message": "Task deleted successfully"}

@router.get("/list", response_model=List[TaskResponse])
async def list_tasks(
    project_id: int,
    status: Optional[str] = None,
    sprint_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Проверяем, что проект существует
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
    
    # Формируем запрос для получения задач
    query = select(Task).where(
        and_(
            Task.project_id == project_id,
            Task.is_deleted == False
        )
    )
    
    # Добавляем фильтр по статусу, если он указан
    if status:
        result = await db.execute(
            select(ProjectStatus).where(
                and_(
                    ProjectStatus.project_id == project_id,
                    ProjectStatus.name == status
                )
            )
        )
        status_obj = result.scalars().first()
        
        if not status_obj:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        query = query.where(Task.status_id == status_obj.id)
    
    # Добавляем фильтр по спринту, если он указан
    if sprint_id:
        result = await db.execute(
            select(Sprint).where(
                and_(
                    Sprint.id == sprint_id,
                    Sprint.project_id == project_id
                )
            )
        )
        sprint = result.scalars().first()
        
        if not sprint:
            raise HTTPException(status_code=400, detail="Invalid sprint")
        
        query = query.where(Task.sprint_id == sprint_id)
    
    # Выполняем запрос
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    return tasks

@router.get("/change", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Получаем задачу
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.is_deleted == False))
    )
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Получаем проект
    result = await db.execute(
        select(Project).where(and_(Project.id == task.project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
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
    
    return task