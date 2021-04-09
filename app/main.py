import random
import uuid

from fastapi import FastAPI, HTTPException, status
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel

from database import DB_URL, Room, User, init_db

init_db()


app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=DB_URL)


class UsernameBody(BaseModel):
    username: str


def get_items(filename):
    labels = set()
    with open(f"labels/{filename}", "r") as file:
        for line in file:
            labels.add(line[:-1])
    return list(labels)


def create_user(room_id, username, filename, new_room=False):
    if not (new_room or Room.query.get(room_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such room. Ciao."
        )
    unique_label = random.choice(get_items(filename))
    while not check_label_unique(room_id, unique_label):
        continue
    user = User(username=username, room_id=room_id, label=unique_label)
    db.session.add(user)
    db.session.commit()


def check_label_unique(room_id, label):
    users = User.query.filter_by(room_id=room_id).all()
    labels = [user.label for user in users]
    return label not in labels


class JoinRoomResponse(BaseModel):
    username: str
    room_id: str


@app.post("/create", response_model=JoinRoomResponse)
def create_room(body: UsernameBody):
    room_id = uuid.uuid4().hex
    room = Room(id=room_id)
    db.session.add(room)
    create_user(room_id, body.username, filename="animals.txt", new_room=True)

    return {"username": body.username, "room_id": room_id}


@app.post("/join/{room_id}", response_model=JoinRoomResponse)
def join_room(room_id, body: UsernameBody):
    create_user(room_id, body.username, filename="animals.txt")
    return {"room_id": room_id, "username": body.username}


@app.get("/status/{room_id}")
def room_status(room_id):
    room = Room.query.get(room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such room. Ciao."
        )
    users = room.users
    return {
        "room_id": room.id,
        "status": room.status,
        "players": [{"username": user.username, "label": user.label} for user in users],
    }


@app.post("/start/{room_id}")
def start_room(room_id):
    room = Room.query.get(room_id)
    if room.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start not-open room.",
        )
    room.status = "started"
    db.session.commit()
    return {"room_id": f"{room_id}"}
