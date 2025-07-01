from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional
from .author import AuthorRead

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    author_uuid: UUID4

class PostRead(PostBase):
    post_uuid: UUID4
    created_at: datetime
    author: AuthorRead

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None