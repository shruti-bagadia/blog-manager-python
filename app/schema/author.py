from pydantic import BaseModel, EmailStr, UUID4

class AuthorBase(BaseModel):
    name: str
    email: EmailStr

class AuthorCreate(AuthorBase):
    pass

class AuthorRead(AuthorBase):
    author_uuid: UUID4

    class Config:
        orm_mode = True