from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy_utils import UUIDType

engine = create_engine("sqlite:///_database/database.db")

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Model = declarative_base(name="Model")
Model.query = db_session.query_property()


def init_db():
    Model.metadata.create_all(bind=engine)


class Room(Model):
    __tablename__ = "rooms"
    id = Column(UUIDType(binary=False), primary_key=True)
    users = relationship("User")


class User(Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(UUIDType, ForeignKey(Room.id))
    room = relationship(Room, back_populates="users")
    username = Column(String(100))
    label = Column(String(100))
