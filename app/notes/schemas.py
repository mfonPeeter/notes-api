from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class NoteBase(SQLModel):
    title: str = Field(min_length=1, index=True)
    content: str = Field(min_length=1)


class Note(NoteBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotePublic(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime


class NoteList(SQLModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


class NoteCreate(NoteBase):
    pass


class NoteUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1)
    content: str | None = Field(default=None, min_length=1)
