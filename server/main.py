import json

from fastapi import FastAPI, File, Form, UploadFile, WebSocket
from fastapi.responses import StreamingResponse
from utils import types
from db_services.MySQLHandler import MySQLHandler
from utils.profile_handler import set_profile_to_env
from apis import profile, note, document, question

app = FastAPI()


@app.on_event('startup')
def startup():
    set_profile_to_env()
    MySQLHandler().connect_to_mysql()


# Profile APIs
@app.get("/profile")
def get_profile():
    return profile._get_profile()


@app.put("/profile")
def set_profile(data: types.Profile):
    return profile._set_profile(data)


# Note APIs
@app.get("/note/notes")
def get_notes():
    return note._get_notes()


@app.get("/note/files/{id}")
def get_files_by_noteId(id: int):
    return note._get_files_by_noteId(id)


@app.get("/note/{id}")
def get_note(id: int):
    return note._get_note(id)


@app.post("/note")
async def add_note(
    language: str = Form(),
    noteName: str = Form(),
    files: list[UploadFile] = File(default=None),
    notionId: str = Form(default=None),
):
    res = await note._add_note(language, noteName, files, notionId)
    return res


@app.delete("/note/{id}")
def delete_note(id: int):
    return note._delete_note(id)


@app.patch("/note/icon")
def update_note_icon(data: types.Icon):
    return note._update_note_icon(data)


# File APIs


@app.delete("/file")
def delete_file(id: int, file_name: str):
    return document._delete_file(id, file_name)


@app.websocket("/ws/file/uploading")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()
        uploading_files = {"data": document._get_uploading_files()}
        await websocket.send_json(uploading_files)


# Question APIs
@app.get("/questions/note/{id}")
def get_questions_by_note_id(id: int):
    return question._get_questions_by_note_id(id)


@app.post("/question/examine")
async def examine_question(data: types.AnswerQuestion):
    return StreamingResponse(
        question._examine_question(data),
        media_type="text/event-stream"
    )


@app.get("/question/lastAnswer/{id}")
def get_last_answer(id: int):
    return question._get_last_answer(id)


@app.get("/question/document/{id}")
def get_document(id: int):
    return question._get_document(id)


@app.get("/question/random")
def get_random_question():
    return question._get_random_question()


@app.on_event("shutdown")
def shutdown_event():
    MySQLHandler().disconnect_from_mysql()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=51717)
