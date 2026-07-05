import logging
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select

from app.database import SessionDep
from app.auth.dependencies import get_current_user
from app.auth.schemas import User
from .schemas import Note, NoteList, NotePublic, NoteCreate, NoteUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notes", tags=["Notes"])


@router.get("", response_model=list[NoteList])
async def get_all_notes(
    current_user: Annotated[User, Depends(get_current_user)], session: SessionDep
):
    notes = session.exec(select(Note).where(Note.user_id == current_user.id)).all()

    logger.debug(f"Fetched all notes for user: {current_user.id}")
    return notes


@router.get("/{note_id}", response_model=NotePublic)
async def get_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    note = session.exec(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    ).one_or_none()
    if not note:
        logger.warning(
            f"Failed attempt to get note {note_id} for user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    logger.info(f"User {current_user.id} retrieved note {note.id}")
    return note


@router.post("", response_model=NotePublic, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    note = Note.model_validate(payload, update={"user_id": current_user.id})
    session.add(note)
    session.commit()
    session.refresh(note)

    logger.info(f"Note {note.id} created for user {current_user.id}")
    return note


@router.patch("/{note_id}", response_model=NotePublic)
async def update_note(
    note_id: int,
    payload: NoteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    note_db = session.exec(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    ).one_or_none()
    if not note_db:
        logger.warning(
            f"Failed attempt to get note {note_id} for user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )
    note_data = {
        **payload.model_dump(exclude_unset=True),
        "updated_at": datetime.now(timezone.utc),
    }
    note_db.sqlmodel_update(note_data)
    session.add(note_db)
    session.commit()
    session.refresh(note_db)

    logger.info(f"Note {note_db.id} updated for user {current_user.id}")
    return note_db


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    note_db = session.exec(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    ).one_or_none()
    if not note_db:
        logger.warning(
            f"Failed attempt to get note {note_id} for user{current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    logger.info(f"Note {note_db.id} deleted for user {current_user.id}")
    session.delete(note_db)
    session.commit()
