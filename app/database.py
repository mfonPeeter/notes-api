from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine
from app.config import settings

# echo=True logs all SQL queries to terminal — disable in production
engine = create_engine(settings.database_url, echo=settings.debug)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
