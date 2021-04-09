import database
from database import init_db
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel
from database import User, Room

init_db()

import uuid

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///")


class UsernameBody(BaseModel):
    username: str


class JoinRoomResponse(BaseModel):
    username: str
    room_id: str


@app.post("/create", response_model=JoinRoomResponse)
def create_room(username):
    room_id = uuid.uuid4().hex
    # user = User(username=username, room_id=room_id, label="label")
    room = Room(id=room_id)
    db.session.add(room)
    # db.session.add(user)
    db.session.commit()
    return {"username": f"{username}"}


@app.get("/join", response_model=JoinRoomResponse)
def join_room(body: UsernameBody):
    return {"room_id": "room_id", "username": f"{body: username}"}


@app.get("/status/{room_id}")
def read_item(room_id):
    return {
        "room_id": f"{room_id}",
        "status": "on_air",
        "players": [
            {"username": "max", "label": "alpaca"},
            {"username": "ann", "label": "dog"},
            {"username": "adam", "label": "bat"},
        ],
    }


@app.post("/start/{room_id}")
def start_room(room_id):
    return {"room_id": f"{room_id}"}
