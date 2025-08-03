from fastapi import FastAPI, File, WebSocket, WebSocketDisconnect, BackgroundTasks, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import os

from services.transcription import webm_to_text
from services.inference import analyze_recording, generateStory
from db.database import create_tables


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if Database is Created
main_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(main_dir, 'db', 'database.db')
if os.path.exists(relative_path):
    print("The database file exists.")
else:
    print("The database file does not exist. Creating it now...")
    create_tables()


connected_clients = {}
stories = {}

# Endpoints
@app.post("/eval")
async def eval(file: UploadFile = File(...), inference_id : str = None):
    websocket = connected_clients.get(inference_id)
    webm_bytes = await file.read()
    model_output = await webm_to_text(webm_bytes)
    result = await analyze_recording(stories["current_story"], model_output, websocket, inference_id)

    return result

class StoryRequest(BaseModel):
    prompt: str
    inference_id: str

@app.post("/gen-story")
async def generate_story(request: StoryRequest):
    websocket = connected_clients.get(request.inference_id)
    story = await generateStory(request.prompt, websocket, request.inference_id)
    stories["current_story"] = story
    return {"story" : story}

@app.websocket("/ws/inf-stream/{inference_id}")
async def inf_stream(websocket: WebSocket, inference_id: str):
    print(f"Attempting WebSocket connect: {inference_id}")
    await websocket.accept()
    connected_clients[inference_id] = websocket
    print(f"WebSocket connected: {inference_id}")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {inference_id}")
        connected_clients.pop(inference_id, None)