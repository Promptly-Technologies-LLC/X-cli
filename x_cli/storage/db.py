from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session, create_engine


def get_engine(db_url: str, *, echo: bool = False) -> Engine:
    return create_engine(db_url, echo=echo)


def init_db(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)


def get_session(engine: Engine) -> Session:
    return Session(engine)
