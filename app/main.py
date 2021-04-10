from __future__ import annotations

import random
import re
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List

import pytz
from fastapi import FastAPI, HTTPException, status
from fastapi_sqlalchemy import DBSessionMiddleware, db
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from database import DB_URL, Room, User, init_db
from name_generator import generate_room_name

DETAIL_404 = "No such room. Ciao."

init_db()

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=DB_URL)

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost",
    "https://hackathon-23-cocky-chickens.vercel.app",
    "http://hackathon-23-cocky-chickens.vercel.app",
    "*",  # YOLO
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RoomModel(BaseModel):
    room_id: str
    room_name: str
    room_category: str


class Status(str, Enum):
    open = "open"
    on_air = "on_air"
    closed = "closed"


class Categories(str, Enum):
    animals = "animals"
    people = "people"


class UserWithLabel(BaseModel):
    username: str
    label: str


class RoomStatusResponse(BaseModel):
    room_id: str
    status: Status
    players: List[UserWithLabel]


class CreateRoomBody(BaseModel):
    username: str
    room_category: Categories


class UsernameBody(BaseModel):
    username: str


class JoinRoomResponse(BaseModel):
    username: str
    room_id: str


def verify_room_id(room_id: str):
    if not re.match(r"^[a-f0-9]{32}$", room_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=DETAIL_404)


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


@app.post("/create", response_model=JoinRoomResponse)
def create_room(body: CreateRoomBody):
    room_id = uuid.uuid4().hex
    room = Room(id=room_id, name=generate_room_name(), category=body.room_category)
    db.session.add(room)
    db.session.commit()
    create_user(room_id, body.username, filename="animals.txt", new_room=True)

    return {"username": body.username, "room_id": room_id}


@app.post(
    "/join/{room_id}",
    response_model=JoinRoomResponse,
    responses={404: {"detail": DETAIL_404}},
)
def join_room(room_id, body: UsernameBody):
    verify_room_id(room_id)
    create_user(room_id, body.username, filename="animals.txt")
    return {"room_id": room_id, "username": body.username}


@app.get(
    "/status/{room_id}",
    response_model=RoomStatusResponse,
    responses={404: {"detail": DETAIL_404}},
)
def room_status(room_id):
    verify_room_id(room_id)
    room = Room.query.get(room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=DETAIL_404)
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    room_age = now - room.updated
    if room_age > timedelta(minutes=60):
        room.status = Status.closed
        db.session.add(room)
        db.session.commit()
    users = room.users if room.status != Status.closed else []
    return {
        "room_id": room_id,
        "status": room.status,
        "players": [{"username": user.username, "label": user.label} for user in users],
    }


@app.post(
    "/start/{room_id}",
    response_model=RoomModel,
    responses={
        404: {"detail": DETAIL_404},
        400: {"detail": "Cannot start not-open room."},
    },
)
def start_room(room_id):
    verify_room_id(room_id)
    room = Room.query.get(room_id)
    if room.status != Status.open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start not-open room.",
        )
    room.status = Status.on_air
    db.session.add(room)
    db.session.commit()
    return {"room_id": f"{room_id}"}


class RoomsResponse(BaseModel):
    rooms: List[RoomModel]


@app.get("/rooms", response_model=RoomsResponse)
def list_rooms():
    rooms = Room.query.filter_by(status=Status.open).all()
    return {
        "rooms": [
            RoomModel(
                room_id=str(room.id),
                room_name=room.room_name,
                room_category=room.room_category,
            )
            for room in rooms
        ]
    }
