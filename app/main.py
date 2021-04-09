import database
import random
from database import init_db
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel
from database import User, Room

init_db()

import uuid

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///_database/database.db")


class UsernameBody(BaseModel):
    username: str


def get_items(filename):
    labels = set()
    with open(f"labels/{filename}","r" ) as file:
        for line in file:
            labels.add(line[:-1])
    return list(labels)


def create_user(room_id, username, filename):
    unique_label = random.choice(get_items(filename))
    while not check_label_unique(room_id, unique_label):
        continue
    user = User(username=username, room_id=room_id, label=unique_label)
    db.session.add(user)
    db.session.commit()


def check_label_unique(room_id, label):
    users = User.query.filter_by(room_id=room_id).all()
    labels = []
    for user in users:
        labels.append(user.label)
    return label not in labels


class JoinRoomResponse(BaseModel):
    username: str
    room_id: str


@app.post("/create", response_model=JoinRoomResponse)
def create_room(username):
    room_id = uuid.uuid4().hex
    create_user(room_id, username, filename="animals.txt")
    room = Room(id=room_id)
    db.session.add(room)

    return {"username": f"{username}", "room_id": f"{room_id}"}


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
