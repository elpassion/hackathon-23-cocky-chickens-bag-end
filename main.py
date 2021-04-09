from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.post("/create")
def create_room(username):
    pass


@app.get("/join")
def read_root(username):
    pass


@app.get("/status/{room_id}")
def read_item(room_id):
    pass


@app.post("/start/{room_id")
def start_room(room_id):
    pass