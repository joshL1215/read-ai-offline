from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from services.transcription import webm_to_text
from services.inference import analyze_recording
from db.database import create_tables
import os

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

@app.post("/eval")
async def eval(file: UploadFile = File(...)):
    webm_bytes = await file.read()
    model_output = await webm_to_text(webm_bytes)
    result = await analyze_recording(model_output)

    return result

# Check if Database is Created
main_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(main_dir, 'db', 'database.db')
if os.path.exists(relative_path):
    print("The database file exists.")
else:
    print("The database file does not exist.")
    create_tables()