from app.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from app.schemas import SprintBase, SprintResponse
from app.models import Sprint, Project, SprintPeriodicity
from app.security import get_current_active_user
from app.database import get_db
from sqlalchemy.future import select
from sqlalchemy import and_

router = APIRouter()

def calculate_end_date(start_date: datetime, periodicity_name: str) -> datetime:
    if "недел" in periodicity_name:
        weeks = int(periodicity_name.split()[0])
        return start_date + timedelta(weeks=weeks)
    elif "месяц" in periodicity_name:
        months = int(periodicity_name.split()[0])
        return start_date + relativedelta(months=months)
    elif "квартал" in periodicity_name:
        quarters = int(periodicity_name.split()[0])
        return start_date + relativedelta(months=quarters*3)
    elif "год" in periodicity_name:
        years = int(periodicity_name.split()[0])
        return start_date + relativedelta(years=years)
    else:
        return start_date + timedelta(days=7)  # По умолчанию 1 неделя

@router.post("/create", response_model=SprintResponse)
async def create_sprint(
    sprint_data: SprintBase,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Проверяем, что проект существует
    result = await db.execute(
        select(Project).where(and_(Project.id == sprint_data.project_id, Project.is_deleted == False))
    )
    project = result.scalars().first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Проверяем, что пользователь является владельцем проекта
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Получаем периодичность проекта
    result = await db.execute(
        select(SprintPeriodicity).where(SprintPeriodicity.id == project.periodicity_id)
    )
    periodicity = result.scalars().first()
    
    # Рассчитываем дату окончания
    planned_end_date = calculate_end_date(sprint_data.start_date, periodicity.name)
    
    # Получаем номер спринта
    result = await db.execute(
        select(Sprint).where(Sprint.project_id == project.id).order_by(Sprint.start_date.desc())
    )
    last_sprint = result.scalars().first()
    sprint_number = 1 if not last_sprint else int(last_sprint.name.split()[1]) + 1
    
    # Создаем спринт
    sprint = Sprint(
        project_id=project.id,
        name=f"Спринт {sprint_number}",
        start_date=sprint_data.start_date,
        planned_end_date=planned_end_date
    )
    
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    
    return sprint

@router.post("/endSprint")
async def end_sprint(
    project_id: int,
    sprint_id: int,
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
    
    # Проверяем, что пользователь является владельцем проекта
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Получаем спринт
    result = await db.execute(
        select(Sprint).where(
            and_(
                Sprint.id == sprint_id,
                Sprint.project_id == project_id,
                Sprint.actual_end_date == None
            )
        )
    )
    sprint = result.scalars().first()
    
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found or already ended")
    
    # Завершаем спринт
    sprint.actual_end_date = datetime.utcnow()
    await db.commit()
    
    # Создаем новый спринт
    new_sprint_data = SprintBase(
        project_id=project_id,
        start_date=sprint.planned_end_date
    )
    
    return await create_sprint(new_sprint_data, db, current_user)

@router.get("/list", response_model=List[SprintResponse])
async def list_sprints(
    project_id: int,
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
    
    # Получаем спринты проекта
    result = await db.execute(
        select(Sprint).where(Sprint.project_id == project_id).order_by(Sprint.start_date)
    )
    sprints = result.scalars().all()
    
    return sprints