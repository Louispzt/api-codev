from typing import Optional
from pydantic import BaseModel


class BookmarkBase(BaseModel):
    title: str


class BookmarkCreate(BookmarkBase):
    description: Optional[str] = None


class Bookmark(BookmarkCreate):
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str


class UserInDb(UserBase):
    hashed_password: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    bookmarks: list[Bookmark] = []


class User(UserBase):
    id: int
    is_active: bool
    bookmarks: list[Bookmark] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
