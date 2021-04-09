from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi_sqlalchemy import db
from database import Room, User
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url="sqlite:///")


class UsernameBody(BaseModel):
    username: str


@app.post("/create")
def create_room(username):
    return {"username": f"{username}"}


class JoinRoomResponse(BaseModel):
    username: str
    room_id: str


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
