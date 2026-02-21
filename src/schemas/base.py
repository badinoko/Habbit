from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateResponse(BaseModel):
    id: UUID


class Response(BaseModel):
    message: str


class Stats(BaseModel):
    active_tasks: int
    total_habits: int
    success_rate: int


class InDBBase(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
