import os

from sqlalchemy import (
    Column,
    Integer,
    String,
    MetaData,
    Table,
    JSON,
    create_engine, ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType

engine = create_engine("sqlite:///_database/database.db")
engine.connect()

Base = declarative_base()
metadata = MetaData()


class Room(Base):
    __tablename__ = "rooms"

    id = Column(UUIDType(binary=False), primary_key=True)
    users = relationship("User")


rooms = Table("rooms", metadata, Column("id", UUIDType(), primary_key=True))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(UUIDType, ForeignKey('room.id'))
    room  = relationship("Room", back_populates="users")
    username = Column(String(100, collation="utf8mb4_unicode_ci"))
    label = Column(String(100, collation="utf8mb4_unicode_ci"))


users = Table(
    "users",
    metadata,
    Column("id", Integer(), primary_key=True, autoincrement=True),
    Column("username", String(100, collation="utf8mb4_unicode_ci"), nullable=False),
    Column("label", String(100, collation="utf8mb4_unicode_ci"), nullable=False),
)
