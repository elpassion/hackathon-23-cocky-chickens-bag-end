from fastapi import FastAPI

app = FastAPI()


@app.post("/create")
def create_room(username):
    return {"username": f"{username}"}


@app.get("/join")
def read_root(username):
    return {"room_id": "room_id", "username": f"{username}"}


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


@app.post("/start/{room_id")
def start_room(room_id):
    return {"room_id": f"{room_id}"}
