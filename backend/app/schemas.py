from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr
    login: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str
    password_confirm: str

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    login: Optional[str] = None
    profile_picture: Optional[str] = None
    password: Optional[str] = None
    password_confirm: Optional[str] = None

    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    @validator('*', pre=True)
    def check_at_least_one_field(cls, v, values, **kwargs):
        if not any(values.values()):
            raise ValueError('at least one field must be provided')
        return v

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    owner_id: int
    periodicity: str
    statuses: Optional[List[str]] = None
    members: Optional[List[int]] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[int] = None
    members: Optional[List[int]] = None

    @validator('*', pre=True)
    def check_at_least_one_field(cls, v, values, **kwargs):
        if not any(values.values()):
            raise ValueError('at least one field must be provided')
        return v

class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    periodicity: str

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_format: Optional[str] = None
    assignee_id: Optional[int] = None
    project_id: int
    status: Optional[str] = None
    sprint_id: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    file_format: Optional[str]
    assignee_id: Optional[int]
    project_id: int
    status: Optional[str]
    sprint_id: Optional[int]

    class Config:
        orm_mode = True

class SprintBase(BaseModel):
    project_id: int
    start_date: datetime

class SprintResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    planned_end_date: datetime
    actual_end_date: Optional[datetime]

    class Config:
        orm_mode = True