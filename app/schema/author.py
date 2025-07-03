from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional

class AuthorBase(BaseModel):
    name: str
    email: EmailStr

class AuthorCreate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    author_uuid: UUID4

    class Config:
        orm_mode = True

class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
