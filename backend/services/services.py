import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from faster_whisper import WhisperModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect 
from fastapi.middleware.cors import CORSMiddleware
import ollama
import io
import time
import uvicorn

# Global Variables
silenceThrehold = 5 # Flag if silent for more than X seconds
currentText = [] # Stores the current story as an array

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

model = WhisperModel("small", device="cpu", compute_type="float32")

@app.get("/ping")
async def ping():
    return {"message": "pong"}

executor = ThreadPoolExecutor()

async def transcribe_async(audio_chunk):
    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(executor, model.transcribe, audio_chunk, "en")

@app.websocket("/ws/transcribe")
async def transcribe_audio(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    try:
        text = ""
        while True:
            data = await websocket.receive_bytes()
            if not data:
                continue

            audio_chunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

            segments, _ = await transcribe_async(audio_chunk)
            text += "".join(segment.text for segment in segments)
            print(text)
            await websocket.send_text(text)

    except WebSocketDisconnect:
        print("WebSocket disconnected")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
