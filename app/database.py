import os

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy_utils import UUIDType

POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_HOST = "postgres"
DB_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_engine(DB_URL)

db_session = scoped_session(sessionmaker(autocommit=True, autoflush=True, bind=engine))
Model = declarative_base(name="Model")
Model.query = db_session.query_property()


def init_db():
    Model.metadata.create_all(bind=engine)


class Room(Model):
    __tablename__ = "rooms"

    id = Column(UUIDType(binary=False), primary_key=True)
    status = Column(String(10), default="open")
    users = relationship("User")
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )
    name = Column(String(100))
    category = Column(String(20))

    @property
    def nice_id(self):
        return self.id.hex


class User(Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(UUIDType, ForeignKey(Room.id))
    room = relationship(Room, back_populates="users")
    username = Column(String(100))
    label = Column(String(100))
    created = Column(DateTime(timezone=True), server_default=func.now())
    updated = Column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )
